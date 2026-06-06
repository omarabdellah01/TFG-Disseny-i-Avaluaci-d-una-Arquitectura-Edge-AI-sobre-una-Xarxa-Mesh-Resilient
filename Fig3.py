import matplotlib.pyplot as plt
import numpy as np


plt.style.use('default')
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
fig.patch.set_facecolor('#F8F9FA')  # Fondo gris muy claro
ax.set_facecolor('#F8F9FA')


saltos = np.array([1, 2, 3, 4, 5])
c_max = 100.0  # Capacidad máxima de partida (100%)
gamma = 0.10   # Factor de overhead (10% por saltos CSMA/CA)


capacitat = (c_max / saltos) * ((1 - gamma) ** (saltos - 1))


# Barras de capacidad
barras = ax.bar(saltos, capacitat, width=0.55, color='#E63946', edgecolor='#9E2A2B', linewidth=1.5, alpha=0.85)

# Línea de tendencia (Caída exponencial inversa)
ax.plot(saltos, capacitat, color='#1D3557', marker='o', markersize=8, linewidth=2.5, linestyle='--', zorder=3)

# Añadir los porcentajes encima de cada barra
for bar in barras:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2.5, f'{yval:.1f}%', 
            ha='center', va='bottom', fontweight='bold', fontsize=11, color='#1D3557')




ax.set_title('Theoretical Capacity Degradation in Linear Topology (Half-Duplex)', 
             fontsize=14, fontweight='bold', pad=20, color='#111111')
ax.set_xlabel('Number of Physical Hops', 
              fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Available Theoretical Capacity (%)', 
              fontsize=12, fontweight='bold', labelpad=10)
# Customize X axis
ax.set_xticks(saltos)
ax.set_xticklabels(['1 Hop\n(Direct)', '2 Hops', '3 Hops', '4 Hops', '5 Hops'], fontsize=10)

ax.set_ylim(0, 115)

# Cuadrícula sutil
ax.grid(axis='y', linestyle='--', alpha=0.4, color='gray')


ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('gray')
ax.spines['bottom'].set_color('gray')

# Guardar y mostrar
plt.tight_layout()
plt.savefig('figura2_degradacio_teorica.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico guardado como: 'figura2_degradacio_teorica.png'")