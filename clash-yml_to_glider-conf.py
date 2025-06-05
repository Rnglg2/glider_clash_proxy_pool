import yaml
import json
import argparse
import sys


def parse_config(array: list):
    ss = []
    vmess = []
    trojan = []

    for node in array:
        if node['type'] == 'ss':
            node = f"{node['type']}://{node['cipher']}:{node['password']}@{node['server']}:{node['port']}#{node['name']}"
            ss.append(node)
        elif node['type'] == 'vmess':
            node = f"{node['type']}://none:{node['uuid']}@{node['server']}:{node['port']}?alterID={node['alterId']}"
            vmess.append(node)
        elif node['type'] == 'trojan':
            node = f"{node['type']}://{node['password']}@{node['server']}:{node['port']}?sni={node.get('sni', '')}&skipVerify={str(node.get('skip-cert-verify', True)).lower()}"
            trojan.append(node)

    result = []
    for node in ss:
        result.append(f'forward={node}')
    for node in vmess:
        result.append(f'forward={node}')
    for node in trojan:
        result.append(f'forward={node}')
    
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='解析配置文件并生成 glider.conf')
    parser.add_argument('input_file', help='输入的配置文件路径')
    parser.add_argument('-o', '--output', default='glider.conf', help='输出的 glider.conf 文件路径')
    
    args = parser.parse_args()
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            list_array = config['proxies']
            result = parse_config(list_array)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
            
        print(f'成功生成 {args.output} 文件')
    except FileNotFoundError:
        print(f'错误: 找不到文件 "{args.input_file}"')
        sys.exit(1)
    except KeyError as e:
        print(f'错误: 配置文件格式不正确，缺少键 "{e}"')
        sys.exit(1)
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)


