# Excel错误处理优化说明

## 问题描述

原来的错误提示显示技术性错误信息：
```
导出失败：[Errno 13] Permission denied: 'E:/package/TIDtoExcel/0820.xlsx'
```

用户看到这样的错误信息可能不知道如何解决问题。

## 优化方案

将权限拒绝错误改为更友好的提示，明确告诉用户问题原因和解决方法。

## 修改内容

### 1. Excel导出错误处理 (`export_to_excel` 方法)

**位置**: 第1019-1028行

**修改前**:
```python
except Exception as e:
    messagebox.showerror("错误", f"导出失败：{str(e)}")
```

**修改后**:
```python
except PermissionError as e:
    # 权限错误，通常是文件被其他程序打开
    messagebox.showerror("错误", f"无法保存Excel文件，文件可能已在Excel或其他程序中打开。\n\n请关闭相关程序后重试。\n\n文件路径：{excel_file}")
except Exception as e:
    # 检查是否是权限相关的错误
    error_msg = str(e).lower()
    if "permission denied" in error_msg or "errno 13" in error_msg:
        messagebox.showerror("错误", f"无法保存Excel文件，文件可能已在Excel或其他程序中打开。\n\n请关闭相关程序后重试。\n\n文件路径：{excel_file}")
    else:
        messagebox.showerror("错误", f"导出失败：{str(e)}")
```

### 2. Excel文件创建错误处理 (`create_excel_for_export` 方法)

**位置**: 第1064-1075行

**修改前**:
```python
except Exception as e:
    messagebox.showerror("错误", f"创建Excel文件失败：{str(e)}")
    return None
```

**修改后**:
```python
except PermissionError as e:
    # 权限错误，通常是文件被其他程序打开
    messagebox.showerror("错误", f"无法创建Excel文件，目标位置可能没有写入权限或文件已被占用。\n\n请检查文件路径权限或选择其他位置。\n\n文件路径：{file_path}")
    return None
except Exception as e:
    # 检查是否是权限相关的错误
    error_msg = str(e).lower()
    if "permission denied" in error_msg or "errno 13" in error_msg:
        messagebox.showerror("错误", f"无法创建Excel文件，目标位置可能没有写入权限或文件已被占用。\n\n请检查文件路径权限或选择其他位置。\n\n文件路径：{file_path}")
    else:
        messagebox.showerror("错误", f"创建Excel文件失败：{str(e)}")
    return None
```

### 3. Excel文件打开错误处理 (`select_excel_for_export` 方法)

**位置**: 第1094-1105行

**修改前**:
```python
except Exception as e:
    messagebox.showerror("错误", f"打开Excel文件失败：{str(e)}")
    return None
```

**修改后**:
```python
except PermissionError as e:
    # 权限错误，通常是文件被其他程序打开
    messagebox.showerror("错误", f"无法打开Excel文件，文件可能已在Excel或其他程序中打开。\n\n请关闭相关程序后重试。\n\n文件路径：{file_path}")
    return None
except Exception as e:
    # 检查是否是权限相关的错误
    error_msg = str(e).lower()
    if "permission denied" in error_msg or "errno 13" in error_msg:
        messagebox.showerror("错误", f"无法打开Excel文件，文件可能已在Excel或其他程序中打开。\n\n请关闭相关程序后重试。\n\n文件路径：{file_path}")
    else:
        messagebox.showerror("错误", f"打开Excel文件失败：{str(e)}")
    return None
```

## 错误识别逻辑

程序会通过以下方式识别权限相关错误：

1. **直接捕获 `PermissionError`** - Python的标准权限错误异常
2. **检查错误消息内容** - 查找以下关键词：
   - `"permission denied"` (不区分大小写)
   - `"errno 13"` (Linux/Windows权限错误代码)

## 友好错误消息格式

### 导出/保存文件时的权限错误
```
无法保存Excel文件，文件可能已在Excel或其他程序中打开。

请关闭相关程序后重试。

文件路径：E:/package/TIDtoExcel/0820.xlsx
```

### 创建文件时的权限错误
```
无法创建Excel文件，目标位置可能没有写入权限或文件已被占用。

请检查文件路径权限或选择其他位置。

文件路径：E:/package/TIDtoExcel/new_file.xlsx
```

### 打开文件时的权限错误
```
无法打开Excel文件，文件可能已在Excel或其他程序中打开。

请关闭相关程序后重试。

文件路径：E:/package/TIDtoExcel/existing_file.xlsx
```

## 优化效果

### 优化前
- ❌ 显示技术性错误信息：`[Errno 13] Permission denied`
- ❌ 用户不知道如何解决问题
- ❌ 没有明确指出问题原因

### 优化后
- ✅ 显示友好的错误描述
- ✅ 明确指出可能的原因（文件被其他程序打开）
- ✅ 提供具体的解决建议（关闭相关程序）
- ✅ 显示具体的文件路径
- ✅ 保留其他类型错误的原始信息

## 常见使用场景

1. **Excel文件在Microsoft Excel中打开** - 用户忘记关闭Excel程序
2. **文件被其他程序占用** - 文件管理器、文本编辑器等程序正在使用文件
3. **目标文件夹权限不足** - 尝试保存到系统文件夹或只读文件夹
4. **文件属性为只读** - 文件被设置为只读属性

## 测试建议

1. 在Excel中打开一个.xlsx文件，然后尝试导出到同一个文件
2. 将文件设置为只读属性，然后尝试导出
3. 尝试导出到没有写入权限的文件夹
4. 测试其他类型的错误是否仍显示原始错误信息
