#!/usr/bin/env python3
"""
裁剪SVG文件，只保留左侧的logo图片
"""

import os
import xml.etree.ElementTree as ET


def crop_svg_logo(left_percent=0, top_percent=0, right_percent=100, bottom_percent=100):
    """
    裁剪SVG文件，可自定义裁剪区域

    参数:
    left_percent: 左边界百分比 (0-100)
    top_percent: 上边界百分比 (0-100)
    right_percent: 右边界百分比 (0-100)
    bottom_percent: 下边界百分比 (0-100)

    例如: crop_svg_logo(0, 0, 60, 100) 表示保留左侧60%的区域
    """
    svg_path = os.path.join("images", "logo.svg")

    if not os.path.exists(svg_path):
        print(f"✗ 未找到SVG文件: {svg_path}")
        return False

    # 验证参数
    if not (0 <= left_percent < right_percent <= 100):
        print("✗ 错误: 左边界必须小于右边界，且都在0-100范围内")
        return False

    if not (0 <= top_percent < bottom_percent <= 100):
        print("✗ 错误: 上边界必须小于下边界，且都在0-100范围内")
        return False

    try:
        # 读取原始SVG文件
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        print(f"✓ 读取SVG文件: {svg_path}")

        # 解析SVG
        root = ET.fromstring(svg_content)

        # 获取原始viewBox
        viewbox = root.get('viewBox', '0 0 137 71')
        viewbox_parts = viewbox.split()

        if len(viewbox_parts) == 4:
            orig_x, orig_y, orig_width, orig_height = map(float, viewbox_parts)
            print(f"原始viewBox: {orig_x} {orig_y} {orig_width} {orig_height}")

            # 计算新的viewBox坐标和尺寸
            new_x = orig_x + (orig_width * left_percent / 100)
            new_y = orig_y + (orig_height * top_percent / 100)
            new_width = orig_width * (right_percent - left_percent) / 100
            new_height = orig_height * (bottom_percent - top_percent) / 100

            new_viewbox = f"{new_x} {new_y} {new_width} {new_height}"

            print(f"裁剪区域: 左{left_percent}% 上{top_percent}% 右{right_percent}% 下{bottom_percent}%")
            print(f"新的viewBox: {new_x} {new_y} {new_width} {new_height}")

            # 更新viewBox
            root.set('viewBox', new_viewbox)

            # 更新width和height属性（如果存在）
            if 'width' in root.attrib:
                root.set('width', str(int(new_width)))
            if 'height' in root.attrib:
                root.set('height', str(int(new_height)))
        
        # 创建新的SVG内容
        new_svg_content = ET.tostring(root, encoding='unicode')
        
        # 添加XML声明和命名空间
        new_svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + new_svg_content
        
        # 保存裁剪后的SVG
        cropped_path = os.path.join("images", "logo_cropped.svg")
        with open(cropped_path, 'w', encoding='utf-8') as f:
            f.write(new_svg_content)
        
        print(f"✓ 裁剪后的SVG已保存: {cropped_path}")
        
        # 替换原文件
        backup_path = os.path.join("images", "logo_original.svg")
        os.rename(svg_path, backup_path)
        os.rename(cropped_path, svg_path)
        
        print(f"✓ 原文件已备份为: {backup_path}")
        print(f"✓ 裁剪后的文件已替换原文件")
        
        return True
        
    except Exception as e:
        print(f"✗ 裁剪SVG失败: {e}")
        return False


def create_simple_logo():
    """创建一个简单的logo SVG文件"""
    try:
        # 创建一个简单的logo
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 71" width="80" height="71">
  <defs>
    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2E86AB;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#A23B72;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 外框 -->
  <rect x="5" y="5" width="70" height="61" rx="8" ry="8" 
        fill="url(#logoGradient)" stroke="#1a5490" stroke-width="2"/>
  
  <!-- 表格图标 -->
  <g fill="white" stroke="white" stroke-width="1">
    <!-- 水平线 -->
    <line x1="15" y1="25" x2="65" y2="25"/>
    <line x1="15" y1="35" x2="65" y2="35"/>
    <line x1="15" y1="45" x2="65" y2="45"/>
    <line x1="15" y1="55" x2="65" y2="55"/>
    
    <!-- 垂直线 -->
    <line x1="25" y1="15" x2="25" y2="60"/>
    <line x1="40" y1="15" x2="40" y2="60"/>
    <line x1="55" y1="15" x2="55" y2="60"/>
  </g>
  
  <!-- 相机图标表示图片 -->
  <g fill="white" stroke="white" stroke-width="1">
    <rect x="45" y="40" width="15" height="10" rx="2" ry="2"/>
    <circle cx="52.5" cy="45" r="3" fill="none"/>
    <circle cx="52.5" cy="45" r="1.5"/>
  </g>
  
  <!-- 文字 TID -->
  <text x="20" y="20" font-family="Arial, sans-serif" font-size="8" font-weight="bold" fill="white">TID</text>
</svg>'''
        
        # 保存新的logo
        logo_path = os.path.join("images", "logo_simple.svg")
        with open(logo_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✓ 简单logo已创建: {logo_path}")
        return logo_path
        
    except Exception as e:
        print(f"✗ 创建简单logo失败: {e}")
        return None


def get_crop_parameters():
    """获取用户输入的裁剪参数"""
    print("\n请输入裁剪区域的边界百分比 (0-100):")
    print("提示: 0表示最左/最上，100表示最右/最下")
    print("例如: 左0 上0 右60 下100 表示保留左侧60%的区域")

    try:
        left = float(input("左边界百分比 (默认0): ") or "0")
        top = float(input("上边界百分比 (默认0): ") or "0")
        right = float(input("右边界百分比 (默认100): ") or "100")
        bottom = float(input("下边界百分比 (默认100): ") or "100")

        return left, top, right, bottom
    except ValueError:
        print("✗ 输入格式错误，使用默认值")
        return 0, 0, 100, 100


def show_presets():
    """显示预设的裁剪选项"""
    print("\n预设裁剪选项:")
    print("1. 保留左侧30% (0, 0, 30, 100)")
    print("2. 保留左侧50% (0, 0, 50, 100)")
    print("3. 保留左侧60% (0, 0, 60, 100)")
    print("4. 保留右侧50% (50, 0, 100, 100)")
    print("5. 保留上半部分 (0, 0, 100, 50)")
    print("6. 保留下半部分 (0, 50, 100, 100)")
    print("7. 保留中心区域 (25, 25, 75, 75)")
    print("8. 自定义输入")
    print("9. 使用默认值 (0, 0, 100, 100)")

    try:
        choice = input("\n请选择 (1-9): ").strip()

        presets = {
            '1': (0, 0, 30, 100),
            '2': (0, 0, 50, 100),
            '3': (0, 0, 60, 100),
            '4': (50, 0, 100, 100),
            '5': (0, 0, 100, 50),
            '6': (0, 50, 100, 100),
            '7': (25, 25, 75, 75),
            '8': None,  # 自定义输入
            '9': (0, 0, 100, 100)
        }

        if choice in presets:
            if choice == '8':
                return get_crop_parameters()
            else:
                return presets[choice]
        else:
            print("✗ 无效选择，使用默认值")
            return 0, 0, 100, 100

    except KeyboardInterrupt:
        print("\n✗ 用户取消操作")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("SVG Logo裁剪工具 - 可自定义裁剪区域")
    print("=" * 60)

    # 确保images目录存在
    os.makedirs('images', exist_ok=True)

    # 检查是否存在原始SVG文件
    svg_path = os.path.join("images", "logo.svg")
    if not os.path.exists(svg_path):
        print(f"\n✗ 未找到SVG文件: {svg_path}")
        print("正在创建简单的logo...")
        simple_logo = create_simple_logo()

        if simple_logo:
            import shutil
            shutil.copy2(simple_logo, svg_path)
            print(f"✓ 简单logo已创建: {svg_path}")
        else:
            print("✗ 无法创建logo文件")
            return

    # 显示当前SVG信息
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        root = ET.fromstring(content)
        viewbox = root.get('viewBox', '0 0 137 71')
        print(f"\n当前SVG viewBox: {viewbox}")
    except:
        print("\n无法读取当前SVG信息")

    # 获取裁剪参数
    params = show_presets()
    if params is None:
        return

    left, top, right, bottom = params
    print(f"\n使用裁剪参数: 左{left}% 上{top}% 右{right}% 下{bottom}%")

    # 执行裁剪
    print("\n开始裁剪SVG...")
    success = crop_svg_logo(left, top, right, bottom)

    print("\n" + "=" * 60)

    if success:
        print("✓ Logo裁剪完成！")
        print("现在可以在数据记录软件中使用新的logo了")
        print(f"原始文件已备份为: images/logo_original.svg")
    else:
        print("✗ Logo裁剪失败")


if __name__ == "__main__":
    main()
