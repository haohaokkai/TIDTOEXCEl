#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID指令调试工具
用于调用RFIDUtil类发送指令并打印详细的发送/接收信息
"""
import time
from rfid_util import RFIDUtil  # 假设RFIDUtil类所在文件名为rfid_util.py

def print_separator():
    """打印分隔线，增强输出可读性"""
    print("\n" + "="*60 + "\n")

def main():
    print("===== RFID指令调试工具 =====")
    print("该工具将显示所有发送和接收的指令细节（十六进制格式）")
    
    # 初始化RFID工具（使用默认配置或自定义端口）
    rfid = RFIDUtil()
    
    # 尝试连接设备
    print_separator()
    print("尝试连接RFID设备...")
    if not rfid.connect():
        print("无法连接到设备，程序将退出")
        return
    
    try:
        while True: 
            print_separator()
            print("请选择要执行的操作:")
            print("1. 读取固件版本")
            print("2. 启动盘存")
            print("3. 停止盘存")
            print("4. 读取TID")
            print("5. 设置工作模式（应答模式）")
            print("6. 查询工作模式")
            print("7. 复位设备")
            print("8. 单次读取标签")
            print("9. 读取TID（带计数验证）")
            print("10. 上电")
            print("0. 退出程序")
            
            choice = input("请输入操作编号: ").strip()
            
            print_separator()
            
            if choice == "1":
                print("=== 读取固件版本 ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.read_firmware_version()
                print(f"响应解析: {resp.hex(' ').upper() if resp else '无响应'}")
            
            elif choice == "2":
                print("=== 启动盘存 ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.start_inventory()
                print(f"响应解析: {resp.hex(' ').upper() if resp else '无响应'}")
                if resp == rfid.START_INVENTORY_RESPONSE:
                    print("盘存已启动，正在监听标签数据...（5秒后自动停止）")
                    time.sleep(5)
                    rfid.stop_inventory()
                    print("已自动停止盘存")
            
            elif choice == "3":
                print("=== 停止盘存 ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.stop_inventory()
                print(f"响应解析: {resp.hex(' ').upper() if resp else '无响应'}")
                if resp == rfid.STOP_INVENTORY_RESPONSE:
                    print("盘存已成功停止")
            
            elif choice == "4":
                print("=== 读取TID ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.read_tid()
                print(f"响应解析: {resp.hex(' ').upper() if resp else '无响应'}")
                # 尝试解析TID数据
                tids = rfid._parse_tid_data(resp)
                if tids:
                    print(f"解析到TID: {tids}")
                else:
                    print("未解析到有效TID数据")
            
            elif choice == "5":
                print("=== 设置工作模式（应答模式） ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.set_work_mode(RFIDUtil.MODE_RESPONSE)
                print(f"设置指令响应: {resp.hex(' ').upper() if resp else '无响应'}")
                # 验证设置结果
                mode_resp = rfid.query_work_mode()
                print(f"模式查询响应: {mode_resp.hex(' ').upper() if mode_resp else '无响应'}")
                if mode_resp and len(mode_resp)>=9 and mode_resp[5:9] == RFIDUtil.MODE_RESPONSE:
                    print("工作模式已成功设置为应答模式")
            
            elif choice == "6":
                print("=== 查询工作模式 ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.query_work_mode()
                print(f"响应解析: {resp.hex(' ').upper() if resp else '无响应'}")
                if resp and b'\xD9' in resp and len(resp)>=9:
                    mode_data = resp[5:9]
                    mode_str = "应答模式" if mode_data == RFIDUtil.MODE_RESPONSE else \
                               "上电模式" if mode_data == RFIDUtil.MODE_POWER_ON else \
                               f"未知模式 ({mode_data.hex()})"
                    print(f"当前工作模式: {mode_str}")
            
            elif choice == "7":
                print("=== 复位设备 ===")
                rfid.ser.reset_input_buffer()
                confirm = input("确定要复位设备吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    resp = rfid.reset()
                    print(f"复位指令响应: {resp.hex(' ').upper() if resp else '无响应'}")
                    print("设备已复位，等待1秒后恢复通信...")
                    time.sleep(1)
                else:
                    print("已取消复位操作")
            
            elif choice == "8":
                print("=== 单次读取标签 ===")
                rfid.ser.reset_input_buffer()
                timeout = input("请输入读取超时时间(秒，默认0.5): ").strip()
                timeout = float(timeout) if timeout else 0.5
                result = rfid.read_once(timeout=timeout)
                print(f"读取结果（按天线分组）: {result}")
                if result:
                    print("\n详细标签信息:")
                    for ant_id, tags in result.items():
                        print(f"天线 {ant_id}:")
                        for tag in tags:
                            print(f"  EPC: {tag['epc']}, 信号强度: {tag['info']['rssi']} dBm")
            
            elif choice == "9":
                print("=== 读取TID（带计数验证） ===")
                rfid.ser.reset_input_buffer()
                count = input("请输入需要连续读取的次数(默认3次): ").strip()
                count = int(count) if count else 3
                timeout = input("请输入超时时间(秒，默认10秒): ").strip()
                timeout = float(timeout) if timeout else 10.0
                
                print(f"开始读取，需要连续{count}次读到相同TID...")
                tid = rfid.read_tid_with_count_verification(
                    required_count=count,
                    max_duration=timeout,
                    callback=lambda t, c: print(f"回调: TID {t} 已连续读取{c}次")
                )
                if tid:
                    print(f"成功读取到TID: {tid}")
                else:
                    print("未成功读取到符合条件的TID")
            elif choice == "10":
                print("=== 设置工作模式（上电模式） ===")
                rfid.ser.reset_input_buffer()
                resp = rfid.set_work_mode(RFIDUtil.MODE_POWER_ON)
                print(f"设置指令响应: {resp.hex(' ').upper() if resp else '无响应'}")
                # 验证设置结果
                mode_resp = rfid.query_work_mode()
                print(f"模式查询响应: {mode_resp.hex(' ').upper() if mode_resp else '无响应'}")
                if mode_resp and len(mode_resp)>=9 and mode_resp[5:9] == RFIDUtil.MODE_POWER_ON:
                    print("工作模式已成功设置为上电模式")
            elif choice == "0":
                print("退出程序...")
                break
            
            else:
                print("无效的操作编号，请重新输入")
            
            print("\n操作完成，按回车键继续...", end='')
            input()
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    finally:
        rfid.close()
        print("\n程序结束，已断开RFID设备连接")

if __name__ == "__main__":
    main()