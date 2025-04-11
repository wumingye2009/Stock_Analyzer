import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
import numpy as np

def plot_macd(df, stock_code):
    """绘制MACD指标图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
    
    # 将索引转换为datetime
    print("转换前日期示例:", df.index[:5])
    df.index = pd.to_datetime(df.index)
    print("转换后日期示例:", df.index[:5])
    
    # 将日期转换为matplotlib格式
    dates = mdates.date2num(df.index.to_pydatetime())
    
    # 绘制K线图
    ax1.plot(dates, df['收盘'], label='收盘价', color='blue')
    ax1.set_title(f'{stock_code} MACD指标')
    ax1.set_ylabel('价格')
    ax1.legend()
    # 设置x轴范围
    ax1.set_xlim(dates[0], dates[-1])
    
    # 绘制MACD指标
    ax2.plot(df.index, df['MACD'], label='MACD', color='blue')
    ax2.plot(df.index, df['Signal'], label='Signal', color='orange')
    ax2.bar(df.index, df['Hist'], label='Histogram', color=np.where(df['Hist'] >= 0, 'green', 'red'))
    ax2.set_ylabel('MACD')
    ax2.legend()
    
    # 将索引转换为datetime
    print("转换前日期示例:", df.index[:5])
    df.index = pd.to_datetime(df.index)
    print("转换后日期示例:", df.index[:5])
    
    # 格式化x轴
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # 根据数据时间跨度自动调整刻度间隔
        date_range = (df.index[-1] - df.index[0]).days
        if date_range <= 30:  # 小于1个月，按天显示
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, date_range//7)))
        elif date_range <= 365:  # 小于1年，按月显示
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        else:  # 大于1年，按季度显示
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
