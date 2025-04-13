import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import akshare as ak
from matplotlib import pyplot as plt
from indicators import register_all_indicators, INDICATOR_REGISTRY
from visualization.Plot_Schaffchannel import plot_xuess_channel
from visualization.polt_adx import plot_adx
from visualization.plot_macd import plot_macd
from data_processing.data_downloader import StockDataDownloader, get_stock_type, clean_filename

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_latest_trading_day() -> str:
    """获取最近一个交易日"""
    today = datetime.now()
    if today.weekday() >= 5:  # 周末
        return (today - timedelta(days=today.weekday()-4)).strftime('%Y%m%d')
    return today.strftime('%Y%m%d')

def check_data_update_needed(filepath: Path) -> bool:
    """检查数据是否需要更新"""
    if not filepath.exists():
        return True
    
    df = pd.read_csv(filepath)
    last_date = pd.to_datetime(df['日期'].iloc[-1])
    latest_trading_day = pd.to_datetime(get_latest_trading_day())
    
    return last_date < latest_trading_day

def load_and_preprocess(filepath: Path):
    """数据加载与预处理"""
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {filepath} 不存在")

    # 日期有效性检查
    date_mask = df['日期'].isna()
    if date_mask.any():
        print(f"发现 {date_mask.sum()} 行无效日期，示例：\n{df[date_mask].head()}")
        df = df[~date_mask]

    return df.set_index('日期')

def main():
    # 用户输入股票代码
    stock_code = input("请输入股票代码(如:300100): ").strip()
    
    # 数据下载与更新
    start_date = "20240101"
    end_date = get_latest_trading_day()
    downloader = StockDataDownloader(stock_code, start_date, end_date)
    
    # 检查并更新数据
    # 获取股票名称用于生成文件名
    stock_info = ak.stock_individual_info_em(symbol=stock_code)
    stock_name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
    cleaned_name = clean_filename(stock_name)
    data_file = downloader.data_dir / f"{stock_code}_{cleaned_name}_his_{end_date}.csv"
    if not data_file.exists():
        print(f"数据未找到，开始下载...")
    elif check_data_update_needed(data_file):
        print(f"数据需要更新，最后交易日：{pd.read_csv(data_file)['日期'].iloc[-1]}")
    else:
        print(f"数据已是最新，无需更新")
    
    # 下载或更新数据
    downloader.download_data()

    # 指标选择
    print("\n请选择指标：")
    print("1 - 薛斯通道")
    print("2 - ADX")
    print("3 - MACD")
    indicator_choice = input("请输入指标编号: ").strip()

    if indicator_choice == "1":
        indicator_name = "薛斯通道"
        N = int(input("输入N值(默认50): ") or 50)
        M = int(input("输入M值(默认10): ") or 10)
        params = {"N": N, "M": M}
    elif indicator_choice == "2":
        indicator_name = "ADX"
        params = {}
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
    df = load_and_preprocess(data_file)

    # 指标计算
    if indicator_name not in INDICATOR_REGISTRY:
        print(f"错误：指标 '{indicator_name}' 不存在")
        print("支持指标：", ", ".join(INDICATOR_REGISTRY.keys()))
        return

    IndicatorClass = INDICATOR_REGISTRY[indicator_name]
    indicator_instance = IndicatorClass.create(**params)
    df = indicator_instance.calculate(df)

    # 可视化
    if indicator_choice == "1":
        plot_xuess_channel(df, stock_code)
    elif indicator_choice == "2":
        plot_adx(df, stock_code)
    elif indicator_choice == "3":
        plot_macd(df, stock_code)

if __name__ == "__main__":
    main()
