import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches


plt.style.use('default')
fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')


G = nx.Graph()
# Definimos 6 nodos
nodos = ['A', 'B', 'C', 'D', 'E', 'F']
# Definimos las posibles conexiones de la malla
conexiones = [('A', 'B'), ('A', 'C'), ('A', 'D'), 
              ('B', 'E'), ('C', 'E'), ('C', 'D'), 
              ('D', 'F'), ('E', 'F')]
G.add_edges_from(conexiones)


posiciones = {
    'A': (0, 0.5),   # Nodo origen (Izquierda)
    'B': (1, 0.8),   # Vecinos directos
    'C': (1, 0.5),
    'D': (1, 0.2),
    'E': (2, 0.65),  # Siguientes saltos
    'F': (2, 0.35)
}


# Dibujar líneas de conexión (Capa física posible)
nx.draw_networkx_edges(G, posiciones, ax=ax, edge_color='#888888', style='dotted', width=1.5)

# Dibujar los nodos (Círculos blancos con borde negro)
nx.draw_networkx_nodes(G, posiciones, ax=ax, node_color='white', edgecolors='black', node_size=1200, linewidths=2)

# Añadir las etiquetas de los nodos (A, B, C...)
nx.draw_networkx_labels(G, posiciones, ax=ax, font_color='black', font_weight='bold', font_size=12)


# 4.1 Añadir ondas de radio concéntricas alrededor del Nodo A
for radio in [0.25, 0.5, 0.75]:
    onda = patches.Circle(posiciones['A'], radio, fill=False, linestyle='--', color='black', alpha=0.3, lw=1.5)
    ax.add_patch(onda)

# 4.2 Dibujar flechas marcando el envío del OGM a los vecinos (B, C, D)
estilo_flecha = dict(arrowstyle="-|>", color="black", lw=2, shrinkA=20, shrinkB=20)
ax.annotate("", xy=posiciones['B'], xytext=posiciones['A'], arrowprops=estilo_flecha)
ax.annotate("", xy=posiciones['C'], xytext=posiciones['A'], arrowprops=estilo_flecha)
ax.annotate("", xy=posiciones['D'], xytext=posiciones['A'], arrowprops=estilo_flecha)

# 4.3 Añadir las etiquetas "OGM" sobre las flechas
caja_texto = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", lw=1)
ax.text(0.5, 0.68, "OGM", fontsize=10, fontweight='bold', bbox=caja_texto, ha='center')
ax.text(0.5, 0.5, "OGM", fontsize=10, fontweight='bold', bbox=caja_texto, ha='center')
ax.text(0.5, 0.32, "OGM", fontsize=10, fontweight='bold', bbox=caja_texto, ha='center')


ax.set_title("Route Discovery Mechanism (OGM Flooding)", fontsize=14, fontweight='bold', pad=20)

# Ocultar los ejes para que parezca un diagrama limpio
ax.axis('off')

# Guardar la imagen en alta resolución
plt.tight_layout()
plt.savefig('figura3_batman_ogm.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Gráfico guardado como: 'figura3_batman_ogm.png'")