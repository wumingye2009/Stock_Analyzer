import akshare as ak
import pandas as pd
import re
from pathlib import Path
from typing import List

def clean_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', name.strip())

class StockDataDownloader:
    def __init__(self, symbols: List[str], start_date: str, end_date: str):
        """
        :param symbols: 股票代码列表
        :param start_date: 起始日期 (YYYYMMDD)
        :param end_date: 结束日期 (YYYYMMDD)
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data_dir = Path("data")

    def download_data(self) -> None:
        """批量下载股票历史数据"""
        for symbol in self.symbols:
            try:
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                stock_name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
                
                cleaned_name = clean_filename(stock_name)
                filename = f"{symbol}_{cleaned_name}_historical_data.csv"
                filepath = self.data_dir / filename

                # 下载数据（使用前复权）
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=self.start_date,
                    end_date=self.end_date,
                    adjust="qfq"
                )
                
                df.to_csv(filepath, index=False, encoding="utf_8_sig")
                print(f"✅ 成功保存: {filepath}")
                
            except Exception as e:
                print(f"❌ 下载失败 {symbol}: {str(e)}")

# 配置示例
if __name__ == "__main__":
    config = {
        "symbols": ["300100", "300378", "300738", "600276", "688185"],
        "start_date": "20240101",
        "end_date": "20250314"
    }
    downloader = StockDataDownloader(**config)
    downloader.download_data()