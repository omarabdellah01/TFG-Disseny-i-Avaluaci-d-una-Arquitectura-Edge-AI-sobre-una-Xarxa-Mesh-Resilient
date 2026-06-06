import json
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ==========================================
# CONFIGURATION
# ==========================================
ARCHIVO_JSON = "datos_prueba.json"

IP_MESH = "192.168.10.1"    # Jetson 1 (Mesh) - Red
IP_DIRECTO = "192.168.10.2" # Jetson 1 (Direct) - Blue

# Physical milestones for vertical lines INSIDE the graph
HITOS = [
    # PHASE 1
    ("20:13:30", "0m (Origin)"),
    ("20:14:00", "8m (Door A)"),
    ("20:14:10", "16m (Corridor)"),
    ("20:14:25", "24m (Door B)"),
    ("20:14:50", "42m (Reception)"),
    ("20:15:00", "50m (End)"),
    ("20:15:25", "24m (Return)"),
    ("20:15:47", "0m (Origin)"),
    # PHASE 2
    ("20:16:50", "0m (Origin)"),
    ("20:17:00", "8m (Door A)"),
    ("20:17:15", "16m (Corridor)"),
    ("20:17:30", "24m (Door B)"),
    ("20:17:50", "42m (Reception)"),
    ("20:18:00", "50m (End)"),
    ("20:18:30", "24m (Return)"),
    ("20:19:00", "0m (Origin)")
]

# ==========================================
# DATA EXTRACTION
# ==========================================
t_mesh, y_mesh = [], []
transitions_mesh = [] 
t_dir, y_dir = [], []

regex_ping = re.compile(r"=\s*[\d\.]+/(?P<avg>[\d\.]+)/")
regex_hops = re.compile(r'\n\s*(\d+):')

try:
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        
    prev_hop_count = None

    for entrada in datos:
        t_str = entrada.get("timestamp", "")
        try:
            t = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
        except: continue
                
        if t.hour == 20 and 13 <= t.minute <= 19:
            destinos = entrada.get("destinos", {})
            
            # --- PROCESS MESH (.1) ---
            block_mesh = destinos.get(IP_MESH, {})
            val_mesh = block_mesh.get("ping_80bytes", "")
            val_hops = block_mesh.get("batman_hops", "")
            
            hop_count = 1 
            if val_hops:
                lista_saltos = regex_hops.findall(val_hops)
                if lista_saltos:
                    hop_count = max(int(h) for h in lista_saltos)

            m_mesh = regex_ping.search(val_mesh)
            avg_mesh = None
            if m_mesh:
                avg_mesh = float(m_mesh.group('avg'))
                t_mesh.append(t)
                y_mesh.append(avg_mesh)
            elif "Timeout" in val_mesh or "Unreachable" in val_mesh:
                t_mesh.append(t)
                y_mesh.append(39) # Failure Zone

            if prev_hop_count is not None and hop_count != prev_hop_count:
                y_coord = avg_mesh if avg_mesh else 39 
                if hop_count > prev_hop_count:
                    transitions_mesh.append((t, "1->2", y_coord))
                elif hop_count < prev_hop_count:
                    transitions_mesh.append((t, "2->1", y_coord))
            
            prev_hop_count = hop_count

            # --- PROCESS DIRECT (.2) ---
            val_dir = destinos.get(IP_DIRECTO, {}).get("ping_80bytes", "")
            m_dir = regex_ping.search(val_dir)
            if m_dir:
                t_dir.append(t)
                y_dir.append(float(m_dir.group('avg')))
            elif "Timeout" in val_dir or "Unreachable" in val_dir:
                t_dir.append(t)
                y_dir.append(41) # Failure Zone

except FileNotFoundError:
    print(f"❌ Error: File {ARCHIVO_JSON} not found.")
    exit()

# ==========================================
# MATHEMATICAL INTERPOLATION FOR DISTANCE AXIS
# ==========================================
# We calculate the exact time you crossed 0, 10, 20... meters
base_date = (t_mesh or t_dir)[0].strftime('%Y-%m-%d')
fmt = "%Y-%m-%d %H:%M:%S"

def parse_t(time_str):
    return datetime.strptime(f"{base_date} {time_str}", fmt)

def get_time_for_dist(d_target, nodes):
    for i in range(len(nodes)-1):
        t1, d1 = nodes[i]
        t2, d2 = nodes[i+1]
        if (d1 <= d_target <= d2) or (d1 >= d_target >= d2):
            if d1 == d2: return t1
            fraction = (d_target - d1) / (d2 - d1)
            return t1 + (t2 - t1) * fraction
    return nodes[-1][0]

# Nodes defining your physical movement speed
phase1_out = [(parse_t("20:13:30"), 0), (parse_t("20:14:00"), 8), (parse_t("20:14:10"), 16), (parse_t("20:14:25"), 24), (parse_t("20:14:50"), 42), (parse_t("20:15:00"), 50)]
phase1_in  = [(parse_t("20:15:00"), 50), (parse_t("20:15:25"), 24), (parse_t("20:15:47"), 0)]
phase2_out = [(parse_t("20:16:50"), 0), (parse_t("20:17:00"), 8), (parse_t("20:17:15"), 16), (parse_t("20:17:30"), 24), (parse_t("20:17:50"), 42), (parse_t("20:18:00"), 50)]
phase2_in  = [(parse_t("20:18:00"), 50), (parse_t("20:18:30"), 24), (parse_t("20:19:00"), 0)]

# The continuous ticks we want to show on the bottom axis
dists_out = [0, 10, 20, 30, 40, 50]
dists_in  = [40, 30, 20, 10, 0] # We skip 50 to avoid repeating the peak

sec_ticks_dt, sec_ticks_lbl = [], []
for nodes, targets in [(phase1_out, dists_out), (phase1_in, dists_in), (phase2_out, dists_out), (phase2_in, dists_in)]:
    for d in targets:
        sec_ticks_dt.append(get_time_for_dist(d, nodes))
        sec_ticks_lbl.append(str(d))

# ==========================================
# DRAW FINAL PLOT
# ==========================================
fig, ax = plt.subplots(figsize=(20, 8.5), dpi=150)
ax.set_ylim(0, 45)

# 1. Multi-hop Background Shading
for i, (t, tipo, _) in enumerate(transitions_mesh):
    if "1->2" in tipo:
        start_t = t
        end_t = None
        for j in range(i+1, len(transitions_mesh)):
            if "2->1" in transitions_mesh[j][1]:
                end_t = transitions_mesh[j][0]
                break
        if not end_t: end_t = t_mesh[-1] if t_mesh else t
        
        ax.axvspan(start_t, end_t, color='#e67e22', alpha=0.08, zorder=0)
        ax.text(start_t + (end_t - start_t)/2, 30, "MULTI-HOP\nACTIVE", 
                 ha="center", va="center", fontsize=11, fontweight="bold", color="#e67e22", alpha=0.6)

# 2. Draw Lines
ax.plot(t_dir, y_dir, marker='o', markersize=4, linestyle='-', color='#3498db', linewidth=2, label='Direct Link (No Relay)', alpha=0.8)
ax.plot(t_mesh, y_mesh, marker='o', markersize=4, linestyle='-', color='#e74c3c', linewidth=2, label='BATMAN-adv Mesh Link')

# 3. Failure Zone Line
ax.axhline(36, color='black', linestyle='-', lw=1.2, alpha=0.5)
ax.text((t_dir or t_mesh)[0], 36.5, "FAILURE ZONE (TIMEOUTS)", color='black', fontsize=9, fontweight='bold', alpha=0.6)

# 4. Vertical Milestone Lines & Text INSIDE the graph
for hora_str, etiqueta in HITOS:
    if not t_mesh and not t_dir: break
    hora_hito = datetime.strptime(f"{(t_mesh or t_dir)[0].strftime('%Y-%m-%d')} {hora_str}", "%Y-%m-%d %H:%M:%S")
    ax.axvline(x=hora_hito, color='gray', linestyle='--', alpha=0.4, zorder=0)
    ax.text(hora_hito, 2, etiqueta, rotation=90, va='bottom', ha='right', color='gray', fontsize=10)

# 5. Phase Separator
hora_mitad = parse_t("20:16:15")
ax.axvline(x=hora_mitad, color='black', linestyle='-', lw=3, zorder=0)
ax.text(hora_mitad, 43, " ⬅ PHASE 1: NO RELAY  |  PHASE 2: RASPBERRY PI RELAY ACTIVE ➡ ", 
         ha='center', va='center', fontsize=12, fontweight='bold', color='white', 
         bbox=dict(facecolor='black', alpha=0.8, pad=5))

# 6. Primary X-Axis (Time - Diagonal so they don't overlap)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)

# 7. Secondary X-Axis (MATHEMATICAL DISTANCE, ONLY NUMBERS)
ax2 = ax.secondary_xaxis('bottom')
ax2.spines['bottom'].set_position(('outward', 50)) # Separate it visually from the time
ax2.set_xticks(sec_ticks_dt)
ax2.set_xticklabels(sec_ticks_lbl, rotation=0, ha='center', fontsize=10, fontweight='bold', color='#333333')
ax2.tick_params(axis='x', length=5)

# 8. Titles and Labels
ax.set_title("Network Resiliency Timeline: Direct Link vs BATMAN-adv Mesh Routing", fontweight='bold', fontsize=14, pad=15)
# Using linebreaks to properly title both axes without overlapping
ax.set_xlabel("Time (HH:MM:SS)\n\n\nDistance (m)", labelpad=10, fontsize=11, fontweight='bold') 
ax.set_ylabel("RTT Latency (ms)", fontsize=11)
ax.grid(True, alpha=0.3, zorder=0)

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=10, framealpha=0.9)

plt.tight_layout()
plt.savefig('grafica1_timeline_final_continua.png', dpi=200)
print("✅ Gráfica generada. Eje de distancias continuo y preciso.")