import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# =========================================================================
# 1. 全局样式与论文规范设置 (IEEE 会议论文优化)
# NOTE: 使用者通常无需修改此处，除非需要调整整体风格，Linux 或 Mac 用户可能需要安装 Times New Roman 字体以确保兼容性
# =========================================================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.labelsize'] = 14      
plt.rcParams['xtick.labelsize'] = 12     
plt.rcParams['ytick.labelsize'] = 12     
plt.rcParams['legend.fontsize'] = 11     
plt.rcParams['axes.titlesize'] = 14      

# =========================================================================
# 2. 全局绘图参数与文本配置
# NOTE: 使用者只需在此处修改文字或调整位置
# =========================================================================
CONFIG = {
    # 基础输出配置
    'save_path': 'figures/fig5.pdf',
    'fig_size': (7.2, 3.5),
    'input_data': 'data/fig5_data.json',

    # 算法名称映射 (用于图例显示)
    'baselines': ['mobiu_mac', 'dr_dlma_oracle', 'dr_dlma', "dl_mac_p6", "dl_mac_p6_ft", "dl_mac_p3_ft"],
    'name_map': {
        'mobiu_mac': 'MobiU-MAC',
        'dr_dlma_oracle': 'Oracle',
        'dr_dlma': 'DR-DLMA',
        "dl_mac_p6": "DL-MAC-P6",
        "dl_mac_p6_ft": "DL-MAC-P6-FT",
        "dl_mac_p3_ft": "DL-MAC-P3-FT"
    },
    
    # 算法视觉外观映射
    'line_styles': [
        {'color': '#003399', 'marker': 'o', 'linestyle': '-', 'linewidth': 2.2, 'alpha': 0.1},
        {'color': '#D95F02', 'marker': 's', 'linestyle': '--', 'linewidth': 1.5, 'alpha': 0.1},
        {'color': '#FDAE61', 'marker': '', 'linestyle': '-.', 'linewidth': 1.25, 'alpha': 0.1},
        {'color': '#CBC9E2', 'marker': '', 'linestyle': ':', 'linewidth': 1.25, 'alpha': 0.12},
        {'color': '#9E9AC8', 'marker': '', 'linestyle': '--', 'linewidth': 1.25, 'alpha': 0.12},
        {'color': '#7570B3', 'marker': 'x', 'linestyle': '-.', 'linewidth': 1.5, 'alpha': 0.1},
    ],

    # (a) 左图：不同移动速度下的稳定性拓扑配置
    'left_graph': {
        'title': '(a) Impact of AUV Mobility',
        'xlabel': 'AUV Mobility (m/s)',
        'ylabel': 'Steady-state Throughput',
        'speeds': [1, 2, 6, 10, 15, 20, 30],
        'ylim': (0, 1.1)
    },
    
    # (b) 右图：极端高移动性下的收敛表现
    'right_graph': {
        'title': '(b) Convergence under High Mobility',
        'xlabel': r'Time Slot ($\times 10^4$)',
        'ylabel': 'Running Avg. Throughput',
        'target_case': 'case1_30',
        'xlim': (0, 50000),
        'ylim': (0, 1.1),
        'xticks': [0, 10000, 20000, 30000, 40000, 50000],
        'xticklabels': ['0', '1', '2', '3', '4', '5']
    }
}

# =========================================================================
# 3. 读入绘图数据
# =========================================================================
def load_structures_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    mobility_data = {}
    for algo, data in payload['mobility_data'].items():
        mobility_data[algo] = {
            'speed': np.array(data['speed']),
            'mean': np.array(data['mean']),
            'std': np.array(data['std'])
        }
        
    convergence_data = {}
    for algo, data in payload['convergence_data'].items():
        convergence_data[algo] = {
            'step': np.array(data['step']),
            'mean': np.array(data['mean']),
            'std': np.array(data['std'])
        }
    return mobility_data, convergence_data


# =========================================================================
# 4. 图形绘制核心
# =========================================================================
def plot_dynamic_mobility_results(baselines, name_map, mobility_data, convergence_data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=CONFIG['fig_size'])
    
    cfg_a = CONFIG['left_graph']
    cfg_b = CONFIG['right_graph']

    # ==========================================
    # (a) 左图：不同速度下的吞吐量 (折线 + 阴影)
    # ==========================================
    for i, algo in enumerate(baselines):
        speeds = mobility_data[algo]['speed']
        means  = mobility_data[algo]['mean']
        stds   = mobility_data[algo]['std']
        
        if len(speeds) > 0:
            st = CONFIG['line_styles'][i]
            ax1.plot(speeds, means, label=name_map[algo],
                     color=st['color'], marker=st['marker'], linestyle=st['linestyle'],
                     linewidth=st['linewidth'], markersize=5, zorder=3)
            ax1.fill_between(speeds, means - stds, means + stds, 
                             color=st['color'], alpha=st['alpha'], edgecolor='none', zorder=2)

    ax1.set_ylim(cfg_a['ylim'])
    ax1.set_xlabel(cfg_a['xlabel'], labelpad=5)
    ax1.set_ylabel(cfg_a['ylabel'])
    ax1.set_xticks(cfg_a['speeds'])
    ax1.set_title(cfg_a['title'], pad=10)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # ==========================================
    # (b) 右图：特定高速度场景下的收敛曲线
    # ==========================================
    for i, algo in enumerate(baselines):
        steps = convergence_data[algo]['step']
        means = convergence_data[algo]['mean']
        stds  = convergence_data[algo]['std']
        
        if len(steps) > 0:
            st = CONFIG['line_styles'][i]
            line, = ax2.plot(steps, means, color=st['color'], 
                             linestyle=st['linestyle'], linewidth=st['linewidth'],
                             marker=st['marker'], markevery=5000, markersize=5, 
                             zorder=1 if i == 0 else 0)
            ax2.fill_between(steps, means - stds, means + stds, 
                             color=line.get_color(), alpha=st['alpha'])

    ax2.set_xlim(cfg_b['xlim'])
    ax2.set_ylim(cfg_b['ylim'])
    ax2.set_xticks(cfg_b['xticks'])
    ax2.set_xticklabels(cfg_b['xticklabels'])
    ax2.set_xlabel(cfg_b['xlabel'], labelpad=5)
    ax2.set_ylabel(cfg_b['ylabel'])
    ax2.set_title(cfg_b['title'], pad=10)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # ==========================================
    # 动图例设置
    # ==========================================
    handles = []
    labels = []
    for i, algo in enumerate(baselines):
        st = CONFIG['line_styles'][i]
        name = name_map[algo]
        proxy = Line2D([0], [0], color=st['color'], marker=st['marker'], 
                       linestyle=st['linestyle'], linewidth=st['linewidth'], markersize=6)
        handles.append(proxy)
        labels.append(f"{name} (Proposed)" if i == 0 else name)

    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.08),
               ncol=3, frameon=False, columnspacing=1.2, handlelength=3.8)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.24) 
    
    plt.savefig(CONFIG['save_path'], format='pdf', bbox_inches='tight')
    png_path = CONFIG['save_path'].rsplit('.', 1)[0] + '.png'
    plt.savefig(png_path, format='png', bbox_inches='tight')
    print(f"成功保存学术图表至: {CONFIG['save_path']}, {png_path}")
    plt.show()


if __name__ == "__main__":
    if os.path.exists(CONFIG['input_data']):
        print(f"直接加载数据文件: '{CONFIG['input_data']}'...")
        mobility_data, convergence_data = load_structures_from_json(CONFIG['input_data'])

        plot_dynamic_mobility_results(CONFIG['baselines'], CONFIG['name_map'], mobility_data, convergence_data)
    else:
        print(f"致命错误：未找到有效的数据源文件 {CONFIG['input_data']}")