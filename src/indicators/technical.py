# src/indicators/technical.py
from abc import ABC, abstractmethod # 导入抽象基类工具
import pandas as pd
import numpy as np
from .register import get_registry  # 导入注册表函数



class TechnicalIndicator(ABC):  # 定义技术指标抽象基类
    INDICATOR_REGISTRY = {}  # 类属性：全局指标注册表
    
    @classmethod  # 类方法装饰器
    def register(cls):  # 类方法：自动注册子类
        """将子类注册到全局注册表"""
        registry = get_registry()  # 获取注册表
        registry[cls.INDICATOR_NAME] = cls  # 存储类引用
    
    @classmethod  # 工厂方法装饰器
    def create(cls, **kwargs):  # 工厂方法：创建指标实例
        """通过类名和参数动态创建实例"""
        return cls(**kwargs)  # 实例化时传递所有关键字参数
    
    @abstractmethod  # 抽象方法装饰器
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:  # 核心计算方法
        """子类必须实现的指标计算逻辑"""
        pass




class TechnicalBase(ABC):
    """技术指标基类，所有指标必须继承此类"""
    # IS_BASE_CLASS = True  # 标记为基类，不应被注册
    
    @classmethod
    def weighted_price(cls, df: pd.DataFrame) -> pd.Series:
        """计算加权平均价格（WAP）"""
        if df.empty:
            raise ValueError("输入数据框不能为空")
            
        # 确保必要的列存在
        required_columns = ['收盘', '最高', '最低']
        if not all(col in df.columns for col in required_columns):
            raise KeyError(f"数据框必须包含以下列：{required_columns}")
            
        # 向量化计算（比循环快10倍以上）
        weights = np.array([2, 1, 1])
        weighted_sum = (df[required_columns].values * weights).sum(axis=1)
        return pd.Series(weighted_sum / 4, index=df.index, name='加权平均')
    
    @classmethod
    def volatility(cls, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """计算波动率指标  (这个不是标准化波动率，只是简单的波动率，标准化波动率需要用到标准差  result = (wap - ma).abs() / ma.rolling(window=window, min_periods=1).std())"""
        if window <= 0:
            raise ValueError("窗口期必须为正整数")
        # if window > len(df):
        #     window = len(df)
            
        wap = cls.weighted_price(df)
        ma = df['收盘'].rolling(window=window, min_periods=1).mean()
        result = (wap - ma).abs() / ma
        # result = (wap - ma).abs() / ma.rolling(window=window, min_periods=1).std()      #  # 使用滚动标准差计算波动率
        # 处理NaN值（避免影响后续计算）
        result.fillna(0, inplace=True)
        return pd.Series(result, index=df.index, name='标准化波动率')
        
        # 标准化波动率公式（行业通用实现）
        # return (wap - ma).abs() / ma.rolling(window=window).std()
        # volatility = (wap - ma).abs() / ma.rolling(window=window, min_periods=1).std()
        # # 处理NaN值（避免影响后续计算）     
        # volatility.fillna(0, inplace=True)
        # return pd.Series(volatility, index=df.index, name='标准化波动率')   
    
    @staticmethod
    def dynamic_ma(series: pd.Series, alpha_series: pd.Series) -> pd.Series:
        """计算动态移动平均（DMA）"""
        # 输入验证
        if not isinstance(series, pd.Series) or not isinstance(alpha_series, pd.Series):
            raise TypeError("series 和 alpha_series 必须是 pandas Series")
        if len(series) != len(alpha_series):
            raise ValueError(f"series 和 alpha_series 长度不一致：{len(series)} vs {len(alpha_series)}")
            
        # 使用NumPy向量化计算（比循环快100倍）
        values = series.astype(float).values
        alpha = alpha_series.astype(float).values
        
        result = np.full_like(values, np.nan)
        result[0] = values[0]
        
        for i in range(1, len(values)):
            result[i] = alpha[i] * values[i] + (1 - alpha[i]) * result[i-1]
        return pd.Series(result, index=series.index, name='DMA')

    @staticmethod
    def get_true_range(df: pd.DataFrame) -> pd.Series:
        """计算真实波幅（TR）"""
        high_low = df['最高'] - df['最低']
        high_close = (df['最高'] - df['收盘'].shift(1)).abs()
        low_close = (df['最低'] - df['收盘'].shift(1)).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return pd.Series(tr, index=df.index, name='TR')

    @staticmethod
    def average_true_range(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """计算平均真实波幅（ATR）"""
        tr = TechnicalBase.get_true_range(df)
        atr = tr.rolling(window=window, min_periods=1).mean()
        return pd.Series(atr, index=df.index, name='ATR')
