from colorama import init, Fore, Style

# 初始化 colorama
init()

def format_audio_device_info(device_info, indent=2, tip:str="设配信息"):
    """
    将音频设备信息格式化为易读的字符串，支持自定义缩进。

    参数:
        device_info (dict): 包含音频设备信息的字典。
        indent (int): 每行缩进的空格数，默认值为 2。

    返回:
        str: 格式化的设备信息字符串。
    """
    # 映射主机 API 索引到直观名称
    host_api_map = {
        0: "Windows DirectSound",
        1: "MME",
        2: "ASIO",
        3: "WASAPI",
        4: "WDM-KS",
    }
    
    # 获取字段值，设置默认值防止缺失
    index = device_info.get("index", "未知")
    name = device_info.get("name", "未知设备")
    host_api = host_api_map.get(device_info.get("hostApi", -1), "未知接口")
    max_input_channels = device_info.get("maxInputChannels", 0)
    max_output_channels = device_info.get("maxOutputChannels", 0)
    default_sample_rate = device_info.get("defaultSampleRate", 0)
    low_input_latency = device_info.get("defaultLowInputLatency", 0)
    high_input_latency = device_info.get("defaultHighInputLatency", 0)
    low_output_latency = device_info.get("defaultLowOutputLatency", 0)
    high_output_latency = device_info.get("defaultHighOutputLatency", 0)
    
    # 缩进字符串
    indent_str = " " * indent
    
    # 格式化字符串，动态应用缩进
    formatted_info = (
        f"{Fore.CYAN}{tip}:{Style.RESET_ALL}\n"
        f"{indent_str}{Fore.GREEN}设备编号:{Style.RESET_ALL} {index}\n"
        f"{indent_str}{Fore.GREEN}设备名称:{Style.RESET_ALL} {name}\n"
        f"{indent_str}{Fore.GREEN}音频接口类型:{Style.RESET_ALL} {host_api}\n"
        f"{indent_str}{Fore.GREEN}最大输入声道数:{Style.RESET_ALL} {max_input_channels} (支持 {max_input_channels} 个麦克风)\n"
        f"{indent_str}{Fore.GREEN}最大输出声道数:{Style.RESET_ALL} {max_output_channels} (支持 {max_output_channels} 个扬声器)\n"
        f"{indent_str}{Fore.GREEN}默认采样率:{Style.RESET_ALL} {default_sample_rate:.0f} Hz\n"
        f"{indent_str}{Fore.GREEN}最小输入延迟:{Style.RESET_ALL} {low_input_latency:.3f} 秒\n"
        f"{indent_str}{Fore.GREEN}最大输入延迟:{Style.RESET_ALL} {high_input_latency:.3f} 秒\n"
        f"{indent_str}{Fore.GREEN}最小输出延迟:{Style.RESET_ALL} {low_output_latency:.3f} 秒\n"
        f"{indent_str}{Fore.GREEN}最大输出延迟:{Style.RESET_ALL} {high_output_latency:.3f} 秒"
    )
    
    return formatted_info

# 测试函数
if __name__ == "__main__":
    device_info = {
        "index": 1,
        "structVersion": 2,
        "name": "麦克风阵列 (Realtek(R) Audio)",
        "hostApi": 0,
        "maxInputChannels": 4,
        "maxOutputChannels": 0,
        "defaultLowInputLatency": 0.09,
        "defaultLowOutputLatency": 0.09,
        "defaultHighInputLatency": 0.18,
        "defaultHighOutputLatency": 0.18,
        "defaultSampleRate": 44100
    }
    
    # 测试不同缩进
    print("缩进 2 个空格：")
    print(format_audio_device_info(device_info, indent=2))
    print("\n缩进 4 个空格：")
    print(format_audio_device_info(device_info, indent=4))