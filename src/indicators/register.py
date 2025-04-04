# register.py
from importlib import import_module
from pathlib import Path
import sys


# 这里的__all__变量是一个约定，用于定义模块的公共接口。
# 当使用from module import *语句时，只有在__all__中列出的名称会被导入。

# __all__ = ["SchaffChannel", "ADX", "TechnicalBase"]

# # 添加项目根目录到Python路径（关键步骤）
# project_root = Path(__file__).parent.parent.resolve()  # 上两级目录（到stock_analyzer根目录）
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))

# # print("INDICATOR_REGISTRY路径配置调试:", sys.path)  # 调试语句

# INDICATOR_REGISTRY = {}
# def register_indicator(module_name):
#     """使用绝对导入路径"""
#     module_path = f"indicators.{module_name}"  # 绝对路径（相对于项目根目录）
#     try:
#         module = import_module(module_path)
#         # 通过 importlib 实现运行时反射加载，相比静态导入的优势：
#         # 延迟加载（只有在注册时才加载模块）
#         # 支持热插拔（新增指标无需重启服务）
#         # 错误隔离（单个模块加载失败不影响整体流程）
        
#     except ImportError as e:
#         print(f"模块加载失败: {module_path} ({str(e)})", file=sys.stderr)
#         return
    
#     for cls_name in dir(module):    
#     # 遍历模块中的所有类 
#     # dir()在Python中用于列出一个对象的所有属性和方法。
#     # 当传入一个模块对象时，它会返回列表包含:模块中所有定义的名称，比如函数、类、变量等。
#         cls = getattr(module, cls_name)             # 获取类对象
#         if hasattr(cls, 'INDICATOR_NAME'):          # 检查类是否有INDICATOR_NAME属性
#             INDICATOR_REGISTRY[cls.INDICATOR_NAME] = cls
#             print(f"注册指标: {cls.INDICATOR_NAME}")

# # 自动发现所有指标模块（确保文件名与模块名一致）
# indicator_files = ["indicator_schaff", "technical", "indicator_ADX"]
# for file in indicator_files:
#     register_indicator(file)

INDICATOR_REGISTRY = {}

def register_indicator(module_name):
    """动态注册技术指标"""
    module_path = f"indicators.{module_name}"  
    try:
        module = import_module(module_path)
        # 通过 importlib 实现运行时反射加载，相比静态导入的优势：
        # 延迟加载（只有在注册时才加载模块）
        # 支持热插拔（新增指标无需重启服务）
        # 错误隔离（单个模块加载失败不影响整体流程）
    except ImportError as e:
        print(f"模块加载失败: {module_path} ({str(e)})", file=sys.stderr)
        return
    
    for cls_name in dir(module):    
    # 遍历模块中的所有类 
    # dir()在Python中用于列出一个对象的所有属性和方法。
    # 当传入一个模块对象时，它会返回列表包含:模块中所有定义的名称，比如函数、类、变量等。
        cls = getattr(module, cls_name)             # 获取类对象
        if hasattr(cls, 'INDICATOR_NAME') and cls.INDICATOR_NAME:  # 检查类是否有INDICATOR_NAME属性且不为空
            INDICATOR_REGISTRY[cls.INDICATOR_NAME] = cls
            print(f"注册指标: {cls.INDICATOR_NAME}")
        elif hasattr(cls, 'INDICATOR_NAME'):
            print(f"警告: 发现未命名的指标类 {cls.__name__}")

def register_all_indicators():
    """自动发现所有指标模块"""
    indicator_files = ["indicator_schaff", "indicator_ADX", "indicator_macd"]
    for file in indicator_files:
        register_indicator(file)


def get_registry():
    """获取注册表，避免循环导入问题"""
    return INDICATOR_REGISTRY
