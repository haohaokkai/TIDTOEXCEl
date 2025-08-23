# RFID TID读取功能说明

## 功能概述

新增的TID读取功能支持在应答模式下读取RFID标签的TID数据，具有以下特点：

- **应答模式**: 使用应答模式进行单次TID读取
- **计数验证**: 连续读取相同TID指定次数后返回，确保稳定性
- **去重处理**: 对连续读取到的同一标签进行计数验证
- **回调支持**: 支持回调函数，实时处理读取进度
- **超时控制**: 可设置最大读取时长
- **自动停止**: 每次调用完成后自动停止读取

## 主要方法

### 1. `_ensure_response_mode()` - 确保应答模式
```python
rfid_util._ensure_response_mode()
```
- 将RFID设备切换到应答模式
- 自动查询和设置工作模式
- 内部方法，通常无需手动调用

### 2. `read_tid_with_count_verification(required_count=5, max_duration=30, callback=None)` - 计数验证TID读取
```python
def on_tid_callback(tid, count):
    print(f"TID: {tid}, 第{count}次")

tid = rfid_util.read_tid_with_count_verification(
    required_count=5,
    max_duration=20,
    callback=on_tid_callback
)
```
- **工作原理**:
  1. 进入应答模式
  2. 发送一次read_tid指令进入TID读取模式
  3. 验证收到READ_TID_SUCCESS_RESPONSE响应
  4. 持续监听串口数据，无需再发送指令
  5. 连续读到相同TID n次后返回
- 参数:
  - `required_count`: 需要连续读取的次数
  - `max_duration`: 最大读取时长(秒)
  - `callback`: 回调函数，参数为(tid, count)
- 返回: `str` - 连续读取到n次的TID，失败返回None

### 3. `read_single_tid(timeout=5.0, required_count=1)` - 读取单个TID
```python
# 读取1次即返回
tid = rfid_util.read_single_tid(timeout=10.0)

# 需要连续读取3次相同TID
tid = rfid_util.read_single_tid(timeout=15.0, required_count=3)
```
- 可指定需要连续读取的次数
- 参数:
  - `timeout` - 超时时间(秒)
  - `required_count` - 连续读取次数，默认1次
- 返回: `str` - TID字符串，超时返回None

### 4. `read_tid_continuous(max_duration=30, callback=None)` - 持续读取TID
```python
def on_tid_read(tid):
    print(f"新TID: {tid}")

tids = rfid_util.read_tid_continuous(
    max_duration=15, 
    callback=on_tid_read
)
```
- 持续读取TID，返回所有唯一TID
- 参数:
  - `max_duration`: 最大读取时长(秒)
  - `callback`: 回调函数，参数为TID字符串
- 返回: `Set[str]` - 所有读取到的唯一TID集合

## 响应验证机制

### 读TID指令响应验证
程序会验证读TID指令的响应，确保设备正确进入TID读取模式：

- **成功响应**: `0xD9 0x06 0x01 0x00 0x2D 0x00 0x00 0xF3`
- **验证逻辑**:
  - 完全匹配：响应与预期完全相同
  - 部分匹配：前5字节匹配（帧头、长度、地址、命令码）
- **失败处理**: 如果响应不匹配，程序会停止TID读取并报告错误

### TID读取模式工作流程
1. **模式准备**: 确保设备处于应答模式
2. **指令发送**: 发送一次read_tid指令 (CMD_READ_TID = 0x2D)
3. **响应验证**: 验证收到READ_TID_SUCCESS_RESPONSE
4. **模式激活**: 成功后设备进入TID读取模式
5. **数据监听**: 持续监听串口数据，无需再发送指令
6. **自动解析**: 自动解析收到的TID数据并进行计数验证

### 响应格式说明
```
0xD9        - 帧头
0x06        - 数据长度
0x01 0x00   - 地址
0x2D        - 命令码（读TID）
0x00 0x00   - 状态/数据
0xF3        - 校验码
```

## 使用示例

### 基本使用
```python
from rfid_util import rfid_util

# 连接设备
if rfid_util.connect():
    # 读取单个TID
    tid = rfid_util.read_single_tid(timeout=10.0)
    if tid:
        print(f"TID: {tid}")
    
    # 关闭连接
    rfid_util.close()
```

### 计数验证示例
```python
from rfid_util import rfid_util

def handle_tid_count(tid, count):
    """处理TID计数"""
    print(f"TID: {tid}, 第{count}次读取")
    if count >= 3:
        print(f"TID {tid} 已稳定读取")

# 连接设备
if rfid_util.connect():
    try:
        # 需要连续读取5次相同TID
        stable_tid = rfid_util.read_tid_with_count_verification(
            required_count=5,
            max_duration=20,
            callback=handle_tid_count
        )

        if stable_tid:
            print(f"稳定TID: {stable_tid}")
        else:
            print("未获得稳定TID")

    finally:
        rfid_util.close()
```

### 持续读取示例
```python
from rfid_util import rfid_util

def handle_new_tid(tid):
    """处理新读取到的TID"""
    print(f"收到新TID: {tid}")
    # 在这里添加你的处理逻辑

# 连接设备
if rfid_util.connect():
    try:
        # 持续读取15秒
        all_tids = rfid_util.read_tid_continuous(
            max_duration=15,
            callback=handle_new_tid
        )
        print(f"总共读取到 {len(all_tids)} 个唯一TID")

    finally:
        rfid_util.close()
```

## 测试工具

### 1. 基本功能测试
```bash
python test_tid_reader.py
```
- 测试设备连接
- 测试单个TID读取
- 测试持续TID读取

### 2. 集成演示
```bash
python tid_integration_example.py
```
- 图形界面演示
- 实时TID显示
- 读取历史记录

### 3. 读TID指令响应验证测试
```bash
python test_tid_command.py
```
- 测试读TID指令的响应验证
- 验证设备是否正确进入TID读取模式

### 4. TID计数验证测试
```bash
python test_tid_count_verification.py
```
- 测试TID计数验证功能
- 测试连续读取相同TID的稳定性

### 5. 应答模式TID读取测试
```bash
python test_response_mode_tid.py
```
- 测试应答模式下的TID读取
- 对比单次读取与计数验证的效果

### 6. TID模式进入测试
```bash
python test_tid_mode_entry.py
```
- 测试TID模式进入和响应验证
- 测试串口数据监听功能
- 验证新的工作流程

### 7. RFID工具测试
```bash
python rfid_util.py
```
- 修改 `test_option = 5` 来测试TID计数验证功能

## 配置要求

### 硬件要求
- RFID读卡器设备
- 正确的串口连接
- 兼容的RFID标签

### 软件要求
```bash
pip install pyserial
```

### 配置文件
创建 `simple_config.py` 或使用 `config/config_manager.py`:
```python
RFID_CONFIG = {
    "rfid_port": "COM4",        # 修改为实际串口
    "rfid_baudrate": 115200,    # 波特率
    "rfid_timeout": 0.5,        # 超时时间
}
```

## 集成到数据记录软件

### 修改 data_recorder.py
在数据记录软件中集成TID自动读取功能：

```python
# 在 DataRecorderApp 类中添加
def auto_get_tid(self):
    """自动获取TID"""
    try:
        from rfid_util import rfid_util
        
        # 显示读取状态
        self.tid_var.set("正在读取...")
        self.root.update()
        
        # 读取TID
        tid = rfid_util.read_single_tid(timeout=5.0)
        
        if tid:
            self.tid_var.set(tid)
            messagebox.showinfo("成功", f"成功读取TID: {tid}")
        else:
            self.tid_var.set("")
            messagebox.showwarning("警告", "未读取到TID，请检查设备连接和标签位置")
            
    except ImportError:
        messagebox.showerror("错误", "RFID模块不可用")
    except Exception as e:
        self.tid_var.set("")
        messagebox.showerror("错误", f"读取TID失败: {e}")
```

### 启用自动获取按钮
```python
# 修改按钮状态
ttk.Button(tid_frame, text="自动获取", command=self.auto_get_tid).grid(row=0, column=1, padx=(5, 0))
```

## 注意事项

1. **设备连接**: 确保RFID设备正确连接并配置正确的串口
2. **标签距离**: 标签需要在读卡器的有效读取范围内
3. **工作模式**: 函数使用应答模式进行单次TID读取，每次调用完成后自动停止
4. **读取间隔**: 应答模式下读取间隔为0.1秒，确保设备有足够时间响应
5. **线程安全**: 在GUI应用中使用时注意线程安全
6. **资源清理**: 使用完毕后记得关闭连接

## 故障排除

### 常见问题

1. **设备连接失败**
   - 检查串口号是否正确
   - 检查设备是否被其他程序占用
   - 检查波特率设置

2. **读取不到TID**
   - 检查标签是否在读取范围内
   - 检查标签是否支持TID读取
   - 检查设备天线连接

3. **读取超时**
   - 增加超时时间
   - 检查设备响应是否正常
   - 检查标签质量

### 调试信息
程序会输出详细的调试信息，包括：
- 设备连接状态
- 模式切换过程
- 原始数据帧
- TID解析结果

查看控制台输出可以帮助诊断问题。
