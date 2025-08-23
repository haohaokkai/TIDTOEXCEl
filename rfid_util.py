#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UHF 超高频 RFID 读写器工具类（协议 V2.16）
"""
import time
import serial
from typing import Dict,List, Optional, Any
import threading


class EpcFrameDetectedException(Exception):
    """检测到EPC帧时抛出的异常，提示需要重置RFID设备"""
    pass


class TimeoutDetectedException(Exception):
    """检测到超时数据时抛出的异常，提示可能存在通信问题"""
    pass


# 尝试导入配置管理器，如果失败则使用简化配置
try:
    from config.config_manager import get_config
except ImportError:
    # 如果都没有，使用默认配置
    def get_config(key, default=None):
        defaults = {
            "rfid_port": "COM4",
            "rfid_baudrate": 115200,
            "rfid_timeout": 0.5
        }
        return defaults.get(key, default)

class RFIDUtil:
    """UHF超高频RFID读写器通信工具类
    
    单例模式，支持V2.16协议，提供标签读取、设置和查询功能
    """


    
    # 单例模式相关属性
    _instance = None
    _lock = threading.Lock()
    
    # 默认参数
    DEFAULT_PORT = get_config("rfid_port")
    DEFAULT_BAUD = get_config("rfid_baudrate")
    DEFAULT_TIMEOUT = get_config("rfid_timeout")
    DEFAULT_DELAY=0.05 #读取延迟
    # 命令码定义
    CMD_READ_FIRMWARE = 0x10    # 读固件版本
    CMD_START_INVENTORY = 0x20  # 启动EPC盘存
    CMD_STOP_INVENTORY = 0x2F   # 停止盘存
    CMD_READ_TID = 0x2D         # 读TID
    CMD_SET_WORK_MODE = 0x51    # 设置工作模式
    CMD_QUERY_WORK_MODE = 0x52  # 查询工作模式
    CMD_RESET = 0x40            # 复位
    
    # 特殊帧标识
    START_INVENTORY_RESPONSE = b'\xD9\x06\x01\x00\x20\x00\x00\x00'  # 启动盘存响应
    STOP_INVENTORY_RESPONSE = b'\xD9\x06\x01\x00\x2F\x00\x00\xF1'   # 停止盘存响应
    READ_TID_SUCCESS_RESPONSE = b'\xD9\x06\x01\x00\x2D\x00\x00\xF3'  # 读TID指令成功响应


    # 工作模式定义
    MODE_RESPONSE = b'\x00\x00\x00\x00' # 应答模式
    MODE_POWER_ON = b'\x03\x00\x00\x00' # 上电模式
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RFIDUtil, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, port=DEFAULT_PORT, baudrate=DEFAULT_BAUD, timeout=DEFAULT_TIMEOUT):
        """初始化RFID读写器连接
        
        Args:
            port: 串口名称，默认COM4
            baudrate: 波特率，默认115200
            timeout: 读取超时时间(秒)，默认0.5
        """
        # 单例模式下，只初始化一次
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connected = False
        self._initialized = True
        
        # 延迟连接，不在初始化时立即连接，避免导入时出错
        # 首次调用方法时会自动连接

    def connect(self) -> bool:
        """连接到串口设备

        Returns:
            bool: 连接是否成功
        """
        try:
            if self.connected and self.ser and self.ser.is_open:
                # 已经连接，更新全局状态并返回
                
                return True

            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=self.timeout
            )
            self.connected = self.ser.is_open

            # 更新全局连接状态
            

            if self.connected:
                print(f"✅ RFID设备连接成功: {self.port} @ {self.baudrate}")
            else:
                print(f"❌ RFID设备连接失败: {self.port}")

            return self.connected
        except serial.SerialException as e:
            print(f"❌ RFID设备连接错误: {e}")
            self.connected = False
            # 更新全局连接状态
            
            return False

    @staticmethod
    def checksum(frame_without_ck: bytes) -> int:
        """
        协议校验：所有字节求和→取低 8 位→按位取反→+1
        """
        return (~(sum(frame_without_ck) & 0xFF) + 1) & 0xFF

    @staticmethod
    def build_frame(cmd: int, data: bytes = b'') -> bytes:
        """
        构建协议帧
        
        协议格式：
        D9 | LEN | 485_Addr_L | 485_Addr_H | CMD | DATA... | CK
        LEN = 从 485_Addr_L 开始的所有字节数（不含 LEN 本身，不含 CK）
        CK  = ~(sum(D9..DATA) & 0xFF) + 1
        
        Args:
            cmd: 命令码
            data: 命令数据
            
        Returns:
            构建好的完整协议帧
        """
        payload = b'\x01\x00' + bytes([cmd]) + data   # 地址 0x0100 低字节在前
        length = len(payload)+1
        head_len = b'\xD9' + bytes([length])
        frame_without_ck = head_len + payload
        ck = RFIDUtil.checksum(frame_without_ck)
        return frame_without_ck + bytes([ck])

    def _is_timeout_response(self, data: bytes) -> bool:
        """检测是否为超时响应
        
        Args:
            data: 响应数据
            
        Returns:
            bool: 是否为超时响应
        """
        if len(data) < 50:  # 超时响应通常很长
            return False
        
        # 已知超时模式
        timeout_pattern = bytes.fromhex('D9190100 2D010D01 3000E280 F3022000 0000B9C7 CA0ADF22 0000D5'.replace(' ', ''))
        
        # 检查是否包含超时模式且重复出现
        if timeout_pattern in data:
            pattern_count = data.count(timeout_pattern)
            if pattern_count >= 3:  # 重复3次以上视为超时
                print(f'[超时检测] 检测到超时响应，模式重复{pattern_count}次')
                return True
        
        # 检查数据长度异常（超过500字节很可能是超时）
        if len(data) > 500:
            print(f'[超时检测] 数据长度异常: {len(data)} 字节，判断为超时')
            return True
            
        return False

    def send_cmd(self, cmd: int, data: bytes = b'', timeout=DEFAULT_TIMEOUT) -> bytes:
        """发送命令并获取响应
        
        Args:
            cmd: 命令码
            data: 命令数据
            timeout: 等待响应超时时间(秒)
            
        Returns:
            原始响应数据
        """
        # 自动连接检查
        if not self.connected:
            if not self.connect():
                print("未连接到设备，无法发送命令")
                return b''
        
        # 确保缓冲区干净
        self.ser.reset_input_buffer()
        
        # 构建并发送帧
        frame = self.build_frame(cmd, data)
        self.ser.write(frame)
        self.ser.flush()
        print(f'[SEND] {frame.hex(" ").upper()}')
        
        # 等待并读取响应
        time.sleep(self.DEFAULT_DELAY)
        resp = self.ser.read(self.ser.in_waiting or 256)
        
        # 超时检测
        if resp and self._is_timeout_response(resp):
            print(f'[RECV] <检测到超时响应，抛出异常>')
            raise TimeoutDetectedException("RFID通信超时：检测到重复数据帧，可能存在通信问题")
        
        if resp:
            print(f'[RECV] {resp.hex(" ").upper()}')
        else:
            print('[RECV] <超时无数据>')
        return resp

    def _split_frames(self, raw_data: bytes) -> List[bytes]:
        """
        将原始数据按帧头分割为多个帧
        
        Args:
            raw_data: 原始字节数据
            
        Returns:
            帧列表，每个元素为一个完整帧
        """
        result = []
        segments = raw_data.split(b'\xD9')
        for segment in segments[1:]:  # 跳过第一个可能为空的段
            if segment:
                frame = b'\xD9' + segment
                result.append(frame)
        return result

    def _process_frames_from_data(self, raw_data: bytes, results_by_antenna: dict,
                                antennas_read: set, source_desc: str = "数据") -> None:
        """
        从原始数据中提取并处理所有可能的帧

        Args:
            raw_data: 原始字节数据
            results_by_antenna: 按天线分组的结果字典，会被修改
            antennas_read: 已读取的天线集合，会被修改
            source_desc: 数据来源描述，用于日志
        """
        print(f"[调试] 处理{source_desc}: {raw_data.hex(' ').upper()}")

        # 1. 检查是否包含开始读卡标识，如果有，特别处理后续数据
        if self.START_INVENTORY_RESPONSE in raw_data:
            parts = raw_data.split(self.START_INVENTORY_RESPONSE)
            for i, part in enumerate(parts[1:], 1):  # 跳过第一个部分
                if not part:
                    continue
                self._process_frames_from_data(part, results_by_antenna, antennas_read, f"{source_desc}-开始标识后{i}")

        # 2. 分割所有可能的帧并处理
        frames = self._split_frames(raw_data)
        print(f"[调试] {source_desc}中分割出 {len(frames)} 个可能的帧")

        # 收集所有帧的标签信息
        frame_infos = []
        for i, frame in enumerate(frames, 1):
            # 跳过特殊帧
            if self._is_special_frame(frame):
                print(f"[调试] 跳过特殊帧 {i}: {frame.hex(' ').upper()}")
                continue

            # 处理可能的标签数据帧
            tag_info = self.parse_tag_frame(frame)
            if not tag_info:
                continue

            frame_infos.append(tag_info)

        # 处理所有标签数据，保存到对应天线的列表中
        for tag_info in frame_infos:
            ant_id = tag_info['ant']
            epc = tag_info['epc']

            # 初始化天线的标签列表（如果还没有）
            if ant_id not in results_by_antenna:
                results_by_antenna[ant_id] = []

            # 检查是否已经存在相同的EPC，避免重复添加
            existing_epcs = [tag['epc'] for tag in results_by_antenna[ant_id]]
            if epc not in existing_epcs:
                # 添加新的标签数据
                results_by_antenna[ant_id].append({
                    'epc': epc,
                    'info': tag_info
                })
                antennas_read.add(ant_id)
                print(f'[读取到标签] 天线{ant_id:02d} EPC:{epc} RSSI:{tag_info["rssi"]} dBm')
            else:
                print(f'[重复标签] 天线{ant_id:02d} EPC:{epc} 已存在，跳过')

    def read_firmware_version(self) -> bytes:
        """读取固件版本"""
        return self.send_cmd(self.CMD_READ_FIRMWARE)

    def start_inventory(self) -> bytes:
        """启动EPC盘存"""
        return self.send_cmd(self.CMD_START_INVENTORY)

    def stop_inventory(self) -> bytes:
        """停止盘存"""
        return self.send_cmd(self.CMD_STOP_INVENTORY)

    def read_tid(self) -> bytes:
        """读TID"""
        return self.send_cmd(self.CMD_READ_TID)

    def start_tid_reading_mode(self) -> bool:
        """启动TID读取模式

        Returns:
            bool: 是否成功启动TID读取模式
        """
        try:
            print("📡 发送读TID指令，启动TID读取模式...")

            # 清空缓冲区
            if self.ser:
                self.ser.reset_input_buffer()

            # 发送读TID指令
            response = self.send_cmd(self.CMD_READ_TID)

            # 验证响应
            return self._verify_read_tid_response(response)

        except Exception as e:
            print(f"❌ 启动TID读取模式失败: {e}")
            return False

    def set_work_mode(self, data: bytes) -> bytes:
        """设置工作模式
        
        Args:
            data: 模式数据，按协议格式传入
                常见值:
                b'\x00\x00\x00\x00' - 应答模式
                b'\x03\x00\x00\x00' - 上电模式
        """
        return self.send_cmd(self.CMD_SET_WORK_MODE, data)

    def query_work_mode(self) -> bytes:
        """查询工作模式"""
        return self.send_cmd(self.CMD_QUERY_WORK_MODE)

    def reset(self) -> bytes:
        """复位设备"""
        return self.send_cmd(self.CMD_RESET)
    

    def close(self):
        """关闭串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print(f'🔌 RFID设备已断开连接: {self.port}')




    def read_tid_with_count_verification(self, required_count=5, max_duration=30, callback=None) -> Optional[str]:
        """在应答模式下持续读取TID，连续读到同一个TID n次后返回

        Args:
            required_count: 需要连续读取到相同TID的次数，默认5次
            max_duration: 最大读取时长(秒)，默认30秒
            callback: 回调函数，当读取到TID时调用，参数为(tid, count)

        Returns:
            str: 连续读取到n次的TID，超时或失败返回None
        """
        # 自动连接检查
        if not self.connected:
            if not self.connect():
                print("❌ 未连接到设备，无法读取TID")
                return None


        print(f"🔄 开始读取TID，需要连续读取{required_count}次相同TID")
        print(f"⏱️ 最大时长: {max_duration}秒")

        # 发送一次read_tid指令进入读取TID模式
        print("📡 发送读TID指令，进入TID读取模式...")
        self.ser.reset_input_buffer()  # 清空缓冲区
        # tid_response = self.send_cmd(self.CMD_READ_TID)

        # # 验证是否成功进入TID读取模式
        # if not self._verify_read_tid_response(tid_response):
        #     print("❌ 未能进入TID读取模式")
        #     return None

        print("✅ 成功进入TID读取模式，开始监听串口数据...")

        # TID计数器
        current_tid = None
        current_count = 0
        start_time = time.time()

        try:
            while time.time() - start_time < max_duration:
                # 直接读取串口传输过来的数据
                if self.ser.in_waiting > 0:
                    raw_data = self.ser.read(self.ser.in_waiting)
                    if raw_data:
                        print(f"[串口数据] 收到: {raw_data.hex(' ').upper()}")

                        # 解析TID数据
                        new_tids = self._parse_tid_data(raw_data)

                        for tid in new_tids:
                            if tid == current_tid:
                                # 相同TID，计数器增加
                                current_count += 1
                                print(f"📋 TID: {tid} (第{current_count}次)")

                                # 调用回调函数
                                if callback:
                                    try:
                                        callback(tid, current_count)
                                    except Exception as e:
                                        print(f"⚠️ 回调函数执行失败: {e}")

                                # 检查是否达到要求的次数
                                if current_count >= required_count:
                                    print(f"✅ TID {tid} 已连续读取{current_count}次，返回结果")
                                    return tid

                            else:
                                # 不同TID，重置计数器
                                if current_tid is not None:
                                    print(f"🔄 TID变化: {current_tid} -> {tid}，重置计数器")
                                else:
                                    print(f"📋 首次读取到TID: {tid}")

                                current_tid = tid
                                current_count = 1

                                # 调用回调函数
                                if callback:
                                    try:
                                        callback(tid, current_count)
                                    except Exception as e:
                                        print(f"⚠️ 回调函数执行失败: {e}")

                time.sleep(0.05)  # 短暂休眠避免过度占用CPU

        except KeyboardInterrupt:
            print("\n⏹️ 用户中断读取")
        except Exception as e:
            print(f"❌ 读取过程中发生错误: {e}")

        print(f"⚠️ 超时或未能连续读取到{required_count}次相同TID")
        if current_tid:
            print(f"📊 最后读取的TID: {current_tid} (共{current_count}次)")

        return None


    def _parse_tid_data(self, raw_data: bytes) -> List[str]:
        """解析TID数据，支持多条返回数据的分割解析

        Args:
            raw_data: 原始字节数据

        Returns:
            List[str]: 解析出的TID列表
        """
        tids = []

        try:
            print(f"[TID解析] 处理原始数据: {raw_data.hex(' ').upper()}")

            # 使用与EPC解析相同的帧分割逻辑
            frames = self._split_frames(raw_data)
            print(f"[TID解析] 分割出 {len(frames)} 个帧")

            for i, frame in enumerate(frames, 1):
                print(f"[TID解析] 处理第{i}个帧: {frame.hex(' ').upper()}")

                if len(frame) < 8:
                    print(f"[TID解析] 帧{i}太短，跳过")
                    continue

                # 检查帧格式
                if frame[0] != 0xD9:
                    print(f"[TID解析] 帧{i}不是有效帧头，跳过")
                    continue

                cmd = frame[4]
                print(f"[TID解析] 帧{i}命令码: 0x{cmd:02X}")

                # 方法1: 检查是否为读TID命令的直接响应
                if cmd == self.CMD_READ_TID:
                    tid = self._parse_tid_response_frame(frame)
                    if tid:
                        tids.append(tid)
                        print(f"[TID解析] 从TID响应帧提取: {tid}")

                # 方法2: 检查是否为盘存响应中的EPC数据
                elif cmd == self.CMD_START_INVENTORY:
                    print(f"⚠️ [TID解析] 检测到EPC帧(0x{cmd:02X})，设备可能处于EPC模式而非TID模式")
                    print(f"💡 [TID解析] 建议执行RFID重置操作：停止存盘->读TID")

                    # 抛出特殊异常，通知上层需要重置RFID
                    raise EpcFrameDetectedException("检测到EPC帧，需要重置RFID设备到TID模式")

                # 方法3: 尝试解析其他可能包含TID数据的帧
                else:
                    print(f"[TID解析] 帧{i}命令码0x{cmd:02X}不是TID或盘存响应，跳过")

        except Exception as e:
            print(f"[TID解析] 解析错误: {e}")
            print(f"[TID解析] 原始数据: {raw_data.hex(' ').upper()}")

        print(f"[TID解析] 总共解析出 {len(tids)} 个TID: {tids}")
        return tids

    def _parse_tid_response_frame(self, frame: bytes) -> Optional[str]:
        """解析TID响应帧，提取TID数据

        Args:
            frame: 单个TID响应帧

        Returns:
            str: 提取的TID，如果解析失败返回None
        """
        try:
            # 根据协议文档，TID帧的最小长度应该是26字节
            # D9(1) + LEN(1) + Reserved(2) + CMD(1) + Flags(1) + Freq(1) + Ant(1) + PC(2) + TID(12) + CRC(2) + RSSI(2) + CK(1) = 26字节
            if len(frame) < 26:
                print(f"[TID帧解析] 帧太短: {len(frame)} < 26")
                return None

            # 帧格式: D9 LEN Reserved(2) CMD Flags Freq Ant PC(2) TID(12) CRC(2) RSSI(2) CK
            # TID数据位置: 从第11字节开始，长度12字节

            frame_len = frame[1]
            cmd = frame[4]
            print(f"[TID帧解析] 帧长度: {frame_len}, 命令码: 0x{cmd:02X}")

            # 验证是否为TID命令响应
            if cmd != self.CMD_READ_TID:
                print(f"[TID帧解析] 不是TID命令响应: 0x{cmd:02X}")
                return None

            # TID数据从第11字节开始（索引10），长度12字节
            tid_data_start = 10  # 第11字节的索引
            tid_data_end = tid_data_start + 12  # TID长度12字节

            if len(frame) >= tid_data_end:
                tid_data = frame[tid_data_start:tid_data_end]

                # 过滤空数据
                if len(tid_data) == 12 and not all(b == 0 for b in tid_data):
                    tid_hex = tid_data.hex().upper()
                    print(f"[TID帧解析] 提取TID数据: {tid_hex}")
                    print(f"[TID帧解析] 完整帧: {frame.hex(' ').upper()}")
                    print(f"[TID帧解析] TID位置: 字节{tid_data_start+1}-{tid_data_end}")
                    return tid_hex
                else:
                    print(f"[TID帧解析] TID数据为空或全零: {tid_data.hex(' ').upper()}")
            else:
                print(f"[TID帧解析] 帧长度不足，无法提取12字节TID: {len(frame)} < {tid_data_end}")

        except Exception as e:
            print(f"[TID帧解析] 解析异常: {e}")
            print(f"[TID帧解析] 问题帧: {frame.hex(' ').upper()}")

        return None

# 创建全局实例
rfid_util = RFIDUtil()

