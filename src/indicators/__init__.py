# __init__.py
# from .technical import TechnicalIndicator
from .register import register_all_indicators, INDICATOR_REGISTRY

register_all_indicators()  # 自动注册所有指标
