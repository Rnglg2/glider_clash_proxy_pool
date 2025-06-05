# glider_clash_proxy_pool

一个非常简单的工具，用于将 Clash 配置文件中的代理服务器转换为在本地不同端口上运行的 Glider 代理池。

## 功能

本项目包含几个脚本，协同工作以实现以下目标：

1.  **转换配置**：将 Clash (YAML格式) 配置文件中的代理列表提取出来。
2.  **创建代理池**：为每个提取出的代理启动一个独立的 Glider 进程，使其监听在本地不同的端口上。
3.  **测试代理**：提供工具来测试在本地启动的这些代理的可用性。

## 组件

*   `glider.exe`: 核心的代理程序 (项目地址: [https://github.com/nadoo/glider](https://github.com/nadoo/glider))。
*   `clash-yml_to_glider-conf.py`:
    *   读取 Clash YAML 配置文件 (例如 `config.yaml`)。
    *   提取 `proxies` 部分的代理信息 (支持 `ss`, `vmess`, `trojan` 类型)。
    *   将这些代理转换为 Glider 的转发规则，并保存到 `glider.conf` 文件中 (每行一个规则)。
*   `proxy_pool_creator.py`:
    *   读取 `glider.conf` 文件。
    *   用户输入起始端口和端口步长。
    *   为 `glider.conf` 中的每一条规则，在本地启动一个 `glider.exe` 实例，监听在计算出的独立端口上 (例如 `127.0.0.1:10000`, `127.0.0.1:10001`, ...)。
    *   程序运行时会保持这些 Glider 进程，按 `Ctrl+C` 可以退出并清理所有 Glider 进程和临时文件。
*   `proxy_tester.py`:
    *   用户输入要测试的本地端口范围、步长和代理类型 (通常是 `socks5`，因为 Glider 默认以 SOCKS5 模式转发)。
    *   并发测试指定范围内的本地代理是否可用，并显示结果 (IP, 延迟)。

## 使用流程

1.  **准备 Clash 配置文件**: 确保你有一个 Clash YAML 配置文件 (例如，命名为 `my_clash_config.yaml`)，其中包含了你想要使用的代理服务器列表。
2.  **转换配置**:
    ```bash
    python clash-yml_to_glider-conf.py my_clash_config.yaml -o glider.conf
    ```
    这会生成 `glider.conf` 文件。
3.  **创建代理池**:
    ```bash
    python proxy_pool_creator.py
    ```
    程序会提示你输入起始端口 (例如 `10000`) 和端口步长 (例如 `1`)。然后，它会为 `glider.conf` 中的每个代理启动一个 Glider 实例。
4.  **测试代理 (可选)**:
    打开新的终端窗口，运行：
    ```bash
    python proxy_tester.py
    ```
    根据 `proxy_pool_creator.py` 运行时使用的起始端口、代理数量和步长，输入相应的端口范围进行测试。例如，如果起始端口是 10000，有 5 个代理，步长是 1，那么结束端口就是 10004。

## 依赖

*   Python 3
*   `glider.exe` (需要放置在与脚本相同的目录下)
*   Python 库:
    *   `PyYAML`: 用于解析 Clash 配置文件。可以通过 `pip install PyYAML` 安装。
    *   `requests`: 用于 `proxy_tester.py` 测试代理。可以通过 `pip install requests` 安装。
    *   `PySocks`: `proxy_tester.py` 测试 SOCKS 代理时需要。可以通过 `pip install PySocks` 安装。

    (如果 `proxy_tester.py` 检测到 `PySocks` 未安装，它会尝试自动安装。)

## 注意

*   确保 `glider.exe` 与 Python 脚本在同一目录下，或者 `glider.exe` 在系统的 PATH 环境变量中。当前脚本设计为 `glider.exe` 在同级目录。
*   `proxy_pool_creator.py` 会在运行时创建一个 `tmp` 目录来存放临时的配置文件和 Glider 可执行文件的副本，程序退出时会自动清理该目录。

## 相关链接

*   **Glider GitHub**: [https://github.com/nadoo/glider](https://github.com/nadoo/glider) 