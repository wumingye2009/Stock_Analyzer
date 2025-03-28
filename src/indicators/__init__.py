# 指标注册中心
from importlib import import_module
from pathlib import Path
import sys
# src/indicators/__init__.py
from .schaff import SchaffChannel
from .adx import ADX
from .technical import TechnicalBase

__all__ = ["SchaffChannel", "ADX", "TechnicalBase"]

# 添加项目根目录到Python路径（关键步骤）
project_root = Path(__file__).parent.parent.resolve()  # 上两级目录（到stock_analyzer根目录）
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("INDICATOR_REGISTRY路径配置调试:", sys.path)  # 调试语句

INDICATOR_REGISTRY = {}
def register_indicator(module_name):
    """使用绝对导入路径"""
    module_path = f"indicators.{module_name}"  # 绝对路径（相对于项目根目录）
    try:
        module = import_module(module_path)
    except ImportError as e:
        print(f"模块加载失败: {module_path} ({str(e)})", file=sys.stderr)
        return
    
    for cls_name in dir(module):
        cls = getattr(module, cls_name)
        if hasattr(cls, 'INDICATOR_NAME'):
            INDICATOR_REGISTRY[cls.INDICATOR_NAME] = cls
            print(f"注册指标: {cls.INDICATOR_NAME}")

# 自动发现所有指标模块（确保文件名与模块名一致）
indicator_files = ["schaff", "technical", "adx"]



for file in indicator_files:
    register_indicator(file)



