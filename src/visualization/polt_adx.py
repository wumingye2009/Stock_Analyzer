import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_adx(df, stock_code):
    """ADX趋势强度可视化"""
    plt.figure(figsize=(16, 8))

    # 将索引转换为datetime
    df.index = pd.to_datetime(df.index)
    
    # 将日期转换为matplotlib格式
    dates = mdates.date2num(df.index.to_pydatetime())

    ax = plt.subplot(1, 1, 1, title=f"{stock_code} ADX趋势强度")
    if 'ADX' in df.columns:
        ax.fill_between(dates, df['ADX'], color='skyblue', alpha=0.4)
        # 设置x轴范围和格式化
        ax.set_xlim(dates[0], dates[-1])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # 根据数据时间跨度自动调整刻度间隔
        date_range = (df.index[-1] - df.index[0]).days
        if date_range <= 30:  # 小于1个月，按天显示
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, date_range//7)))
        elif date_range <= 365:  # 小于1年，按月显示
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        else:  # 大于1年，按季度显示
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        # 使用转换后的日期范围绘制水平线
        ax.hlines(25, dates[0], dates[-1], color='gray', linestyle='--')
        ax.hlines(75, dates[0], dates[-1], color='gray', linestyle='--')
        ax.set_ylabel('ADX值')
    else:
        # 使用转换后的日期范围定位文本
        mid_date = dates[len(dates)//2]
        ax.text(mid_date, 0.5, "未选择ADX指标", ha='center', va='center', fontsize=12)

    plt.tight_layout()
    plt.show()
