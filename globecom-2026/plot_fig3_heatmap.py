import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns

'''
NOTE: 均值与CV热力图均采用了非等距的渐变颜色映射（LinearSegmentedColormap），目的
在于大幅提升高目标值区间的视觉分辨率，以精准捕获理论相变边界。所以使用时必须保持颜色
条（Colorbar）可见，且必须开启格子数值标注（annot=True），以确保数据完全透明。
'''

# =========================================================================
# 1. 全局样式与论文规范设置 (IEEE 会议论文优化)
# NOTE: 使用者通常无需修改此处，除非需要调整整体风格，Linux 或 Mac 用户可能需要安装 Times New Roman 字体以确保兼容性
# =========================================================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 18
plt.rcParams['axes.titlesize'] = 20

# =========================================================================
# 2. 全局绘图参数、非等距色带、网格及多画布文本配置
# NOTE: 使用者只需在此处修改文字或调整位置
# =========================================================================
CONFIG = {
    # 基础输出与解耦中介配置
    'save_path': 'fig3.pdf',
    'fig_size': (22, 5),
    'input_data': 'data/fig3_data.json',

    # (a, b) 均值热力图 (Mean Heatmap) 专用色带及非等距配置
    'mean_heatmap': {
        'base_cmap': 'Blues_r',
        'bounds': [0.70, 0.87, 0.885, 0.94, 0.97, 0.985, 1.0],
        'color_depths': [0.0, 0.2, 0.4, 0.5, 0.7, 0.9, 1.0],
        'cbar_label': r'$\text{Mean Equivalence Ratio}$',
        'ticks_count': 7
    },

    # (c, d) 变异系数热力图 (CV Heatmap) 专用色带及非等距配置
    'cv_heatmap': {
        'base_cmap': 'YlOrRd',
        'bounds': [0.0, 0.015, 0.06, 0.07, 0.14],
        'color_depths': [0.0, 0.1, 0.3, 0.6, 1.0],
        'cbar_label': r'$\text{CV (Std/Mean)}$',
        'ticks_count': 8
    }
}

# =========================================================================
# 3. 读入绘图数据
# =========================================================================
def load_structures_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        
    data_dict = {}
    for key, data in payload.items():
        data_dict[key] = {
            'id': data['id'],
            'x_labels': data['x_labels'],
            'y_labels': data['y_labels'],
            'mean': np.array(data['mean']),
            'std': np.array(data['std']),
            'cv': np.array(data['cv'])
        }
    return data_dict


# =========================================================================
# 4. 图形绘制函数
# =========================================================================
def plot_combined_analysis(data_dict):
    fig = plt.figure(figsize=CONFIG['fig_size'])

    # 1. 动态切分布局网格 (1行2列大框架下各嵌套1行2列子图)
    gs_main = fig.add_gridspec(1, 2, wspace=0.2) 
    gs_left = gs_main[0].subgridspec(1, 2, wspace=0.1)
    gs_right = gs_main[1].subgridspec(1, 2, wspace=0.1)

    axes = [
        fig.add_subplot(gs_left[0, 0]),
        fig.add_subplot(gs_left[0, 1]),
        fig.add_subplot(gs_right[0, 0]),
        fig.add_subplot(gs_right[0, 1])
    ]
    
    case_keys = ['case1', 'case3']

    # 2. 从 CONFIG 中动态组装非等距连续色带 A (Mean Heatmap)
    cfg_m = CONFIG['mean_heatmap']
    nodes_m = [(b - cfg_m['bounds'][0]) / (cfg_m['bounds'][-1] - cfg_m['bounds'][0]) for b in cfg_m['bounds']]
    color_list_m = plt.get_cmap(cfg_m['base_cmap'])(cfg_m['color_depths'])
    cmap_mean = colors.LinearSegmentedColormap.from_list('smooth_mean', list(zip(nodes_m, color_list_m)))
    norm_mean = colors.Normalize(vmin=cfg_m['bounds'][0], vmax=cfg_m['bounds'][-1])
    sm_mean = cm.ScalarMappable(cmap=cmap_mean, norm=norm_mean)
    sm_mean.set_array([])

    # 3. 从 CONFIG 中动态组装非等距连续色带 B (CV Heatmap)
    cfg_c = CONFIG['cv_heatmap']
    nodes_cv = [(b - cfg_c['bounds'][0]) / (cfg_c['bounds'][-1] - cfg_c['bounds'][0]) for b in cfg_c['bounds']]
    color_list_cv = plt.get_cmap(cfg_c['base_cmap'])(cfg_c['color_depths'])
    cmap_cv = colors.LinearSegmentedColormap.from_list('smooth_cv', list(zip(nodes_cv, color_list_cv)))
    norm_cv = colors.Normalize(vmin=cfg_c['bounds'][0], vmax=cfg_c['bounds'][-1])
    sm_cv = cm.ScalarMappable(cmap=cmap_cv, norm=norm_cv)
    sm_cv.set_array([])

    # 4. 开始双重矩阵的循环渲染
    for i, key in enumerate(case_keys):
        case_id = data_dict[key]['id']
        x_labs  = data_dict[key]['x_labels']
        y_labs  = data_dict[key]['y_labels']
        
        # --- (a, b) Mean Heatmaps 绘制 ---
        ax_m = axes[i]
        df_m = pd.DataFrame(data_dict[key]['mean'], index=x_labs, columns=y_labs).T.iloc[::-1]
        sns.heatmap(df_m, annot=True, fmt=".3f", cmap=cmap_mean, norm=norm_mean, ax=ax_m, square=True, cbar=False,
                    annot_kws={"size": 11})
        
        rows, cols = df_m.shape
        boundary_line, = ax_m.plot([0, cols], [rows, 0], color='red', lw=2, ls='--', 
                                   label=r'Boundary, $\hat{H} = 2D_{\max} + 1$')
        ax_m.set_title(f"({chr(97+i)}) Case {case_id}: Equivalence Ratio", pad=15)
        ax_m.set_xlabel(r'Horizon $\hat{H}$')
        if i == 0: ax_m.set_ylabel(r'Delay Bound $D_{\max}$')

        # --- (c, d) CV Heatmaps 绘制 ---
        ax_c = axes[i+2]
        df_c = pd.DataFrame(data_dict[key]['cv'], index=x_labs, columns=y_labs).T.iloc[::-1]
        sns.heatmap(df_c, annot=True, fmt=".3f", cmap=cmap_cv, norm=norm_cv, ax=ax_c, square=True, cbar=False,
                    annot_kws={"size": 11})
        ax_c.plot([0, cols], [rows, 0], color='red', lw=2, ls='--')
        ax_c.set_title(f"({chr(99+i)}) Case {case_id}: Performance Stability", pad=15)
        ax_c.set_xlabel(r'Horizon $\hat{H}$')
        if i == 0: ax_c.set_ylabel(r'Delay Bound $D_{\max}$')

    # 5. 挂载 Mean 组侧边颜色条
    divider_m = make_axes_locatable(axes[1])
    cax_m = divider_m.append_axes("right", size="5%", pad=0.2) 
    cbar_m = fig.colorbar(sm_mean, cax=cax_m, fraction=0.046, pad=0.04)
    cbar_m.set_label(cfg_m['cbar_label'], fontsize=18)
    cbar_m.set_ticks(np.linspace(cfg_m['bounds'][0], cfg_m['bounds'][-1], cfg_m['ticks_count'])) 
    cbar_m.ax.tick_params(labelsize=12)
    cbar_m.outline.set_visible(False)

    # 6. 挂载 CV 组侧边颜色条
    divider_c = make_axes_locatable(axes[3])
    cax_c = divider_c.append_axes("right", size="5%", pad=0.2)
    cbar_c = fig.colorbar(sm_cv, cax=cax_c, fraction=0.046, pad=0.04)
    cbar_c.set_label(cfg_c['cbar_label'], fontsize=18)
    cbar_c.set_ticks(np.linspace(cfg_c['bounds'][0], cfg_c['bounds'][-1], cfg_c['ticks_count'])) 
    cbar_c.ax.tick_params(labelsize=12)
    cbar_c.outline.set_visible(False)

    # 7. 全局图例与论文多栏视图间距优化
    fig.legend(handles=[boundary_line], loc='lower center', bbox_to_anchor=(0.5, -0.01), ncol=1, frameon=False)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.18, top=0.9)
    plt.savefig(CONFIG['save_path'], format='pdf', bbox_inches='tight')
    png_path = CONFIG['save_path'].rsplit('.', 1)[0] + '.png'
    plt.savefig(png_path, format='png', bbox_inches='tight')
    print(f"成功保存学术图表至: {CONFIG['save_path']}, {png_path}")
    plt.show()

if __name__ == "__main__":
    if os.path.exists(CONFIG['input_data']):
        print(f"直接加载数据文件: '{CONFIG['input_data']}'")
        data_structures = load_structures_from_json(CONFIG['input_data'])

        plot_combined_analysis(data_structures)
    else:
        print(f"致命错误：未找到任何有效数据源 ({CONFIG['input_data']})")