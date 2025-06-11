import socketio
from winotify import Notification, audio
import sys
import time
import logging
import argparse
import pystray
from PIL import Image
import threading
import os
import pyperclip
import subprocess
from datetime import datetime
import msvcrt
import traceback

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 创建logs目录（如果不存在）
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志
log_filename = os.path.join('logs', f'client_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建Socket.IO客户端
sio = socketio.Client()

# 全局变量
icon = None
is_connected = False

def on_quit(icon):
    """退出程序"""
    logger.info('正在退出程序...')
    if is_connected:
        sio.disconnect()
    icon.stop()
    return 0

def on_show_status(icon):
    """显示连接状态"""
    status = "已连接" if is_connected else "未连接"
    server_url = sio.connection_url if is_connected else "未连接"
    toast = Notification(
        app_id="Webhook通知客户端",
        title="连接状态",
        msg=f"当前状态: {status}\n服务器地址: {server_url}",
        duration="short"
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()
    return 0

def get_server_url():
    """获取服务器地址"""
    while True:
        server_url = input("请输入服务器地址 (例如: http://192.168.1.100:59999): ").strip()
        if server_url:
            return server_url
        print("服务器地址不能为空，请重新输入！")

@sio.event
def connect():
    """连接成功时的回调"""
    global is_connected
    is_connected = True
    logger.info('已连接到服务器')

@sio.event
def disconnect():
    """断开连接时的回调"""
    global is_connected
    is_connected = False
    logger.info('与服务器断开连接')
    print("与服务器的连接已断开")

@sio.on('notification')
def on_notification(data):
    """接收通知时的回调"""
    logger.info(f'收到通知: {data}')
    
    # 显示Windows通知
    title = data.get('title', '新通知')
    message = data.get('message', str(data))
    
    # 创建通知
    toast = Notification(
        app_id="Webhook通知客户端",
        title=title,
        msg=message,
        duration="long"
    )
    
    # 设置通知音频
    toast.set_audio(audio.Default, loop=False)
    
    # 复制内容到剪贴板
    try:
        pyperclip.copy(message)
        logger.info(f'已复制内容到剪贴板: {message}')
        # 在通知消息中添加提示
        toast.msg = f"{message}\n\n(已自动复制到剪贴板)"
    except Exception as e:
        logger.error(f'复制到剪贴板失败: {str(e)}')
    
    # 显示通知
    toast.show()

def run_socket_client(server_url):
    """运行Socket客户端"""
    global is_connected
    while True:
        try:
            if not is_connected:
                logger.info(f'正在连接到服务器: {server_url}')
                print(f"正在连接到服务器: {server_url}")
                sio.connect(server_url)
            time.sleep(1)
        except Exception as e:
            logger.error(f'连接错误: {str(e)}')
            print(f"连接错误: {str(e)}")
            is_connected = False
            time.sleep(5)  # 等待5秒后重试

def run_background():
    """在后台运行系统托盘图标"""
    global icon
    icon.run()

def test_connection(server_url):
    """测试与服务器的连接"""
    try:
        # 尝试连接服务器
        sio.connect(server_url, wait_timeout=5)
        # 连接成功后断开
        sio.disconnect()
        logger.info(f'连接测试成功')
    except Exception as e:
        logger.error(f'连接测试失败: {str(e)}')
        raise ConnectionError(f'无法连接到服务器: {str(e)}')

def is_process_running():
    """检查是否已有实例在运行"""
    if sys.platform == 'win32':
        import psutil
        process_name = "Webhook通知客户端.exe" if getattr(sys, 'frozen', False) else "python.exe"
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] == process_name:
                    # 检查命令行参数
                    cmdline = proc.info['cmdline']
                    if cmdline and len(cmdline) > 1 and '--background' in cmdline:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return False

def main():
    """主函数"""
    # 检查是否已有实例在运行
    if is_process_running():
        print("Webhook通知客户端已在后台运行！")
        print("请查看系统托盘图标。")
        print("=" * 50)
        input("\n按回车键退出...")
        sys.exit(0)

    print("欢迎使用Webhook通知客户端！")
    print("=" * 50)
    
    # 获取服务器地址
    server_url = get_server_url()
    print(f"正在启动客户端，服务器地址: {server_url}")
    print("=" * 50)

    test_connection(server_url)
        
    # 连接成功后显示信息
    print("\n已成功连接到服务器！")
    print("\n程序即将在后台运行，您可以：")
    print("1. 在系统托盘中找到Webhook通知客户端图标")
    print("2. 右键点击图标可以查看状态或退出程序")
    print("3. 按回车键关闭此窗口（程序会继续在后台运行）")
    print("\n日志文件保存在 logs 目录下")
    print("=" * 50)
    
    # 等待用户按回车
    input("\n按回车键关闭此窗口...")

    # 启动后台进程
    if sys.platform == 'win32':
        # 启动后台进程
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            exe_path = sys.executable
            logger.info(f'启动后台进程: {exe_path}')
            
            # 使用完整路径启动进程
            process = subprocess.Popen(
                [exe_path, '--background', server_url],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                shell=True
            )
            
            # 等待一小段时间确保进程启动
            time.sleep(1)
            
            # 检查进程是否成功启动
            if process.poll() is not None:
                logger.error(f'后台进程启动失败，返回码: {process.returncode}')
            else:
                logger.info('后台进程启动成功')
        else:
            # 如果是开发环境，使用pythonw.exe
            python_exe = sys.executable
            if python_exe.endswith('python.exe'):
                pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
                if os.path.exists(pythonw_exe):
                    python_exe = pythonw_exe
            
            logger.info(f'启动后台进程: {python_exe}')
            process = subprocess.Popen(
                [python_exe, sys.argv[0], '--background', server_url],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                shell=True
            )
            
            # 等待一小段时间确保进程启动
            time.sleep(1)
            
            # 检查进程是否成功启动
            if process.poll() is not None:
                logger.error(f'后台进程启动失败，返回码: {process.returncode}')
            else:
                logger.info('后台进程启动成功')
    else:
        # 在Unix系统上使用nohup
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.executable
        logger.info(f'启动后台进程: {exe_path}')
        process = subprocess.Popen(
            ['nohup', exe_path, '--background', server_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # 等待一小段时间确保进程启动
        time.sleep(1)
        
        # 检查进程是否成功启动
        if process.poll() is not None:
            logger.error(f'后台进程启动失败，返回码: {process.returncode}')
        else:
            logger.info('后台进程启动成功')
    
    # 立即退出当前进程
    logger.info('程序已在后台运行')
    os._exit(0)

if __name__ == '__main__':
    try:
        # 检查是否是后台模式
        if len(sys.argv) > 1 and sys.argv[1] == '--background':
            server_url = sys.argv[2]
            # 创建系统托盘图标
            icon = pystray.Icon("webhook_client")
            icon_path = get_resource_path('icon.ico')
            icon.icon = Image.open(icon_path)
            icon.title = "Webhook通知客户端"
            icon.menu = pystray.Menu(
                pystray.MenuItem("状态", on_show_status, default=True),
                pystray.MenuItem("退出", on_quit)
            )
            # 在新线程中运行Socket客户端
            client_thread = threading.Thread(
                target=run_socket_client,
                args=(server_url,),
                daemon=True
            )
            client_thread.start()
            # 运行系统托盘图标
            icon.run()
        else:
            main()
    except SystemExit:
        # 正常退出，不需要记录错误
        pass
    except:
        logger.error(f"程序发生错误: {traceback.format_exc()}")