import akshare as ak
import pandas as pd
import re
from pathlib import Path
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def clean_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', name.strip())

def get_stock_type(symbol: str) -> str:
    """识别股票类型"""
    if symbol.startswith('6'):
        return 'sh'  # 上海A股
    elif symbol.startswith('0') or symbol.startswith('3'):
        return 'sz'  # 深圳A股
    else:
        return 'us'  # 美股

def get_filename(symbol: str, name: str) -> str:
    """生成符合要求的文件名"""
    today = datetime.now().strftime('%Y%m%d')
    stock_type = get_stock_type(symbol)
    
    if stock_type in ['sh', 'sz']:
        return f"{symbol}_{name}_his_{today}.csv"
    else:
        return f"{symbol}_his_{today}.csv"

class StockDataDownloader:
    def __init__(self, symbols: Union[str, List[str]], start_date: str, end_date: str):
        """
        :param symbols: 单个股票代码或股票代码列表
        :param start_date: 起始日期 (YYYYMMDD)
        :param end_date: 结束日期 (YYYYMMDD)
        """
        self.symbols = [symbols] if isinstance(symbols, str) else symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def _download_single(self, symbol: str) -> None:
        """下载单个股票数据"""
        try:
            stock_type = get_stock_type(symbol)
            
            if stock_type == 'us':
                # 美股数据下载
                df = ak.stock_us_daily(symbol=symbol)
            else:
                # A股数据下载
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                stock_name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
                cleaned_name = clean_filename(stock_name)
                
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=self.start_date,
                    end_date=self.end_date,
                    adjust="qfq"
                )
                
                filename = get_filename(symbol, cleaned_name)
                filepath = self.data_dir / filename
                df.to_csv(filepath, index=False, encoding="utf_8_sig")
                print(f"✅ 成功保存: {filepath}")
                
        except Exception as e:
            print(f"❌ 下载失败 {symbol}: {str(e)}")

    def download_data(self) -> None:
        """批量下载股票历史数据"""
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._download_single, symbol) for symbol in self.symbols]
            for future in as_completed(futures):
                future.result()

# 配置示例
if __name__ == "__main__":
    config = {
        "symbols": ["300100", "300378", "300738", "600276", "688185", "AAPL"],
        "start_date": "20240101",
        "end_date": "20250314"
    }
    downloader = StockDataDownloader(**config)
    downloader.download_data()
