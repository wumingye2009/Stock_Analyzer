import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
import numpy as np

def plot_macd(df, stock_code):
    """绘制MACD指标图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
    
    # 绘制K线图
    ax1.plot(df.index, df['收盘'], label='收盘价', color='blue')
    ax1.set_title(f'{stock_code} MACD指标')
    ax1.set_ylabel('价格')
    ax1.legend()
    
    # 绘制MACD指标
    ax2.plot(df.index, df['MACD'], label='MACD', color='blue')
    ax2.plot(df.index, df['Signal'], label='Signal', color='orange')
    ax2.bar(df.index, df['Hist'], label='Histogram', color=np.where(df['Hist'] >= 0, 'green', 'red'))
    ax2.set_ylabel('MACD')
    ax2.legend()
    
    # 格式化x轴
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
