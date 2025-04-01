from matplotlib import pyplot as plt

def plot_adx(df, stock_code):
    """ADX趋势强度可视化"""
    plt.figure(figsize=(16, 8))

    ax = plt.subplot(1, 1, 1, title=f"{stock_code} ADX趋势强度")
    if 'ADX' in df.columns:
        ax.fill_between(df.index, df['ADX'], color='skyblue', alpha=0.4)
        ax.axhline(25, color='gray', linestyle='--')
        ax.axhline(75, color='gray', linestyle='--')
        ax.set_ylabel('ADX值')
    else:
        ax.text(0.5, 0.5, "未选择ADX指标", ha='center', va='center', fontsize=12)

    plt.tight_layout()
    plt.show()