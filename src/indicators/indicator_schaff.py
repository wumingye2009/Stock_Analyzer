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

        
        df['AA'] = weight_avg_series.rolling(
            window=self.window,
            min_periods=1
            ).mean()          # df['AA'] 是 pandas.Series
        df['AA'].bfill(inplace=True)                                                      # 避免 NaN 影响
        # print(df['AA'].head(10))
        
        # 计算 CC（波动率）
        df['CC'] = TechnicalBase.volatility(df, window=20).squeeze()
        print(df['CC'].head(10))
        # df['CC'] 是 pandas.Series


        # 计算 DD（动态移动均线）   df['DD'] 是 pandas.Series
        df['DD'] = TechnicalBase.dynamic_ma(df['AA'], alpha_series=df['CC'])


        # 计算通道
        df['静态支撑带'] = df['AA'] * self.N / 100
        df['静态压力带'] = df['AA'] * (200 - self.N) / 100
        df['动态趋势上轨'] = (1 + self.M/100) * df['DD']
        df['动态趋势下轨'] = (1 - self.M/100) * df['DD']
        
        # 确保返回仅包含所需的 4 列
        # return df[['静态支撑带', '静态压力带', '动态趋势上轨', '动态趋势下轨']]
        return df