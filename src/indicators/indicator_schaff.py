# src/indicators/indicator_schaff.py
from .technical import TechnicalBase
from .technical import TechnicalIndicator  # 确保继承正确
import pandas as pd

class SchaffChannel(TechnicalIndicator):
    INDICATOR_NAME = "薛斯通道"  # 必须属性

    def __init__(self, N=50, M=10, window=5):
        self.N = N 
        self.M = M
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """薛斯通道计算"""
        df = df.copy()
        
        # 计算 AA（加权均价）
        weight_avg_series = TechnicalBase.weighted_price(df)

        
        df['AA'] = weight_avg_series.rolling(window=self.window,min_periods=1).mean()                                # df['AA'] 是 pandas.Series
        df['AA'].bfill(inplace=True)                # 避免 NaN 影响
        # print(df['AA'].head(10))
        
        # 计算 CC（波动率）
        df['CC'] = TechnicalBase.volatility(df, window=20).squeeze()        # df['CC'] 是 pandas.Series        
        """ 
        .squeeze() 是 Pandas 的方法，用于去除维度为 1 的轴（行或列）。它适用于 DataFrame 和 Series：
        如果 .squeeze() 作用于 DataFrame，且 DataFrame 只有一列或一行，它会转换为 Series。
        如果 .squeeze() 作用于 Series，它不会有任何效果（不会出错）。
        print(df['CC'].head(10))
        """


        # 计算 DD（动态移动均线）   df['DD'] 是 pandas.Series
        df['DD'] = TechnicalBase.dynamic_ma(df['AA'], alpha_series=df['CC'])


        # 计算ATR（Average True Range）作为通道宽度基数
        df['ATR'] = TechnicalBase.average_true_range(df, self.window)
        
        # 计算静态通道
        # 使用布林带原理计算静态通道，更准确地反映价格波动范围
        rolling_window = 20  # 滚动窗口大小
        rolling_mean = df['AA'].rolling(window=rolling_window, min_periods=1).mean()
        rolling_std = df['AA'].rolling(window=rolling_window, min_periods=1).std()
        
        # 设置静态通道为均线上下一定倍数的标准差
        df['静态支撑带'] = rolling_mean - self.N / 100 * rolling_std
        df['静态压力带'] = rolling_mean + self.N / 100 * rolling_std
        
        # 使用ATR作为动态通道宽度
        channel_width = self.M * df['ATR']
        df['动态趋势上轨'] = df['DD'] + channel_width
        df['动态趋势下轨'] = df['DD'] - channel_width
        
        # 确保返回仅包含所需的 4 列
        # return df[['静态支撑带', '静态压力带', '动态趋势上轨', '动态趋势下轨']]
        return df
