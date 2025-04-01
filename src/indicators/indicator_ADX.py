# src/indicators/adx.py
import pandas as pd
from src.indicators.technical import TechnicalIndicator  # 导入基类


class ADX(TechnicalIndicator):
    INDICATOR_NAME = "ADX"
    
    def __init__(self, window=14):
        self.window = window
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        # ADX具体实现
        delta = df['收盘'].diff()
        gain = delta.clip(lower=0).rolling(self.window).mean()
        loss = -delta.clip(upper=0).rolling(self.window).mean()
        rs = gain / loss
        adx = 100 - (100 / (1 + rs))
        df['ADX'] = adx.round(2)
        return df