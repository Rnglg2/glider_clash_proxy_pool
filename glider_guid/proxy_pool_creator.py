import os
import shutil
import sys
import subprocess
import signal
import atexit
import time

# 全局变量，存储所有启动的进程
processes = []

def cleanup():
    """
    清理函数，终止所有进程并删除tmp目录
    """
    print("\n正在清理资源...")
    
    # 终止所有进程
    for process in processes:
        try:
            if process.poll() is None:  # 如果进程仍在运行
                process.terminate()
                # 给进程一些时间来终止
                time.sleep(0.2)
                if process.poll() is None:  # 如果进程仍未终止
                    process.kill()
        except Exception as e:
            print(f"终止进程时出错: {e}")
    
    # 删除tmp目录
    tmp_dir = "tmp"
    if os.path.exists(tmp_dir):
        try:
            shutil.rmtree(tmp_dir)
            print(f"已删除目录: {tmp_dir}")
        except Exception as e:
            print(f"删除目录时出错: {e}")

def signal_handler(sig, frame):
    """
    信号处理函数，用于捕获Ctrl+C
    """
    print("\n接收到终止信号，正在退出...")
    sys.exit(0)

def create_proxy_pool(start_port, step, config_file="glider.conf"):
    """
    创建代理池
    
    参数:
        start_port: 起始端口
        step: 端口步长
        config_file: 配置文件路径
    """
    # 创建tmp目录
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        print(f"创建目录: {tmp_dir}")
    
    # 读取配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config_lines = f.readlines()
    
    # 过滤空行
    config_lines = [line.strip() for line in config_lines if line.strip()]
    
    print(f"正在启动 {len(config_lines)} 个代理...")
    
    # 为每一行配置创建单独的配置文件和可执行文件，并启动进程
    for i, line in enumerate(config_lines):
        # 计算端口
        port = start_port + i * step
        
        # 创建配置文件
        conf_file = os.path.join(tmp_dir, f"glider-{port}.conf")
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(line)
        
        # 复制glider.exe
        exe_file = os.path.join(tmp_dir, f"glider-{port}.exe")
        shutil.copy("glider.exe", exe_file)
        
        # 启动进程
        try:
            process = subprocess.Popen(
                [exe_file, "--config", conf_file, "-listen", f"0.0.0.0:{port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # 在Windows上隐藏窗口
            )
            processes.append(process)
            print(f"启动代理 {port}: {line[:50]}{'...' if len(line) > 50 else ''}")
        except Exception as e:
            print(f"启动代理 {port} 失败: {e}")
    
    print(f"\n所有代理已启动! 共 {len(processes)} 个进程")
    print(f"端口范围: {start_port} - {start_port + (len(config_lines) - 1) * step}")
    print("按 Ctrl+C 退出并清理资源")
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

def main():
    print("代理池创建工具")
    print("-" * 30)
    
    # 注册清理函数，在程序退出时执行
    atexit.register(cleanup)
    
    # 注册信号处理函数，捕获Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        start_port = int(input("请输入起始端口 (例如: 10000): "))
        step = int(input("请输入端口步长 (例如: 1): "))
        
        if start_port < 1 or start_port > 65535:
            print("错误: 端口必须在 1-65535 之间")
            return
            
        if step < 1:
            print("错误: 步长必须大于 0")
            return
            
        create_proxy_pool(start_port, step)
        
    except ValueError:
        print("错误: 请输入有效的数字")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main() 