import akshare as ak
import pandas as pd

# 获取A股实时行情数据数据,返回的是一个pandas.DataFrame对象，包含了沪深京A股上市公司的实时行情数据。

# data_cfw=ak.stock_zh_a_spot_em()    # 获取A股实时行情数据数据来源于东方财富网。
# data_sina=ak.stock_zh_a_spot()      # 获取A股实时行情数据数据来源于新浪财经。

# print(data_sina.describe())
# print(data_sina.info())


# stock_individual_info_em_df = ak.stock_individual_info_em(symbol="600276")
# print(stock_individual_info_em_df)

# Fetch real-time market data
# real_time_data = ak.stock_zh_a_spot_em()

# # Filter the data for the specific stock code "600276"
# real_time_data_600276 = real_time_data[real_time_data['代码'] == '600276']
# print(real_time_data_600276)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# ================== 全局配置 ==================
plt.rcParams.update({
    'font.sans-serif': 'Microsoft YaHei',  # 中文字体
    'axes.unicode_minus': False,           # 显示负号
    'figure.dpi': 150                      # 显示分辨率
})

# ================== 数据准备 ==================
def load_and_preprocess(filename):
    """数据加载与预处理"""
    try:
        df = pd.read_csv(f"{filename}.csv", 
                         encoding='utf-8',
                         parse_dates=['日期'],
                         infer_datetime_format=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {filename}.csv 不存在")
        
    # 日期有效性检查
    date_mask = df['日期'].isna()
    if date_mask.any():
        print(f"发现 {date_mask.sum()} 行无效日期，示例：\n{df[date_mask].head()}")
        df = df[~date_mask]
    
    return df.set_index('日期')

# ================== 技术指标计算 ==================
class TechnicalIndicators:
    """技术指标计算工具类"""
    
    @staticmethod
    def weighted_price(df):
        """计算加权价格（向量化实现）"""
        weights = np.array([2, 1, 1])[:, None]  # 增加维度用于广播
        weighted = (df[['收盘', '最高', '最低']].values * weights).sum(axis=0) / 4
        return pd.Series(weighted, index=df.index)
    
    @staticmethod
    def volatility(df, window=20):
        """计算波动率指标"""
        ma = df['收盘'].rolling(window).mean()
        return (TechnicalIndicators.weighted_price(df) - ma).abs() / ma
    
    @staticmethod
    def dynamic_ma(df, alpha_series, adjust=False):
        """动态指数移动平均"""
        alpha = alpha_series.values
        weights = (1 - alpha) ** np.arange(len(alpha))[::-1, None]
        weights /= weights.sum(axis=0)
        return (df.values * weights).sum(axis=0)
    
    @staticmethod
    def adx_calculation(df, period=14):
        """平均趋向指数计算"""
        df = df.copy()
        df['TR'] = np.maximum(
            df['最高'] - df['最低'],
            np.maximum(
                abs(df['最高'] - df['收盘'].shift()),
                abs(df['最低'] - df['收盘'].shift())
            )
        )
        
        df['+DM'] = np.where(
            (df['最高'].diff() > df['最低'].shift().diff().abs()),
            df['最高'].diff().clip(lower=0), 0)
        
        df['-DM'] = np.where(
            (df['最低'].shift().diff().abs() > df['最高'].diff()),
            df['最低'].shift().diff().abs().clip(lower=0), 0)
        
        # 平滑处理
        smooth = lambda x: x.ewm(alpha=1/period, adjust=False).mean()
        df['+DI'] = smooth(df['+DM']) / smooth(df['TR']) * 100
        df['-DI'] = smooth(df['-DM']) / smooth(df['TR']) * 100
        df['ADX'] = smooth(abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']) * 100)
        
        return df[['+DI', '-DI', 'ADX']]

# ================== 主程序 ==================
if __name__ == "__main__":
    # 参数配置
    N = 50
    M = 10
    
    # 加载数据
    filename = '300100_双林股份_historical_data'
    df = load_and_preprocess(filename)
    
    # ========== 指标计算 ==========
    # 加权价格相关指标
    df['AA'] = TechnicalIndicators.weighted_price(df).rolling(5).mean()
    df['通道1'] = df['AA'] * N / 100
    df['通道2'] = df['AA'] * (200 - N) / 100
    
    # 波动率相关指标
    df['CC'] = TechnicalIndicators.volatility(df)
    df['DD'] = TechnicalIndicators.dynamic_ma(df['收盘'], df['CC'])
    
    # 通道计算
    df['通道3'] = (1 + M/100) * df['DD']
    df['通道4'] = (1 - M/100) * df['DD']
    
    # 成交量加权指标
    df['VAR2'] = df['收盘'] * df['成交量']
    df['VAR3'] = TechnicalIndicators.dynamic_ma(df['VAR2'], pd.Series(0.25, index=df.index))
    
    # ADX指标
    adx_df = TechnicalIndicators.adx_calculation(df)
    df = pd.concat([df, adx_df], axis=1)
    
    # ========== 可视化 ==========
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True, 
                                  gridspec_kw={'height_ratios': [3, 1]})
    
    # 价格与通道
    price_colors = ['#1f77b4', '#2ca02c', '#d62728', '#ff7f0e', '#9467bd']
    labels = ['收盘价', '通道1', '通道2', '通道3', '通道4']
    for i, col in enumerate(['收盘', '通道1', '通道2', '通道3', '通道4']):
        ax1.plot(df.index, df[col], color=price_colors[i], 
                linewidth=1.5 if i==0 else 1.2, 
                alpha=0.8 if i==0 else 0.6, 
                label=labels[i])
    
    # ADX指标
    ax2.fill_between(df.index, df['ADX'], alpha=0.3, color='purple', label='ADX')
    ax2.axhline(25, color='gray', linestyle='--', alpha=0.7)
    ax2.axhline(75, color='gray', linestyle='--', alpha=0.7)
    
    # 图表装饰
    ax1.set_title(f'{filename.split("_")[1]} 技术分析', fontsize=14, pad=20)
    ax1.set_ylabel('价格水平', fontsize=10)
    ax1.legend(loc='upper left', ncol=3)
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
    
    ax2.set_title('ADX趋势强度指标', fontsize=10, pad=10)
    ax2.set_ylabel('ADX值', fontsize=9)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.show()