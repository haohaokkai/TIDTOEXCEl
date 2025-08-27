# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 1) 收集 rapidocr_onnxruntime 的数据文件
rapidocr_datas = collect_data_files(
    'rapidocr_onnxruntime',
    includes=[
        '*.yaml', '*.yml', '*.onnx', '*.txt', '*.json',
        '**/*.yaml', '**/*.yml', '**/*.onnx', '**/*.txt', '**/*.json'
    ]
)

# 新增：打印原始路径，看看 dest 本来长什么样
print("=== 原始 rapidocr_datas 路径 ===")
for src, dest in rapidocr_datas[:2]:  # 只打印前2个，避免输出太多
    print(f"src: {src}")
    print(f"dest: {dest}")
    print("---")

# 2) 不手动加 _internal，直接用原始 dest（关键修改！）
rapidocr_datas_prefixed = rapidocr_datas  # 直接用收集到的原始路径，不做替换

# 3) 收集子模块
rapidocr_hiddenimports = collect_submodules('rapidocr_onnxruntime')

a = Analysis(
    ['data_recorder.py'],
    pathex=[],
    binaries=[],
    datas=rapidocr_datas_prefixed + [
        ('images/*', 'images'),  # 图片资源
        ('config/config.json', '.'),  # 配置文件到根目录，运行时会复制到 _internal
    ],
    hiddenimports=rapidocr_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TIDtoExcel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TIDtoExcel',
)