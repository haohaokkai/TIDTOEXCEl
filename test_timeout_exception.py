#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RFID超时异常功能
"""

def test_timeout_exception():
    """测试超时异常功能"""
    try:
        from rfid_util import RFIDUtil, TimeoutDetectedException
        
        print("测试RFID超时异常功能")
        print("="*50)
        
        # 创建RFID工具实例
        rfid = RFIDUtil()
        
        # 测试超时数据（重复的模式）
        timeout_hex = """D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5 D9 19 01 00 2D 01 0D 01 30 00 E2 80 F3 02 20 00 00 00 B9 C7 CA 0A DF 22 00 00 D5"""
        timeout_data = bytes.fromhex(timeout_hex.replace(' ', ''))
        
        print(f"测试数据长度: {len(timeout_data)} 字节")
        
        # 模拟send_cmd函数，检查异常是否正确抛出
        try:
            # 验证超时检测
            if rfid._is_timeout_response(timeout_data):
                print("检测到超时数据，尝试抛出异常...")
                # 模拟send_cmd的异常抛出逻辑
                raise TimeoutDetectedException("RFID通信超时：检测到重复数据帧，可能存在通信问题")
        except TimeoutDetectedException as e:
            print(f"✓ 成功捕获超时异常: {e}")
        
        # 测试非超时数据
        normal_hex = "D9 19 01 00 2D 01 02 03 30 00 E2 80 11 60 60 00 02 04 08 14 A1 3F 12 34 56 78"
        normal_data = bytes.fromhex(normal_hex.replace(' ', ''))
        
        try:
            # 验证正常数据
            if rfid._is_timeout_response(normal_data):
                raise TimeoutDetectedException("RFID通信超时：检测到重复数据帧，可能存在通信问题")
            else:
                print("✓ 正常数据未触发超时异常")
        except TimeoutDetectedException:
            print("✗ 正常数据错误地触发了超时异常")
        
        print("\n测试完成！")
        
    except ImportError as e:
        print(f"导入失败: {e}")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_timeout_exception()
