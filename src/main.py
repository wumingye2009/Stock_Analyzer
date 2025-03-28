import sys
from pathlib import Path
from importlib import import_module
from indicators import INDICATOR_REGISTRY  # 绝对路径导入
import pandas as pd
from matplotlib import pyplot as plt

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.resolve()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("project_root:", project_root)  # 调试语句

# ================== 数据准备 ==================
def load_and_preprocess(filename):
    """数据加载与预处理"""
    try:
        df = pd.read_csv(f"{filename}.csv", encoding='utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {filename}.csv 不存在")

    # 日期有效性检查
    date_mask = df['日期'].isna()
    if date_mask.any():
        print(f"发现 {date_mask.sum()} 行无效日期，示例：\n{df[date_mask].head()}")
        df = df[~date_mask]

    return df.set_index('日期')


# ================== 全局配置 ==================
plt.rcParams.update({
    'font.sans-serif': 'Microsoft YaHei',  # 中文字体
    'axes.unicode_minus': False,           # 显示负号
    'figure.dpi': 150                      # 显示分辨率
})


def main():
    # 用户输入
    stock_code = input("请输入股票代码(如:300100): ").strip()
    indicator_name = input("请选择指标（当前支持：薛斯通道）: ").strip()
    N = int(input("输入N值(默认50): ") or 50)
    M = int(input("输入M值(默认10): ") or 10)

    # 加载数据
    filename = 'data/300100_双林股份_historical_data'
    filepath = project_root / filename
    df = load_and_preprocess(filepath)

    # 指标计算
    if indicator_name not in INDICATOR_REGISTRY:
        print(f"错误：指标 '{indicator_name}' 不存在")
        print("支持指标：", ", ".join(INDICATOR_REGISTRY.keys()))
        return

    IndicatorClass = INDICATOR_REGISTRY[indicator_name]
    df = IndicatorClass.calculate(df, N=N, M=M)
    print(df.head())

    # ========== 可视化 ==========
    plt.figure(figsize=(16, 10))

    # 价格图
    ax1 = plt.subplot(2, 1, 1, title=f"{stock_code} 技术分析")
    ax1.plot(df.index, df['收盘'], label='收盘价', lw=2.5, color='black')

    # 颜色映射
    color_map = {
        '静态支撑带': 'green',
        '静态压力带': 'red',
        '动态趋势上轨': 'blue',
        '动态趋势下轨': 'purple'
    }

    # 动态添加指标线
    for col, color in color_map.items():
        if col in df.columns:
            ax1.plot(df.index, df[col], lw=1.5, linestyle='--', color=color, label=col)

    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # ADX趋势图（示例）
    ax2 = plt.subplot(2, 1, 2, title="ADX趋势强度")
    if 'ADX' in df.columns:
        ax2.fill_between(df.index, df['ADX'], color='skyblue', alpha=0.4)
        ax2.axhline(25, color='gray', linestyle='--')
        ax2.axhline(75, color='gray', linestyle='--')
        ax2.set_ylabel('ADX值')
    else:
        ax2.text(0.5, 0.5, "未选择ADX指标", ha='center', va='center', fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
