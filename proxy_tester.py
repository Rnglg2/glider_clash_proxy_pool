import os
import requests
import json
import time
import concurrent.futures
from urllib.parse import urlparse
test_url="https://api.ipify.org/?format=json"
def test_proxy(proxy_url, test_url="https://api.ipify.org/?format=json", timeout=10, proxy_type="socks5"):
    """
    测试代理是否可用
    
    参数:
        proxy_url: 代理地址，格式为 host:port
        test_url: 测试URL
        timeout: 超时时间（秒）
        proxy_type: 代理类型，可选 'http', 'socks4', 'socks5'
    
    返回:
        成功: (True, IP地址, 响应时间)
        失败: (False, 错误信息, None)
    """
    # 解析代理地址
    if "://" in proxy_url:
        # 如果已经包含协议，直接使用
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    else:
        # 否则添加协议前缀
        proxies = {
            "http": f"{proxy_type}://{proxy_url}",
            "https": f"{proxy_type}://{proxy_url}"
        }
    
    try:
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            try:
                data = response.json()
                return True, data.get("ip", "未知IP"), elapsed
            except json.JSONDecodeError:
                return False, "解析JSON失败", None
        else:
            return False, f"HTTP错误: {response.status_code}", None
    
    except requests.exceptions.ConnectTimeout:
        return False, "连接超时", None
    except requests.exceptions.ReadTimeout:
        return False, "读取超时", None
    except requests.exceptions.ProxyError:
        return False, "代理错误", None
    except requests.exceptions.SSLError:
        return False, "SSL错误", None
    except Exception as e:
        return False, f"未知错误: {str(e)}", None

def scan_local_proxies(start_port, end_port, step=1, host="127.0.0.1", proxy_type="socks5"):
    """
    扫描本地代理端口
    
    参数:
        start_port: 起始端口
        end_port: 结束端口
        step: 端口步长
        host: 代理主机地址
        proxy_type: 代理类型，可选 'http', 'socks4', 'socks5'
    """
    ports = range(start_port, end_port + 1, step)
    proxy_urls = [f"{host}:{port}" for port in ports]
    
    print(f"开始测试 {len(proxy_urls)} 个 {proxy_type} 代理...")
    print("-" * 70)
    print(f"{'代理地址':<25} {'状态':<8} {'IP地址':<20} {'响应时间':<10}")
    print("-" * 70)
    
    # 使用线程池并行测试代理
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {
            executor.submit(test_proxy, proxy_url, test_url, 10, proxy_type): proxy_url 
            for proxy_url in proxy_urls
        }
        
        success_count = 0
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy_url = future_to_proxy[future]
            success, result, elapsed = future.result()
            
            if success:
                success_count += 1
                status = "✓ 成功"
                elapsed_str = f"{elapsed:.2f}秒"
            else:
                status = "✗ 失败"
                elapsed_str = "-"
            
            print(f"{proxy_type}://{proxy_url:<25} {status:<8} {str(result):<20} {elapsed_str:<10}")
    
    print("-" * 70)
    print(f"测试完成: {success_count}/{len(proxy_urls)} 个代理可用")
    return success_count

def main():
    print("代理池测试工具")
    print("=" * 30)
    print("此工具将测试本地代理是否可以正常连接到互联网")
    print(f"测试地址:{test_url}")
    print("=" * 30)
    
    try:
        start_port = int(input("请输入起始端口: "))
        end_port = int(input("请输入结束端口: "))
        step = int(input("请输入端口步长 (默认为1): ") or "1")
        
        proxy_type = input("请输入代理类型 (socks5/socks4/http, 默认为socks5): ").lower() or "socks5"
        if proxy_type not in ["socks5", "socks4", "http"]:
            print(f"错误: 不支持的代理类型 '{proxy_type}'，使用默认值 'socks5'")
            proxy_type = "socks5"
        
        if start_port < 1 or start_port > 65535 or end_port < 1 or end_port > 65535:
            print("错误: 端口必须在 1-65535 之间")
            return
            
        if step < 1:
            print("错误: 步长必须大于 0")
            return
            
        if start_port > end_port:
            start_port, end_port = end_port, start_port
        
        # 检查是否安装了PySocks库
        try:
            import socks
        except ImportError:
            print("警告: 未检测到PySocks库，尝试安装...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "PySocks"])
                print("PySocks安装成功!")
            except Exception as e:
                print(f"安装PySocks失败: {e}")
                print("请手动安装PySocks: pip install PySocks")
                return
        
        # 开始测试
        scan_local_proxies(start_port, end_port, step, "127.0.0.1", proxy_type)
        
    except ValueError:
        print("错误: 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    import sys
    main() 