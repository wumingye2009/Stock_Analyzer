import pandas as pd
from pandas import Series
import numpy as np

class TechnicalBase:
    """基础技术指标基类"""
  
    INDICATOR_NAME = None  # 子类必须定义
    
    @classmethod
    def weighted_price(cls,df):
        """计算加权平均价格"""
        weights = np.array([2, 1, 1])
        weighted_sum=(df[['收盘', '最高', '最低']].values * weights).sum(axis=1) / 4
        # df[['收盘', '最高', '最低']].values：将 DataFrame 转换为 NumPy 数组（形状为 (n_rows, 3)）。
        # .values * weights：逐元素乘法（形状不变）。
        # .sum(axis=1)：按行求和（结果形状为 (n_rows, 1)）。
        # / 4：最终结果形状为 (n_rows,) 的一维数组。
        # return pd.DataFrame({'加权平均':weighted_sum})
        return pd.Series(weighted_sum, index=df.index, name='加权平均')


  
    @classmethod
    def volatility(cls,df, window=20):
        """波动率指标"""
        if window > len(df):
            window = len(df)
        ma = df['收盘'].rolling(window=window,min_periods=1).mean().astype(float)
        # weighted_avg = cls.weighted_price(df)['加权平均'].astype(float)
        # return (weighted_avg - ma).abs() / ma
        print(ma.head())
        result = (cls.weighted_price(df) - ma).abs() / ma
        # print(type(result))
        print(result.head())
        return result
    @classmethod
    def dynamic_ma(cls, series, alpha_series, adjust=False):

        """
        计算动态移动平均
        series: pd.Series (n_samples,)  # 价格数据
        alpha_series: pd.Series (n_samples,)  # 平滑参数
        """
        if not isinstance(series, pd.Series):
            raise ValueError("series 必须是 pandas Series")
        if not isinstance(alpha_series, pd.Series):
            raise ValueError("alpha_series 必须是 pandas Series")
        if len(series) != len(alpha_series):
            raise ValueError(f"series 和 alpha_series 长度必须一致 ({len(series)} vs {len(alpha_series)})")

        # 转换为 NumPy 数组
        values = series.astype(float).values
        alpha = alpha_series.astype(float).values

        # 计算动态移动平均
        result = np.zeros_like(values)

        # 计算第一个值
        result[0] = values[0]

        # 递归计算移动均线
        for i in range(1, len(values)):
            result[i] = alpha[i] * values[i] + (1 - alpha[i]) * result[i - 1]

        return pd.Series(result, index=series.index)  # 直接使用 series.index 保持一致

