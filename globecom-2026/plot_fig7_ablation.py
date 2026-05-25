import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
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
# 2. 全局绘图参数、文本配置、视觉样式与标签映射字典
# NOTE: 使用者只需在此处修改文字或调整位置
# =========================================================================
CONFIG = {
    # 基础输出与解耦中介配置
    'save_path': 'figures/fig7.pdf',
    'fig_size': (7.2, 3.5),
    'input_data': 'data/fig7_data.json',

    # 实验信息
    'algorithm': 'mobiu_mac',
    'topology_trend': ['full_argo', 'w_ER_5K'],

    # 学术标签显示文本映射 (Latex 格式)
    'label_name': {
        'mobiu_mac': 'MobiU-MAC (Full)',
        'case1_2_fixed_stats.csv': 'MobiU-MAC (Full)',
        'case1_2_fixed_abla_stats.csv': r'$\text{w/ ER}_{5K}$',
        'ablation_20260401_2': r'$\text{w/o IS}$',
        'ablation_20260401_4': r'$\text{w/o } \{\text{IS}, \lambda\}$',
        'ablation_20260401_5': r'$\text{w/o MSR}$',
        'ablation_20260401_6_2024': r'$\text{w/ ER}_{1K}$',
        'ablation_20260401_6_10240': r'$\text{w/ ER}_{5K}$',
        'ablation_20260401_7': r'$\text{DQN}$',
    },

    # 视觉渲染样式控制
    'bar_style': {
        'color': '#B0E2FF',
        'acolor': '#C00000',
        'width': 0.5
    },
    'line_styles': [
        {'color': '#003399', 'marker': 'o', 'linestyle': '-', 'linewidth': 2.2, 'markersize': 5, 'zorder': 2},
        {'color': '#FF4500', 'marker': 'v', 'linestyle': '--', 'linewidth': 1.5, 'markersize': 4, 'zorder': 1}
    ],

    # (a) 左图：消融子图环境设置
    'left_graph': {
        'title': '(a) Component ablation analysis',
        'ylabel': 'Norm. Performance',
        'ylim': (0, 1.1),
        'rotation': 35
    },
    
    # (b) 右图：动态双轴子图环境设置
    'right_graph': {
        'title': '(b) Mobility adaptation: STER vs. ER',
        'xlabel': r'Time Slot ($\times 10^4$)',
        'ylabel_left': 'Running Avg. Throughput',
        'ylabel_right': r'$D(t) \text{ [slots]}$',
        'xlim': (0, 50000),
        'ylim_left': (0, 1.1),
        'ylim_right': (0, 6),
        'xticks': [0, 10000, 20000, 30000, 40000, 50000],
        'xticklabels': ['0', '1', '2', '3', '4', '5'],
        'yticks_right': [1, 2, 3, 4, 5]
    }
}

# =========================================================================
# 3. 读入绘图数据
# =========================================================================
def load_structures_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    ablation_data = payload['ablation_data']
    
    trend_data = {}
    for key, data in payload['trend_data'].items():
        trend_data[key] = {
            'step': np.array(data['step']),
            'mean': np.array(data['mean']),
            'std': np.array(data['std'])
        }
        
    delay_data = {
        'step': np.array(payload['delay_data']['step']),
        'delay': np.array(payload['delay_data']['delay'])
    }
    return ablation_data, trend_data, delay_data


# =========================================================================
# 4. 图形绘制核心
# =========================================================================
def plot_ablation_results(ablation_data, trend_data, delay_data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=CONFIG['fig_size'])
    
    cfg_a = CONFIG['left_graph']
    cfg_b = CONFIG['right_graph']

    # ==========================================
    # (a) 左图：消融柱状对比图绘制
    # ==========================================
    ablation_labels = [item['label'] for item in ablation_data]
    final_means = [item['mean'] for item in ablation_data]
    final_stds = [item['std'] for item in ablation_data]
    x_pos = np.arange(len(ablation_labels))
    
    ax1.bar(x_pos, final_means, yerr=final_stds, align='center', 
            color=CONFIG['bar_style']['color'], width=CONFIG['bar_style']['width'], 
            edgecolor='black', linewidth=0.8, ecolor='0.5', capsize=2, 
            error_kw={'elinewidth': 1.0})

    # 绘制水平性能红线基准线
    ax1.axhline(y=1.0, color=CONFIG['bar_style']['acolor'], linestyle='--', linewidth=1.5, zorder=3)

    ax1.set_ylabel(cfg_a['ylabel'])
    ax1.set_ylim(cfg_a['ylim'])
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(ablation_labels, rotation=cfg_a['rotation'], ha='right', fontsize=11, rotation_mode='anchor') 
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_title(cfg_a['title'], pad=10)

    # ==========================================
    # (b) 右图：多轴联动曲线（左轴：收敛折线，右轴：阶跃时延）
    # ==========================================
    for i, trend_case in enumerate(CONFIG['topology_trend']):
        if trend_case in trend_data:
            steps = trend_data[trend_case]['step']
            means = trend_data[trend_case]['mean']
            stds  = trend_data[trend_case]['std']
            
            if len(steps) > 0:
                st = CONFIG['line_styles'][i]
                line, = ax2.plot(steps, means, color=st['color'], 
                                 linestyle=st['linestyle'], linewidth=st['linewidth'],
                                 marker=st['marker'], markevery=5000, markersize=5,
                                 zorder=st['zorder'])
                ax2.fill_between(steps, means - stds, means + stds, 
                                 color=line.get_color(), alpha=0.1, zorder=st['zorder'])

    ax2.set_xlim(cfg_b['xlim'])
    ax2.set_ylim(cfg_b['ylim_left'])
    ax2.set_xticks(cfg_b['xticks'])
    ax2.set_xticklabels(cfg_b['xticklabels'])
    ax2.set_xlabel(cfg_b['xlabel'], labelpad=5)
    ax2.set_ylabel(cfg_b['ylabel_left'])
    ax2.set_title(cfg_b['title'], pad=10)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)

    # 激活并挂载右侧的独立延迟轴
    ax_delay = ax2.twinx()
    if len(delay_data['step']) > 0:
        ax_delay.step(delay_data['step'], delay_data['delay'], color='#7F7F7F', 
                      linestyle='-', linewidth=1.0, alpha=0.4, where='post', zorder=0)

    ax_delay.set_ylabel(cfg_b['ylabel_right'], color='#7F7F7F')
    ax_delay.set_ylim(cfg_b['ylim_right'])
    ax_delay.set_yticks(cfg_b['yticks_right'])
    ax_delay.tick_params(axis='y', labelcolor='#7F7F7F')
    ax_delay.grid(False) # 避免右轴网格干扰主网格

    # ==========================================
    # 复合图例设置
    # ==========================================
    p_full_a = Line2D([0], [0], color=CONFIG['bar_style']['acolor'], linestyle='--', linewidth=1.5)
    p_full_b = Line2D([0], [0], color=CONFIG['line_styles'][0]['color'], linestyle='-', linewidth=2.2, marker='o', markersize=5)
    p_variants = Patch(facecolor=CONFIG['bar_style']['color'], edgecolor='black', linewidth=0.8)
    p_er5m = Line2D([0], [0], color=CONFIG['line_styles'][1]['color'], linestyle='--', linewidth=1.5, marker='v', markersize=4)
    p_delay = Line2D([0], [0], color='#7F7F7F', linestyle='-', linewidth=1.5, alpha=0.6)

    # 依靠元组 (p_full_a, p_full_b) 将左图红虚线基准与右图蓝折线进行梦幻图例组合绑定
    handles = [(p_full_a, p_full_b), p_variants, p_er5m, p_delay]
    labels = [CONFIG['label_name'][CONFIG['algorithm']], 'Ablated Variants', CONFIG['label_name']['case1_2_fixed_abla_stats.csv'], '$D(t)$']
    
    fig.legend(handles=handles, labels=labels,
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0.5)}, 
               loc='lower center', bbox_to_anchor=(0.5, -0.05), 
               ncol=4, frameon=False, columnspacing=2.0, handlelength=3.0)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.24) 
    
    plt.savefig(CONFIG['save_path'], format='pdf', bbox_inches='tight')
    png_path = CONFIG['save_path'].rsplit('.', 1)[0] + '.png'
    plt.savefig(png_path, format='png', bbox_inches='tight')
    print(f"成功保存学术图表至: {CONFIG['save_path']}, {png_path}")
    plt.show()

if __name__ == "__main__":
    if os.path.exists(CONFIG['input_data']):
        print(f"直接加载数据文件: '{CONFIG['input_data']}'")
        ablation_data, trend_data, delay_data = load_structures_from_json(CONFIG['input_data'])
        
        # 移交至纯粹的图形渲染模块
        plot_ablation_results(ablation_data, trend_data, delay_data)
    else:
        print(f"致命错误：未找到有效的数据源文件 {CONFIG['input_data']}")