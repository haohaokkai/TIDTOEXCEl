# EPC帧检测功能说明

## 功能概述

在TID读取过程中，如果检测到完整帧的第五个字节为0x20（EPC帧），系统会自动弹窗通知用户重置RFID设备，因为设备可能处于EPC模式而非TID模式。

## 帧格式识别

### 帧结构
```
D9 | LEN | Reserved(2) | CMD | DATA...
0  | 1   | 2-3         | 4   | 5...
```

### 命令码识别
- **0x2D**: TID帧 - 正常的TID读取响应
- **0x20**: EPC帧 - 盘存响应，表示设备处于EPC模式
- **0x2F**: 停止存盘帧 - 控制命令响应

## 实现方案

### 1. 异常类定义

**位置**: `rfid_util.py` 第13-16行

```python
class EpcFrameDetectedException(Exception):
    """检测到EPC帧时抛出的异常，提示需要重置RFID设备"""
    pass
```

### 2. EPC帧检测逻辑

**位置**: `rfid_util.py` 第786-792行

**修改前**:
```python
elif cmd == self.CMD_START_INVENTORY:
    # 使用现有的EPC解析逻辑
    tag_info = self.parse_tag_frame(frame)
    if tag_info and tag_info.get('epc'):
        epc_as_tid = tag_info['epc']
        tids.append(epc_as_tid)
        print(f"[TID解析] 从盘存响应提取EPC作为TID: {epc_as_tid}")
```

**修改后**:
```python
elif cmd == self.CMD_START_INVENTORY:
    print(f"⚠️ [TID解析] 检测到EPC帧(0x{cmd:02X})，设备可能处于EPC模式而非TID模式")
    print(f"💡 [TID解析] 建议执行RFID重置操作：停止存盘->读TID")
    
    # 抛出特殊异常，通知上层需要重置RFID
    raise EpcFrameDetectedException("检测到EPC帧，需要重置RFID设备到TID模式")
```

### 3. 异常处理 - 自动获取TID

**位置**: `data_recorder.py` 第858-865行

```python
except EpcFrameDetectedException as e:
    print(f"⚠️ 检测到EPC帧，需要重置RFID设备: {e}")
    # 在主线程中显示弹窗
    self.root.after(0, self._show_epc_frame_warning)
    return None
except Exception as e:
    print(f"TID读取异常: {e}")
    return None
```

### 4. 异常处理 - 手动获取TID

**位置**: `data_recorder.py` 第507-514行

```python
except EpcFrameDetectedException as e:
    print(f"⚠️ 手动TID读取时检测到EPC帧: {e}")
    # 在主线程中显示弹窗
    self.root.after(0, self._show_epc_frame_warning)
    # 同时更新TID读取状态
    self.root.after(0, self._update_tid_result, None)
except Exception as e:
    self.root.after(0, self._update_tid_error, str(e))
```

### 5. 用户提示对话框

**位置**: `data_recorder.py` 第867-883行

```python
def _show_epc_frame_warning(self):
    """显示EPC帧检测警告"""
    import tkinter.messagebox as messagebox
    result = messagebox.askyesno(
        "RFID设备状态异常", 
        "检测到EPC帧，设备可能处于EPC模式而非TID模式。\n\n"
        "建议执行RFID重置操作：停止存盘->读TID\n\n"
        "是否立即执行RFID重置？",
        icon="warning"
    )
    
    if result:
        # 用户选择执行重置
        self.rfid_reset()
```

## 触发场景

### 1. 手动TID读取
- 用户点击"自动获取"按钮（TID输入框旁边）
- 系统调用 `rfid_util.read_tid_with_count_verification()`
- 如果读取到EPC帧，弹出警告对话框

### 2. 自动批量获取
- 用户点击"开始自动获取"按钮
- 系统在后台持续调用 `get_tid_sync()`
- 如果读取到EPC帧，弹出警告对话框

### 3. RFID重置操作
- 用户点击"RFID重置"按钮
- 系统调用 `rfid_util.read_tid()`
- 如果读取到EPC帧，弹出警告对话框

## 用户交互流程

### 对话框内容
```
标题: RFID设备状态异常
图标: ⚠️ 警告

内容: 
检测到EPC帧，设备可能处于EPC模式而非TID模式。

建议执行RFID重置操作：停止存盘->读TID

是否立即执行RFID重置？

按钮: [是] [否]
```

### 用户选择
1. **选择"是"**:
   - 自动调用 `self.rfid_reset()` 方法
   - 执行"停止存盘->读TID"操作序列
   - 尝试将设备切换到TID模式

2. **选择"否"**:
   - 关闭对话框
   - 用户可以手动处理或稍后重试

## 技术细节

### 帧检测位置
在 `_parse_tid_data()` 方法中，当处理每个帧时：
```python
cmd = frame[4]  # 第五个字节（索引4）
if cmd == self.CMD_START_INVENTORY:  # 0x20
    # 检测到EPC帧，抛出异常
```

### 异常传播路径
```
_parse_tid_data() 
    ↓ 抛出 EpcFrameDetectedException
read_tid_with_count_verification()
    ↓ 异常向上传播
get_tid_sync() / read_tid_thread()
    ↓ 捕获异常
_show_epc_frame_warning()
    ↓ 显示对话框
rfid_reset() (可选)
```

### 线程安全
- 异常在工作线程中抛出
- 使用 `self.root.after(0, ...)` 确保UI更新在主线程中执行
- 避免跨线程的UI操作问题

## 测试验证

### 运行测试程序
```bash
python test_epc_frame_detection.py
```

### 测试内容
1. **TID帧解析** - 验证正常TID帧不会触发异常
2. **EPC帧检测** - 验证EPC帧会正确抛出异常
3. **混合数据处理** - 验证包含多种帧的数据处理
4. **其他帧跳过** - 验证其他命令码帧正常跳过

### 手动测试
1. 确保RFID设备处于EPC模式
2. 点击"自动获取TID"按钮
3. 观察是否弹出EPC帧检测对话框
4. 选择"是"验证是否自动执行重置
5. 验证重置后是否能正常读取TID

## 优势效果

### 用户体验改进
1. **及时提醒**: 立即告知用户设备状态异常
2. **明确指导**: 提供具体的解决方案
3. **一键修复**: 可以直接执行重置操作
4. **避免困惑**: 减少用户反复尝试的挫败感

### 技术优势
1. **自动检测**: 无需用户手动判断设备状态
2. **精确识别**: 基于协议帧格式的准确检测
3. **优雅处理**: 使用异常机制而非返回值判断
4. **线程安全**: 正确处理多线程环境下的UI更新

## 扩展可能

1. **其他异常帧检测**: 可以扩展检测更多异常状态
2. **自动重置**: 可以配置为检测到异常时自动重置
3. **状态记录**: 记录设备状态异常的历史
4. **批量处理**: 在批量操作中智能处理异常状态

这个功能大大提升了用户在使用RFID设备时的体验，避免了因设备模式错误而导致的操作困惑！
