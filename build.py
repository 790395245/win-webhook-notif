import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义图标文件路径
icon_path = os.path.join(current_dir, 'icon.ico')

# 定义打包参数
pyinstaller_args = [
    'client.py',  # 主程序文件
    '--name=Webhook通知客户端',  # 可执行文件名称
    '--onefile',  # 打包成单个文件
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不询问确认
    '--add-data=README.md;.',  # 添加说明文件
    '--add-data=icon.ico;.',  # 添加图标文件
]

# 如果有图标文件，添加图标参数
if os.path.exists(icon_path):
    pyinstaller_args.append(f'--icon={icon_path}')

# 运行 PyInstaller
PyInstaller.__main__.run(pyinstaller_args) 