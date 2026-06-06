import json
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.cm import ScalarMappable
import matplotlib.colors as mcolors
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & MILESTONES
# ==========================================
ARCHIVO_JSON = "datos_prueba.json"
ARCHIVO_PLANO = "Fig6.png"

# PHASE 1: Direct Link (No intermediate node)
HITOS_FASE1 = [
    ("20:13:30", 0),
    ("20:14:00", 8),
    ("20:14:10", 16),
    ("20:14:25", 24),
    ("20:14:40", 38),
    ("20:14:50", 42),
    ("20:15:00", 50),
    ("20:15:25", 24),
    ("20:15:47", 0)
]

# PHASE 2: Mesh (BATMAN-adv with intermediate node)
HITOS_FASE2 = [
    ("20:16:50", 0),
    ("20:17:00", 8),
    ("20:17:15", 16),
    ("20:17:30", 24),
    ("20:17:50", 42),
    ("20:18:00", 50),
    ("20:18:30", 24),
    ("20:19:00", 0)
]

def hora_a_segs(h_str):
    t = datetime.strptime(h_str, "%H:%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second

hitos1_sec = [(hora_a_segs(h), m) for h, m in HITOS_FASE1]
hitos2_sec = [(hora_a_segs(h), m) for h, m in HITOS_FASE2]

# Route pixels
puntos_ruta = [
    (89, 1375), (267, 1375), (553, 1169), (553, 985), 
    (2795, 985), (2795, 913), (2907, 917)
]

# ==========================================
# 2. SPATIAL MAPPING FUNCTIONS
# ==========================================
dist_seg = [np.linalg.norm(np.array(puntos_ruta[i+1]) - np.array(puntos_ruta[i])) for i in range(len(puntos_ruta)-1)]
dist_total_px = sum(dist_seg)

def get_xy_from_meters(metros):
    dist_objetivo_px = (max(0, min(metros, 50)) / 50.0) * dist_total_px
    acumulada = 0
    for j, d in enumerate(dist_seg):
        if acumulada + d >= dist_objetivo_px or j == len(dist_seg) - 1:
            ratio = (dist_objetivo_px - acumulada) / d if d > 0 else 0
            px = puntos_ruta[j][0] + (puntos_ruta[j+1][0] - puntos_ruta[j][0]) * ratio
            py = puntos_ruta[j][1] + (puntos_ruta[j+1][1] - puntos_ruta[j][1]) * ratio
            return px, py
        acumulada += d
    return puntos_ruta[-1]

def interpolar_distancia_por_hora(ts_sec, hitos):
    if ts_sec <= hitos[0][0]: return hitos[0][1]
    if ts_sec >= hitos[-1][0]: return hitos[-1][1]
    for i in range(len(hitos) - 1):
        t1, m1 = hitos[i]
        t2, m2 = hitos[i+1]
        if t1 <= ts_sec <= t2:
            return m1 + (m2 - m1) * ((ts_sec - t1) / (t2 - t1))
    return 0

# ==========================================
# 3. DATA EXTRACTION & INTERPOLATION
# ==========================================
regex_ping = re.compile(r"=\s*[\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+\s*ms")
TIMEOUT_RTT = 50.0 

def extrae_ida(ping_str):
    if not ping_str or "Timeout" in ping_str or "100% packet loss" in ping_str:
        return TIMEOUT_RTT / 2.0
    m = regex_ping.search(ping_str)
    return float(m.group(1)) / 2.0 if m else TIMEOUT_RTT / 2.0

raw_t, raw_lat_mesh, raw_lat_dir = [], [], []

try:
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    for entrada in datos:
        ts_sec = hora_a_segs(entrada.get("timestamp", "").split(" ")[1])
        dest = entrada.get("destinos", {})
        raw_t.append(ts_sec)
        raw_lat_mesh.append(extrae_ida(dest.get("192.168.10.1", {}).get("ping_80bytes", "")))
        raw_lat_dir.append(extrae_ida(dest.get("192.168.10.2", {}).get("ping_80bytes", "")))
except Exception as e:
    print(f"Error reading JSON: {e}")
    exit()

t_dense_fase1 = np.arange(hitos1_sec[0][0], hitos1_sec[-1][0] + 1)
t_dense_fase2 = np.arange(hitos2_sec[0][0], hitos2_sec[-1][0] + 1)

lat_fase1 = np.interp(t_dense_fase1, raw_t, raw_lat_dir)
lat_fase2 = np.interp(t_dense_fase2, raw_t, raw_lat_mesh)

coord_x_dir, coord_y_dir = [], []
coord_x_mesh, coord_y_mesh = [], []

# Phase 1
for i, t in enumerate(t_dense_fase1):
    m = interpolar_distancia_por_hora(t, hitos1_sec)
    if m >= 24.0:
        lat_fase1[i] = TIMEOUT_RTT / 2.0 
    px, py = get_xy_from_meters(m)
    coord_x_dir.append(px); coord_y_dir.append(py)

# Phase 2
for i, t in enumerate(t_dense_fase2):
    m = interpolar_distancia_por_hora(t, hitos2_sec)
    px, py = get_xy_from_meters(m)
    coord_x_mesh.append(px); coord_y_mesh.append(py)

# ==========================================
# 4. KDE GENERATION (Ajustado para nubes más suaves)
# ==========================================
img = mpimg.imread(ARCHIVO_PLANO)
h, w = img.shape[:2]
paso = 5 
xg, yg = np.meshgrid(np.arange(0, w, paso), np.arange(0, h, paso))

Z_mesh, W_mesh = np.zeros_like(xg, dtype=float), np.zeros_like(xg, dtype=float)
Z_dir, W_dir   = np.zeros_like(xg, dtype=float), np.zeros_like(xg, dtype=float)

# 1. AUMENTAMOS EL SIGMA: De 70.0 a 120.0 para hacer la nube más ancha y esponjosa
SIGMA = 120.0 

print("Generating Phase 1 (Direct)...")
for i in range(len(coord_x_dir)):
    peso = np.exp(-((xg - coord_x_dir[i])**2 + (yg - coord_y_dir[i])**2) / (2 * SIGMA**2))
    Z_dir += peso * lat_fase1[i]
    W_dir += peso

print("Generating Phase 2 (Mesh)...")
for i in range(len(coord_x_mesh)):
    peso = np.exp(-((xg - coord_x_mesh[i])**2 + (yg - coord_y_mesh[i])**2) / (2 * SIGMA**2))
    Z_mesh += peso * lat_fase2[i]
    W_mesh += peso

m_mask, d_mask = W_mesh > 0, W_dir > 0
Z_mesh[m_mask] /= W_mesh[m_mask]
Z_dir[d_mask]  /= W_dir[d_mask]

cmap = plt.get_cmap('turbo')
norm = mcolors.Normalize(vmin=0, vmax=25.0)

rgba_mesh, rgba_dir = cmap(norm(Z_mesh)), cmap(norm(Z_dir))

W_mesh_norm = W_mesh / np.max(W_mesh) if np.max(W_mesh) > 0 else W_mesh
W_dir_norm = W_dir / np.max(W_dir) if np.max(W_dir) > 0 else W_dir

# 2. SUAVIZAMOS EL ALPHA: Reducimos el multiplicador de 2.0 a 1.2 para un "fade" más gradual
rgba_mesh[..., 3] = np.clip(W_mesh_norm * 1.2, 0, 0.8) 
rgba_dir[..., 3]  = np.clip(W_dir_norm * 1.2, 0, 0.8)

# ==========================================
# 5. PLOTTING
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), dpi=200)
fig.suptitle("Spatial Coverage Heatmap", fontsize=18, fontweight='bold', y=0.96)

# --- MESH ---
ax1.imshow(img)
ax1.imshow(rgba_mesh, extent=[0, w, h, 0], origin='upper')
ax1.set_title("Phase 2: Mesh Topology", fontsize=14, fontweight='bold', pad=10)
ax1.axis('off')

# --- DIRECT ---
ax2.imshow(img)
ax2.imshow(rgba_dir, extent=[0, w, h, 0], origin='upper')
ax2.set_title("Phase 1: Direct Link", fontsize=14, fontweight='bold', pad=10)
ax2.axis('off')

# Colorbar
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
sm = ScalarMappable(norm=norm, cmap=cmap)
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('One-Way Latency (ms) [Red = Dead Zone]', fontsize=12, fontweight='bold')

plt.subplots_adjust(left=0.05, right=0.9, top=0.92, bottom=0.05, hspace=0.1)
plt.savefig('heatmap_english_suave.png', bbox_inches='tight', facecolor='white')
print("✅ Saved: heatmap_english_suave.png")