from .technical import TechnicalIndicator
import pandas as pd

class MACD(TechnicalIndicator):
    INDICATOR_NAME = "MACD"
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        close = df['收盘']
        
        # 计算EMA
        ema_fast = close.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow_period, adjust=False).mean()
        
        # 计算MACD线和信号线
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()
        
        # 计算MACD柱状图
        hist = macd - signal
        
        # 保存结果
        df['MACD'] = macd
        df['Signal'] = signal
        df['Hist'] = hist
        
        return df
