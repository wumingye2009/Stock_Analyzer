import sys
from pathlib import Path
from importlib import import_module
import pandas as pd
from matplotlib import pyplot as plt
from indicators import register_all_indicators, INDICATOR_REGISTRY
print("已注册指标:", list(INDICATOR_REGISTRY.keys()))  # 调试语句
from visualization.Plot_Schaffchannel import plot_xuess_channel
from visualization.polt_adx import plot_adx
from visualization.plot_macd import plot_macd

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.resolve()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


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


# ================== 主程序 ==================

def main():
    # 用户输入
    stock_code = input("请输入股票代码(如:300100): ").strip()
    print("请选择指标：")
    print("1 - 薛斯通道")
    print("2 - ADX")
    print("3 - MACD")
    indicator_choice = input("请输入指标编号: ").strip()

    if indicator_choice == "1":
        indicator_name = "薛斯通道"
        N = int(input("输入N值(默认50): ") or 50)
        M = int(input("输入M值(默认10): ") or 10)
        params = {"N": N, "M": M}  # 将参数打包为字典
    elif indicator_choice == "2":
        indicator_name = "ADX"
        params = {}  # ADX 不需要额外参数
    elif indicator_choice == "3":
        indicator_name = "MACD"
        fast = int(input("输入快线周期(默认12): ") or 12)
        slow = int(input("输入慢线周期(默认26): ") or 26)
        signal = int(input("输入信号线周期(默认9): ") or 9)
        params = {"fast_period": fast, "slow_period": slow, "signal_period": signal}
    else:
        print("无效的选择，请输入1、2或3")
        return

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
   
    # 使用 `create()` 方法实例化对象，并正确传递参数
    indicator_instance = IndicatorClass.create(**params)

    # 计算指标
    df = indicator_instance.calculate(df)

    # ========== 可视化 ==========
    if indicator_choice == "1":
        plot_xuess_channel(df, stock_code)
    elif indicator_choice == "2":
        plot_adx(df, stock_code)
    elif indicator_choice == "3":
        plot_macd(df, stock_code)


if __name__ == "__main__":
    main()
