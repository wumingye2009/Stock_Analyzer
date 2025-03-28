# src/indicators/adx.py
from abc import ABC, abstractmethod
import pandas as pd

class TechnicalIndicator(ABC):
    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class ADX(TechnicalIndicator):
    def __init__(self, params):
        self.window = params.get('window', 14)
        self.over_bought = params.get('over_bought', 70)
        self.over_sold = params.get('over_sold', 30)
        
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        # ADX计算逻辑（示例代码）
        delta = df['收盘价'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.window).mean()
        rs = gain / loss
        adx = 100 - (100 / (1 + rs))
        df['ADX'] = adx
        return df