#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RFID超时检测功能
"""

def test_timeout_detection():
    """测试超时检测功能"""
    try:
        from rfid_util import RFIDUtil
        
        print("测试RFID超时检测功能")
        print("="*50)
        
        # 创建RFID工具实例
        rfid = RFIDUtil()
        
        # 测试超时数据（您提供的数据）
        timeout_hex = """D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5"""
        timeout_data = bytes.fromhex(timeout_hex.replace(' ', ''))
        
        print(f"测试数据长度: {len(timeout_data)} 字节")
        
        # 测试超时检测
        is_timeout = rfid._is_timeout_response(timeout_data)
        print(f"超时检测结果: {'是超时响应' if is_timeout else '不是超时响应'}")
        
        # 测试正常数据
        normal_hex = "D9 19 01 00 2D 01 02 03 30 00 E2 80 11 60 60 00 02 04 08 14 A1 3F 12 34 56 78"
        normal_data = bytes.fromhex(normal_hex.replace(' ', ''))
        
        is_normal_timeout = rfid._is_timeout_response(normal_data)
        print(f"正常数据检测结果: {'是超时响应' if is_normal_timeout else '不是超时响应'}")
        
        # 测试长数据（但不是重复模式）
        long_hex = "D9 19 01 00 2D 01 02 03 30 00 E2 80 11 60 60 00 02 04 08 14 A1 3F 12 34 56 78" * 20
        long_data = bytes.fromhex(long_hex.replace(' ', ''))
        
        is_long_timeout = rfid._is_timeout_response(long_data)
        print(f"长数据检测结果: {'是超时响应' if is_long_timeout else '不是超时响应'}")
        
        print("\n测试完成！")
        
    except ImportError as e:
        print(f"导入失败: {e}")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_timeout_detection()

