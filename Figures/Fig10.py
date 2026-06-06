import json
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & MILESTONES
# ==========================================
ARCHIVO_JSON = "datos_prueba.json"

HITOS_FASE1 = [
    ("20:13:30", 0), ("20:14:00", 8), ("20:14:10", 16),
    ("20:14:25", 24), ("20:14:40", 38), ("20:14:50", 42),
    ("20:15:00", 50), ("20:15:25", 24), ("20:15:47", 0)
]

HITOS_FASE2 = [
    ("20:16:50", 0), ("20:17:00", 8), ("20:17:15", 16),
    ("20:17:30", 24), ("20:17:50", 42), ("20:18:00", 50),
    ("20:18:30", 24), ("20:19:00", 0)
]

def hora_a_segs(h_str):
    t = datetime.strptime(h_str, "%H:%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second

hitos1_sec = [(hora_a_segs(h), m) for h, m in HITOS_FASE1]
hitos2_sec = [(hora_a_segs(h), m) for h, m in HITOS_FASE2]

def interpolar_distancia(ts_sec, hitos):
    if ts_sec <= hitos[0][0]: return hitos[0][1]
    if ts_sec >= hitos[-1][0]: return hitos[-1][1]
    for i in range(len(hitos) - 1):
        t1, m1 = hitos[i]
        t2, m2 = hitos[i+1]
        if t1 <= ts_sec <= t2:
            return m1 + (m2 - m1) * ((ts_sec - t1) / (t2 - t1))
    return 0

# ==========================================
# 2. DATA EXTRACTION
# ==========================================
TIMEOUT_ONE_WAY = 25.0 

# Buckets de distancia
dir_close, dir_mid, dir_far = [], [], []
mesh_close, mesh_mid, mesh_far = [], [], []

def assign_to_bucket(distance, latencies, is_direct=False):
    # Si es enlace directo y supera los 24m, forzar Timeout
    if is_direct and distance >= 24.0:
        latencies = [TIMEOUT_ONE_WAY] * max(1, len(latencies))
        
    for lat in latencies:
        if distance <= 15.0:
            if is_direct: dir_close.append(lat)
            else: mesh_close.append(lat)
        elif distance <= 30.0:
            if is_direct: dir_mid.append(lat)
            else: mesh_mid.append(lat)
        else:
            if is_direct: dir_far.append(lat)
            else: mesh_far.append(lat)

def extract_pings(ping_str):
    if not ping_str or "100% packet loss" in ping_str or "Timeout" in ping_str:
        return [TIMEOUT_ONE_WAY] * 3 # Asumimos 3 paquetes perdidos
    
    # Extraer CADA ping individual (no la media)
    matches = re.findall(r"time=([\d\.]+) ms", ping_str)
    if matches:
        return [float(m)/2.0 for m in matches] # Dividimos entre 2 para One-Way
    return [TIMEOUT_ONE_WAY] * 3

try:
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        
    for entrada in datos:
        ts_sec = hora_a_segs(entrada.get("timestamp", "").split(" ")[1])
        dest = entrada.get("destinos", {})
        
        # Fase 1 (Direct Link)
        if hitos1_sec[0][0] - 5 <= ts_sec <= hitos1_sec[-1][0]:
            dist = interpolar_distancia(ts_sec, hitos1_sec)
            pings = extract_pings(dest.get("192.168.10.2", {}).get("ping_80bytes", ""))
            assign_to_bucket(dist, pings, is_direct=True)
            
        # Fase 2 (Mesh Link)
        if hitos2_sec[0][0] - 5 <= ts_sec <= hitos2_sec[-1][0]:
            dist = interpolar_distancia(ts_sec, hitos2_sec)
            pings = extract_pings(dest.get("192.168.10.1", {}).get("ping_80bytes", ""))
            assign_to_bucket(dist, pings, is_direct=False)

except Exception as e:
    print(f"Error reading JSON: {e}")
    exit()

# ==========================================
# 3. PLOTTING THE BOXPLOT
# ==========================================
fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

data_mesh = [mesh_close, mesh_mid, mesh_far]
data_dir = [dir_close, dir_mid, dir_far]

# Posiciones en el eje X para agrupar las cajas
pos_mesh = [1, 3, 5]
pos_dir = [1.6, 3.6, 5.6]

# Estilos de las cajas
box_width = 0.4
prop_mesh = dict(facecolor='#2A9D8F', color='#1D7066', linewidth=2)
prop_dir = dict(facecolor='#E63946', color='#9E2A2B', linewidth=2)
median_props = dict(color='white', linewidth=2)
flier_props = dict(marker='o', markerfacecolor='gray', markersize=4, alpha=0.5)

# Dibujar las cajas
bp1 = ax.boxplot(data_mesh, positions=pos_mesh, widths=box_width, patch_artist=True, 
                 boxprops=prop_mesh, medianprops=median_props, flierprops=flier_props, 
                 whiskerprops=dict(linewidth=2, color='#1D7066'), capprops=dict(linewidth=2, color='#1D7066'))

bp2 = ax.boxplot(data_dir, positions=pos_dir, widths=box_width, patch_artist=True, 
                 boxprops=prop_dir, medianprops=median_props, flierprops=flier_props,
                 whiskerprops=dict(linewidth=2, color='#9E2A2B'), capprops=dict(linewidth=2, color='#9E2A2B'))

# Añadir línea de Timeout / Zona Muerta
ax.axhline(TIMEOUT_ONE_WAY, color='gray', linestyle='--', linewidth=1.5, zorder=0)
ax.text(6.5, TIMEOUT_ONE_WAY + 0.5, 'Timeout / Connection Lost', color='gray', fontweight='bold', ha='right')

# Etiquetas del eje X
ax.set_xticks([1.3, 3.3, 5.3])
ax.set_xticklabels(['0 - 15m\n(Close Range)', '15 - 30m\n(Mid Range)', '30 - 50m\n(Far Range)'], fontsize=11, fontweight='bold')

# Títulos y Leyenda
ax.set_title("Latency Distribution by Distance Zone (One-Way RTT)", fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel("Latency (ms)", fontsize=12, fontweight='bold')
ax.set_ylim(0, TIMEOUT_ONE_WAY + 3)

# Leyenda personalizada
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2A9D8F', edgecolor='#1D7066', label='Mesh Network (BATMAN-adv)'),
    Patch(facecolor='#E63946', edgecolor='#9E2A2B', label='Direct Link (No Mesh)')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('boxplot_latency_distance.png', dpi=200, bbox_inches='tight')
print("✅ Boxplot saved: 'boxplot_latency_distance.png'")