import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_xuess_channel(df, stock_code):
    """薛斯通道可视化"""
    plt.figure(figsize=(16, 10))

    # 将索引转换为datetime
    df.index = pd.to_datetime(df.index)
    
    # 将日期转换为matplotlib格式
    dates = mdates.date2num(df.index.to_pydatetime())

    # 价格图
    ax1 = plt.subplot(2, 1, 1, title=f"{stock_code} 薛斯通道分析")
    ax1.plot(dates, df['收盘'], label='收盘价', lw=2.5, color='black')
    # 设置x轴范围
    ax1.set_xlim(dates[0], dates[-1])

    # 颜色映射
    color_map = {
        '静态支撑带': 'green',
        '静态压力带': 'red',
        '动态趋势上轨': 'blue',
        '动态趋势下轨': 'purple'
    }

    # 处理NaN值并动态添加指标线
    for col, color in color_map.items():
        if col in df.columns:
            # 前向填充和后向填充NaN值
            df[col] = df[col].ffill().bfill()
            ax1.plot(df.index, df[col], lw=1.5, linestyle='--', color=color, label=col)

    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
