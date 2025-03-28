from .technical import TechnicalBase
import pandas as pd

class SchaffChannel(TechnicalBase):
    INDICATOR_NAME = "薛斯通道"  # 必须属性

    @classmethod
    def calculate(cls, df, N=50, M=10, window=5):
        """薛斯通道计算"""
        df = df.copy()
        
        # 计算 AA（加权均价）
        # weight_avg_df = cls.weighted_price(df)  
        # weight_avg_series = weight_avg_df['加权平均'].reset_index(drop=True)
        # weight_avg_series = weight_avg_df['加权平均']
        weight_avg_series = cls.weighted_price(df)

        
        df['AA'] = weight_avg_series.rolling(window=window,min_periods=1).mean()          # df['AA'] 是 pandas.Series
        df['AA'].bfill(inplace=True)                                                      # 避免 NaN 影响
        # print(df['AA'].head(10))
        
        # 计算 CC（波动率）
        # df['CC'] = cls.volatility(df, window=20).squeeze().reset_index(drop=True)         # df['CC'] 是 pandas.Series
        # df['CC'].bfill(inplace=True)                                                      # 避免 NaN 影响
        df['CC'] = cls.volatility(df, window=20).squeeze()
        # print(df['CC'].head(10))

        print(df['AA'].head())
        print(df['CC'].head())
        print(type(df['CC']))

        # 计算 DD（动态移动均线）                                                       df['DD'] 是 pandas.Series
        df['DD'] = cls.dynamic_ma(df['AA'], alpha_series=df['CC'])


        # 计算通道
        df['静态支撑带'] = df['AA'] * N / 100
        df['静态压力带'] = df['AA'] * (200 - N) / 100
        df['动态趋势上轨'] = (1 + M/100) * df['DD']
        df['动态趋势下轨'] = (1 - M/100) * df['DD']
        
        # 确保返回仅包含所需的 4 列
        # return df[['静态支撑带', '静态压力带', '动态趋势上轨', '动态趋势下轨']]
        return df