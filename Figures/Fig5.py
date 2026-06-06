import matplotlib.pyplot as plt
import matplotlib.patches as patches


plt.style.use('default')
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')



ax.plot([0, 1], [0.5, 0.5], color='gray', linestyle='--', linewidth=1.5)


ax.text(0.02, 0.92, "Traditional Cloud Architecture", fontsize=14, fontweight='bold', color='#1D3557')
ax.text(0.02, 0.42, "Edge Computing Architecture (Proposed)", fontsize=14, fontweight='bold', color='#1D3557')



cam_box1 = patches.FancyBboxPatch((0.05, 0.65), 0.15, 0.15, boxstyle="round,pad=0.02", facecolor="#457B9D", edgecolor="black")
ax.add_patch(cam_box1)
ax.text(0.125, 0.725, "IP Camera", color="white", fontsize=11, fontweight='bold', ha='center', va='center')


cloud_box = patches.FancyBboxPatch((0.75, 0.65), 0.2, 0.15, boxstyle="round,pad=0.05", facecolor="#1D3557", edgecolor="black")
ax.add_patch(cloud_box)
ax.text(0.85, 0.725, "Cloud\nServer", color="white", fontsize=11, fontweight='bold', ha='center', va='center')


ax.annotate("", xy=(0.73, 0.725), xytext=(0.22, 0.725),
            arrowprops=dict(facecolor='#E63946', edgecolor='#9E2A2B', width=12, headwidth=20, shrink=0.02))

ax.text(0.475, 0.78, "Raw Video Stream\n(Bandwidth: ~4 Mbps)", fontsize=11, fontweight='bold', color='#9E2A2B', ha='center')



cam_box2 = patches.FancyBboxPatch((0.05, 0.15), 0.12, 0.15, boxstyle="round,pad=0.02", facecolor="#457B9D", edgecolor="black")
ax.add_patch(cam_box2)
ax.text(0.11, 0.225, "Camera", color="white", fontsize=10, fontweight='bold', ha='center', va='center')


jetson_box = patches.FancyBboxPatch((0.25, 0.12), 0.22, 0.2, boxstyle="round,pad=0.02", facecolor="#F4A261", edgecolor="black")
ax.add_patch(jetson_box)
ax.text(0.36, 0.225, "NVIDIA Jetson\n+ YOLO AI", color="black", fontsize=11, fontweight='bold', ha='center', va='center')

ax.annotate("", xy=(0.24, 0.225), xytext=(0.18, 0.225),
            arrowprops=dict(facecolor='black', width=3, headwidth=8, shrink=0.02))


control_box = patches.FancyBboxPatch((0.75, 0.15), 0.2, 0.15, boxstyle="round,pad=0.05", facecolor="#1D3557", edgecolor="black")
ax.add_patch(control_box)
ax.text(0.85, 0.225, "Control\nCenter", color="white", fontsize=11, fontweight='bold', ha='center', va='center')


ax.annotate("", xy=(0.73, 0.225), xytext=(0.49, 0.225),
            arrowprops=dict(facecolor='#2A9D8F', edgecolor='#1D7066', width=2, headwidth=8, shrink=0.02))


ax.text(0.61, 0.28, "JSON Metadata Alert\n(Bandwidth: ~50 Kbps)", fontsize=11, fontweight='bold', color='#1D7066', ha='center')


ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig('figura4_edge_vs_cloud.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Gráfico guardado como: 'figura4_edge_vs_cloud.png'")