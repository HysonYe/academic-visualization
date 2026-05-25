import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple

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
    'save_path': 'fig4.pdf',
    'fig_size': (7.2, 3.5),
    'input_data': 'data/fig4_data.json',

    # 算法名称，以及名字映射 (用于图例显示)
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
    'bar_colors': ['#003399', '#5dade2', '#85c1e9', '#aed6f1', '#d6eaf8', '#ebf5fb'],
    'hatches': ['', '//', '..', '\\\\', 'xxx', '--'],
    'line_styles': [
        {'color': '#003399', 'marker': 'o', 'linestyle': '-', 'linewidth': 2.2},
        {'color': '#D95F02', 'marker': 's', 'linestyle': '--', 'linewidth': 1.5},
        {'color': '#FDAE61', 'marker': '^', 'linestyle': '-.', 'linewidth': 1.5},
        {'color': '#CBC9E2', 'marker': 'v', 'linestyle': ':', 'linewidth': 1.5},
        {'color': '#9E9AC8', 'marker': 'd', 'linestyle': '--', 'linewidth': 1.5},
        {'color': '#7570B3', 'marker': 'x', 'linestyle': '-.', 'linewidth': 1.5},
    ],
    
    # (a) 左图：静态场景柱状图配置
    'left_graph': {
        'title': '(a) Heterogeneous Coexistence',
        'xlabel': 'Scenarios',
        'ylabel': 'Steady-state Throughput',
        'xticklabels': ['Case 1', 'Case 2', 'Case 3'],
        'ylim': (0, 1.1)
    },
    
    # (b) 右图：动态恢复折线图配置
    'right_graph': {
        'title': '(b) Resilience to Strategy Shifts',
        'xlabel': r'Time Slot ($\times 10^4$)',
        'ylabel': 'Running Avg. Throughput',
        'xlim': (0, 50000),
        'ylim': (0, 1.1),
        'xticks': [0, 10000, 20000, 30000, 40000, 50000],
        'xticklabels': ['0', '1', '2', '3', '4', '5']
    },
    
    # 右图环境突变与时延标注参数
    'env_change': {
        'change_point': 25000,
        'label_text': 'Strategy Shift',
        'text_x_pos': 25000 + 800,
        'text_y_pos': 0.24,
    },
    'recovery_indicators': [
        {
            'algo_key': 'mobiu_mac',
            'end_slot': 31325,
            'y_pos': 0.8,      
            'color': '#003399',
            'label': r'$\Delta t=6325$',
            'text_offset_x': 1800,
            'vline_ymax_adj': 0.12,
        },
        {
            'algo_key': 'dr_dlma_oracle',
            'end_slot': 30160,
            'y_pos': 1.05,     
            'color': '#D95F02',
            'label': r'$\Delta t=5160$',
            'text_offset_x': 2600,
            'vline_ymax_adj': 0,
        }
    ]
}


# =========================================================================
# 3. 读入绘图数据
# =========================================================================
def load_structures_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    bar_data = payload['bar_data']
    line_data = {}
    
    for algo, data in payload['line_data'].items():
        line_data[algo] = {
            'step': np.array(data['step']),
            'mean': np.array(data['mean']),
            'std': np.array(data['std'])
        }
        
    return bar_data, line_data


# =========================================================================
# 4. 图形绘制函数
# =========================================================================
def plot_static_combined_bottom_legend(baselines, name_map, bar_data, line_data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=CONFIG['fig_size'])
    
    cfg_a = CONFIG['left_graph']
    cfg_b = CONFIG['right_graph']

    # ==========================================
    # (a) 左图：静态场景柱状图绘制
    # ==========================================
    cases_bar = ['case1', 'case2', 'case3']
    x = np.arange(len(cases_bar))
    width = 0.75 / len(baselines)
    
    for i, algo in enumerate(baselines):
        means = [bar_data[algo][case]['mean'] for case in cases_bar]
        stds = [bar_data[algo][case]['std'] for case in cases_bar]
                
        offset = i * width - (len(baselines) - 1) * width / 2
        ax1.bar(x + offset, means, width, yerr=stds,
                color=CONFIG['bar_colors'][i], hatch=CONFIG['hatches'][i],
                capsize=0., edgecolor='black', linewidth=0.5, ecolor='0.3',
                error_kw={'elinewidth': 0.6}, zorder=3)

    ax1.set_ylim(cfg_a['ylim'])
    ax1.set_xlabel(cfg_a['xlabel'], labelpad=5)
    ax1.set_ylabel(cfg_a['ylabel'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(cfg_a['xticklabels'])
    ax1.set_title(cfg_a['title'], pad=10)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # ==========================================
    # (b) 右图：动态恢复折线图绘制
    # ==========================================
    for i, algo in enumerate(baselines):
        steps = line_data[algo]['step']
        means = line_data[algo]['mean']
        stds  = line_data[algo]['std']
        
        if len(steps) > 0:
            st = CONFIG['line_styles'][i]
            line, = ax2.plot(steps, means, color=st['color'], 
                             linestyle=st['linestyle'], linewidth=st['linewidth'],
                             marker=st['marker'], markevery=5000, markersize=5)
            ax2.fill_between(steps, means - stds, means + stds, 
                             color=line.get_color(), alpha=0.1)

    ax2.set_xlim(cfg_b['xlim'])
    ax2.set_ylim(cfg_b['ylim'])
    ax2.set_xticks(cfg_b['xticks'])
    ax2.set_xticklabels(cfg_b['xticklabels'])
    ax2.set_xlabel(cfg_b['xlabel'], labelpad=5)
    ax2.set_ylabel(cfg_b['ylabel'])
    ax2.set_title(cfg_b['title'], pad=10)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # ==========================================
    # 环境切换动态的标注部分
    # ==========================================
    env = CONFIG['env_change']
    ax2.axvline(x=env['change_point'], color='black', linestyle='-.', linewidth=0.8, alpha=0.6)
    ax2.text(env['text_x_pos'], env['text_y_pos'], env['label_text'], color='red', fontsize=9, 
             fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
    
    for item in CONFIG['recovery_indicators']:
        ax2.annotate('', 
                    xy=(env['change_point'], item['y_pos']), 
                    xytext=(item['end_slot'], item['y_pos']),
                    arrowprops=dict(arrowstyle='<->', color=item['color'], lw=1.5))
        
        ax2.vlines(x=item['end_slot'], ymin=item['y_pos']-0.03, ymax=item['y_pos']+0.03+item['vline_ymax_adj'], 
                  colors=item['color'], linestyles='-', lw=1, alpha=0.6)
        
        mid_point = (env['change_point'] + item['end_slot']) / 2 + (item['end_slot'] - env['change_point']) + item['text_offset_x']
        ax2.text(mid_point, item['y_pos']-0.03, item['label'], 
                color=item['color'], fontsize=9, ha='center', va='bottom', fontweight='bold')

    # ==========================================
    # 复合图例设置 
    # ==========================================
    legend_elements = []
    labels = []
    for i, algo in enumerate(baselines):
        bar_proxy = Patch(facecolor=CONFIG['bar_colors'][i], hatch=CONFIG['hatches'][i], edgecolor='black', linewidth=0.5)
        st = CONFIG['line_styles'][i]
        line_proxy = Line2D([0], [0], color=st['color'], marker=st['marker'], 
                            linestyle=st['linestyle'], linewidth=st['linewidth'], markersize=5)
        
        legend_elements.append((bar_proxy, line_proxy))
        name = name_map[algo]
        labels.append(f"{name} (Proposed)" if i == 0 else name)

    fig.legend(legend_elements, labels, loc='lower center', bbox_to_anchor=(0.5, -0.08),
               ncol=3, frameon=False, columnspacing=1.2, handlelength=3.8,
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)})

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.24) 
    
    plt.savefig(CONFIG['save_path'], format='pdf', bbox_inches='tight')
    print(f"成功保存学术图表至: {CONFIG['save_path']}")
    plt.show()

if __name__ == "__main__":
    if os.path.exists(CONFIG['input_data']):
        print(f"直接加载数据文件: '{CONFIG['input_data']}'")
        bar_data, line_data = load_structures_from_json(CONFIG['input_data'])

        plot_static_combined_bottom_legend(CONFIG['baselines'], CONFIG['name_map'], bar_data, line_data)
    else:
        print(f"致命错误：未找到任何有效数据源 ({CONFIG['input_data']})")