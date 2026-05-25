import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

# =========================================================================
# 1. 全局样式与论文规范设置 (IEEE 会议论文优化)
# NOTE: 使用者通常无需修改此处，除非需要调整整体风格，Linux 或 Mac 用户可能需要安装 Times New Roman 字体以确保兼容性
# =========================================================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['legend.fontsize'] = 14

# =========================================================================
# 2. 全局绘图参数、子图缩放、及高级箭头标注配置
# NOTE: 使用者只需在此处修改文字或调整位置
# =========================================================================
CONFIG = {
    # 基础输出与解耦媒介配置
    'save_path': 'figures/fig6.pdf',
    'fig_size': (6, 3.5),
    'input_data': 'data/fig6_data.json',
    'baseline': 'mobiu_mac',

    # 实验 Case 标识与标签映射定义
    'cases': {
        'h9': 'case3_d4_h9',
        'h11': 'case3_d4_h11',
        'h15': 'case3_d4_h15'
    },
    'styles': {
        'h9': {'color': '#003399', 'label': r'$\hat{H}=9$', 'linestyle': '-', 'linewidth': 1.5, 'alpha': 1.0},
        'h11': {'color': '#228B22', 'label': r'$\hat{H}=11$', 'linestyle': '--', 'linewidth': 1.5, 'alpha': 0.7},
        'h15': {'color': '#C00000', 'label': r'$\hat{H}=15$', 'linestyle': '-.', 'linewidth': 1.5, 'alpha': 1.0},
    },

    # 主图坐标轴
    'main_graph': {
        'xlabel': r'Time Slot ($\times 10^4$)',
        'ylabel': 'Running Avg. Throughput',
        'xlim': (0, 50000),
        'ylim': (0, 1.1),
        'xticks': [0, 10000, 20000, 30000, 40000, 50000],
        'xticklabels': ['0', '1', '2', '3', '4', '5']
    },

    # 局部放大图 (Inset Axes) 配置区
    'inset_graph': {
        'bounds': [0.45, 0.1, 0.36, 0.42],  # [x0, y0, width, height] 相对比例位置
        'xlim': (0, 10000),                  # 局部的横坐标放大范围
        'ylim': (0.4, 0.8),                  # 局部的纵坐标放大范围
        'xticks': [0, 5000, 10000],
        'xticklabels': ['0', '0.5', '1']
    },

    # 图面交互型弯曲箭头与核心学术论点标注
    'annotations': [
        {
            'text': r'$\hat{H}=2D_{\max}+1$',
            'xy': (26500, 0.4),
            'xytext': (11500, 0.45),
            'style_key': 'h9',  # 绑定 h9 的线条色彩
            'rad': .2
        },
        {
            'text': 'Large $\hat{H}$,\nhigh variance',
            'xy': (37000, 0.37),
            'xytext': (40800, 0.15),
            'style_key': 'h15', # 绑定 h15 的线条色彩
            'rad': .2
        }
    ]
}

# =========================================================================
# 3. 读入绘图数据
# =========================================================================
def load_structures_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    trend_data = {}
    for key, data in payload.items():
        trend_data[key] = {
            'step': np.array(data['step']),
            'mean': np.array(data['mean']),
            'std': np.array(data['std'])
        }
    return trend_data


# =========================================================================
# 4. 图形绘制核心
# =========================================================================
def plot_throughput(trend_data):
    fig, ax = plt.subplots(figsize=CONFIG['fig_size'])

    # 动态生成局部放大图 (Inset Axes)
    ins_cfg = CONFIG['inset_graph']
    axins = ax.inset_axes(ins_cfg['bounds'])

    # 遍历各 Case 同步在主图与子图中进行渲染
    for key in CONFIG['cases'].keys():
        steps = trend_data[key]['step']
        mean  = trend_data[key]['mean']
        std   = trend_data[key]['std']
        
        if len(steps) == 0:
            continue
            
        st = CONFIG['styles'][key]
        
        # 渲染主图曲线及方差阴影
        line, = ax.plot(steps, mean, label=st['label'], 
                        color=st['color'], linestyle=st['linestyle'], 
                        linewidth=st['linewidth'], marker='', zorder=3)
        ax.fill_between(steps, mean - std, mean + std, color=line.get_color(), 
                        alpha=st['alpha'] * 0.15, zorder=2)
        
        # 渲染局部放大子图曲线及阴影
        axins.plot(steps, mean, color=st['color'], linestyle=st['linestyle'], 
                   linewidth=st['linewidth'], marker='', zorder=3)
        axins.fill_between(steps, mean - std, mean + std, color=line.get_color(), 
                           alpha=st['alpha'] * 0.15, zorder=2)

    # 动态配置学术论点文本与指向性弯曲箭头
    for ann in CONFIG['annotations']:
        color = CONFIG['styles'][ann['style_key']]['color']
        ax.annotate(ann['text'], xy=ann['xy'], xytext=ann['xytext'],
                    fontsize=11, color=color, fontweight='bold',
                    arrowprops=dict(arrowstyle='<-', connectionstyle=f"arc3,rad={ann['rad']}", 
                                   color=color, lw=1), zorder=10)
    
    # 主图环境细节配置
    main_cfg = CONFIG['main_graph']
    ax.set_xlim(main_cfg['xlim'])
    ax.set_ylim(main_cfg['ylim'])
    ax.set_xticks(main_cfg['xticks'])
    ax.set_xticklabels(main_cfg['xticklabels'])
    ax.set_xlabel(main_cfg['xlabel'], labelpad=8)
    ax.set_ylabel(main_cfg['ylabel'])
    ax.legend(ncol=3, columnspacing=1.2, labelspacing=0.2, handletextpad=0.4, frameon=True)

    # 放大子图环境细节配置
    axins.set_xlim(ins_cfg['xlim'])
    axins.set_ylim(ins_cfg['ylim'])
    axins.set_xticks(ins_cfg['xticks'])
    axins.set_xticklabels(ins_cfg['xticklabels'])
    # 让子图的上下左右四个方向的刻度线都向内生长，表现更内敛精致
    axins.tick_params(axis='both', direction='in', top=True, right=True, labelsize=9)

    # 在主图中添加指示放大区域的矩形框和断续灰色连接线
    mark_inset(ax, axins, loc1=1, loc2=3, fc="none", ec="0.5", lw=1.0, linestyle='--', color='#666666')

    plt.tight_layout()
    plt.savefig(CONFIG['save_path'], format='pdf', bbox_inches='tight')
    png_path = CONFIG['save_path'].rsplit('.', 1)[0] + '.png'
    plt.savefig(png_path, format='png', bbox_inches='tight')
    print(f"成功保存学术图表至: {CONFIG['save_path']}, {png_path}")
    plt.show()

if __name__ == "__main__":
    if os.path.exists(CONFIG['input_data']):
        print(f"直接加载数据文件: '{CONFIG['input_data']}'")
        trend_data = load_structures_from_json(CONFIG['input_data'])

        plot_throughput(trend_data)
    else:
        print(f"致命错误：未找到有效的数据源文件 {CONFIG['input_data']}")