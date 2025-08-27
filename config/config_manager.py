"""配置管理模块

提供配置的读取和修改功能，支持运行时动态修改配置
"""
import json
import os
import sys
import shutil
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理类
    
    用于管理程序配置，支持从JSON文件读取配置，以及运行时修改配置
    """
    _instance = None
    _config_data = {}
    _config_file = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        # 获取可执行文件所在目录下的_internal文件夹中的config.json
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            exe_dir = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        internal_dir = os.path.join(exe_dir, '_internal')
        target_config_path = os.path.join(internal_dir, 'config.json')
        
        # 确保 _internal 目录存在
        os.makedirs(internal_dir, exist_ok=True)
        
        # 如果目标配置文件不存在，尝试从原始位置复制
        if not os.path.exists(target_config_path):
            print(f"目标配置文件 {target_config_path} 不存在。")
            original_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(original_config_path):
                print(f"正在从 {original_config_path} 复制配置文件到 {target_config_path}")
                shutil.copyfile(original_config_path, target_config_path)
                print("配置文件复制成功。")
        
        self._config_file = target_config_path
        self._load_from_file(self._config_file)
    
    def _load_from_file(self, file_path: str) -> None:
        """从JSON文件加载配置
        
        Args:
            file_path: JSON配置文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self._config_data = json.load(f)
        print(f"已从文件 {file_path} 加载配置")
        
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键名
            default: 默认值，当键不存在时返回
            
        Returns:
            配置值或默认值
        """
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self._config_data[key] = value
    
    def save_to_file(self) -> bool:
        """将当前配置保存到文件
        
        Args:
            file_path: 保存的文件路径，如果为None则使用初始化时的文件路径
            
        Returns:
            是否保存成功
        """
        save_path = self._config_file
        if not save_path:
            print("未指定保存路径")
            return False
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, ensure_ascii=False, indent=4)
            print(f"配置已保存到 {save_path}")
            return True
        except Exception as e:
            print(f"保存配置到 {save_path} 失败: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            包含所有配置的字典
        """
        return self._config_data.copy()

# 创建默认配置管理器实例
config_manager = ConfigManager()

# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return config_manager.get(key, default)

def set_config(key: str, value: Any) -> None:
    """设置配置值的便捷函数"""
    config_manager.set(key, value)

def save_config() -> bool:
    """保存配置的便捷函数"""
    return config_manager.save_to_file()