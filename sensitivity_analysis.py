# -*- coding: utf-8 -*-
#
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ===== 基准参数 =====
Mfood = 50000          # 食品总质量 (kg)
Mnonf = 10000          # 非食品总质量 (kg)
Favoid_food_base = 2.7 # 食品避免排放因子
Favoid_nonf_base = 3.0 # 非食品避免排放因子
Rwaste_base = 0.9       # 废弃物转移率
Ftrans = 0.2            # 运输排放因子 (kg CO2e/km)
trip_dist_base = 50     # 单次往返距离 (km)
trips_base = 20         # 年运输次数
Fstore_base = 0.05      # 仓储排放因子 (kg CO2e/kg食品)
NN_base = 24000         # 年消费次数
Fmove_base = 0.02       # 消费者交通排放因子 (kg CO2e/次)


def compute_Enet(Favoid_food, Favoid_nonf, Rwaste, Ftrans, trip_dist, trips,
                 Mfood, Mnonf, Fstore, NN, Fmove):
    Eavoid = (Mfood * Favoid_food + Mnonf * Favoid_nonf) * Rwaste
    Eadd_trans = trips * trip_dist * Ftrans
    Eadd_store = Mfood * Fstore
    Eadd_move = NN * Fmove
    Eadd = Eadd_trans + Eadd_store + Eadd_move
    Enet = (Eavoid - Eadd) / 1000.0
    return Enet, Eavoid, Eadd


# 基准计算
Enet_base, Eavoid_base, Eadd_base = compute_Enet(
    Favoid_food_base, Favoid_nonf_base, Rwaste_base, Ftrans,
    trip_dist_base, trips_base, Mfood, Mnonf, Fstore_base, NN_base, Fmove_base)
print(f"基准: Enet={Enet_base:.2f} t CO2e")

# ===== 敏感度扫描 =====
# 1) Favoid ±20%
pcts = [-20, -10, 0, 10, 20]
Enet_Favoid = []
for p in pcts:
    factor = 1 + p / 100.0
    e, _, _ = compute_Enet(
        Favoid_food_base * factor, Favoid_nonf_base * factor,
        Rwaste_base, Ftrans, trip_dist_base, trips_base,
        Mfood, Mnonf, Fstore_base, NN_base, Fmove_base)
    Enet_Favoid.append(e)
    print(f"Favoid {p:+d}%: {e:.2f}")

# 2) Rwaste
Rwaste_vals = [0.70, 0.80, 0.85, 0.90, 0.95, 1.00]
Enet_Rwaste = []
for r in Rwaste_vals:
    e, _, _ = compute_Enet(
        Favoid_food_base, Favoid_nonf_base, r,
        Ftrans, trip_dist_base, trips_base,
        Mfood, Mnonf, Fstore_base, NN_base, Fmove_base)
    Enet_Rwaste.append(e)
    print(f"Rwaste={r}: {e:.2f}")

# 3) 运输距离
dist_vals = [35, 50, 65]
Enet_dist = []
for d in dist_vals:
    e, _, _ = compute_Enet(
        Favoid_food_base, Favoid_nonf_base, Rwaste_base,
        Ftrans, d, trips_base,
        Mfood, Mnonf, Fstore_base, NN_base, Fmove_base)
    Enet_dist.append(e)
    print(f"dist={d}: {e:.2f}")

# 4) 运输频次
trip_vals = [14, 20, 26]
Enet_trip = []
for t in trip_vals:
    e, _, _ = compute_Enet(
        Favoid_food_base, Favoid_nonf_base, Rwaste_base,
        Ftrans, trip_dist_base, t,
        Mfood, Mnonf, Fstore_base, NN_base, Fmove_base)
    Enet_trip.append(e)
    print(f"trips={t}: {e:.2f}")

# 5) 公交占比 → Fmove 变化
bus_pcts = [30, 50, 70]
Enet_bus = []
for b in bus_pcts:
    Fmove = 0.01 + 0.02 * (b / 100.0)  # 线性插值
    e, _, _ = compute_Enet(
        Favoid_food_base, Favoid_nonf_base, Rwaste_base,
        Ftrans, trip_dist_base, trips_base,
        Mfood, Mnonf, Fstore_base, NN_base, Fmove)
    Enet_bus.append(e)
    print(f"bus={b}%: Fmove={Fmove:.3f}, Enet={e:.2f}")

# ===== 绘图 =====
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle('Sensitivity Analysis of Key Parameters on $E_{net}$', fontsize=14, fontweight='bold')

# 子图1：Favoid
ax = axes[0, 0]
x_labels = ['-20%', '-10%', 'Base', '+10%', '+20%']
colors = ['red', 'orange', 'green', 'blue', 'purple']
bars = ax.bar(x_labels, Enet_Favoid, color=colors, edgecolor='black')
ax.axhline(y=Enet_base, color='gray', linestyle='--', linewidth=1, label=f'Base = {Enet_base:.1f}')
ax.set_ylabel('$E_{net}$ (t CO$_2$e)')
ax.set_title('(a) $F_{avoid}$ ±20%')
ax.legend(fontsize=8)
for bar, val in zip(bars, Enet_Favoid):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}', ha='center', va='bottom', fontsize=8)

# 子图2：Rwaste
ax = axes[0, 1]
x_labels = ['0.70', '0.80', '0.85', '0.90', '0.95', '1.00']
bars = ax.bar(x_labels, Enet_Rwaste, color='steelblue', edgecolor='black')
ax.axhline(y=Enet_base, color='gray', linestyle='--', linewidth=1)
ax.set_ylabel('$E_{net}$ (t CO$_2$e)')
ax.set_title('(b) $R_{waste}$')
for bar, val in zip(bars, Enet_Rwaste):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}', ha='center', va='bottom', fontsize=8)

# 子图3：运输距离
ax = axes[0, 2]
x_labels = ['35 km', '50 km', '65 km']
bars = ax.bar(x_labels, Enet_dist, color='seagreen', edgecolor='black')
ax.axhline(y=Enet_base, color='gray', linestyle='--', linewidth=1)
ax.set_ylabel('$E_{net}$ (t CO$_2$e)')
ax.set_title('(c) Transport Distance')
for bar, val in zip(bars, Enet_dist):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.2f}', ha='center', va='bottom', fontsize=8)

# 子图4：运输频次
ax = axes[1, 0]
x_labels = ['14/yr', '20/yr', '26/yr']
bars = ax.bar(x_labels, Enet_trip, color='orange', edgecolor='black')
ax.axhline(y=Enet_base, color='gray', linestyle='--', linewidth=1)
ax.set_ylabel('$E_{net}$ (t CO$_2$e)')
ax.set_title('(d) Transport Frequency')
for bar, val in zip(bars, Enet_trip):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.2f}', ha='center', va='bottom', fontsize=8)

# 子图5：公交占比
ax = axes[1, 1]
x_labels = ['30%', '50%', '70%']
bars = ax.bar(x_labels, Enet_bus, color='tomato', edgecolor='black')
ax.axhline(y=Enet_base, color='gray', linestyle='--', linewidth=1)
ax.set_ylabel('$E_{net}$ (t CO$_2$e)')
ax.set_title('(e) Public Transit Share')
for bar, val in zip(bars, Enet_bus):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.2f}', ha='center', va='bottom', fontsize=8)

# 子图6：变化率汇总
ax = axes[1, 2]
ax.axis('off')
summary_text = (
    f"Base $E_{{net}} = {Enet_base:.2f}$ t CO$_2$e\n"
    f"─────────────────\n"
    f"$F_{{avoid}}$ ±20% → Δ = ±{abs(Enet_Favoid[0]-Enet_base):.1f} t\n"
    f"$R_{{waste}}$ 0.7→1.0 → Δ = {Enet_Rwaste[-1]-Enet_Rwaste[0]:.1f} t\n"
    f"Transport ±30% → Δ < 0.2 t\n"
    f"Bus share 30%→70% → Δ = {Enet_bus[-1]-Enet_bus[0]:.2f} t\n"
    f"─────────────────\n"
    f"$F_{{avoid}}$ and $R_{{waste}}$ dominate"
)
ax.text(0.1, 0.5, summary_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='center', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('D:/sensitivity_analysis.png', dpi=150, bbox_inches='tight')
print('\n图片已保存: D:/sensitivity_analysis.png')