import time
import wave
import logging
import json
import threading
from datetime import datetime
import os
from typing import Dict,List

import pyaudio
import colorama
from colorama import Fore, Style

colorama.init()
default_config = {
    "format":8, # 8,4,2 --> 质量逐渐升高
    "channels":1, #通道数量
    "rate":44100, #每秒录制的样本数量
    "is_input":True, #是否是输入设备
    "input_size":1,
    "input_device_index":[1], #输入设备
    "frames_per_buffer":1024, #每帧的样本数
    "mode": "timing", # timing(定时) 和 manual(自动)
    "timing": 9,
    "outpath": "./"
}

class AudioRecorder:
    def __init__(self,config:Dict=default_config):
        self.config = config
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
    
    def show_devices(self) -> None:
        device_count = self.audio.get_device_count()
        for i in range(device_count):
            print(format_device_info(self.audio.get_device_info_by_index(i)))
    
    def show_default_device(self) -> None:
        device_default:Dict = self.audio.get_default_input_device_info()
        print(format_device_info(device_default,tip="默认设备"))
        
    def show_config(self,indent:int=2):
        print(f'{Fore.RED}{json.dumps(self.config,indent=indent)}{Style.RESET_ALL}')

    def set_config(self,config:Dict):
        self.config = config
    
    
    def record_multi_devices(self) -> None:
        if self.is_recording:
            return

        if not self.config.get("input_device_index"):
            print(f"{Fore.RED}✘ 错误: 没有指定输入设备{Style.RESET_ALL}")
            return
        
        self.is_recording = True
        self.recording_lock = threading.Lock()
        self.stop_recording = threading.Event()
        self.recording_threads:List[threading.Thread] = []
        self.audio_data = {}  #存储各个设备的数据
        
        try:
            for idx in self.config.get("input_device_index",[]):
                thread = threading.Thread(
                    target=self._record_single_device,
                    args=(idx,),
                    daemon=True
                )
                thread.start()
                self.recording_threads.append(thread)
            
            print(f'------------------{self.config.get("mode","")}')
            if self.config.get("mode","") == "timing":
                print(f'{Fore.YELLOW}定时录音模式:{Style.RESET_ALL}')
                timing = self.config.get("timing", 5)
                time.sleep(timing)
                self.stop_recording.set()
            else:
                print(f"{Fore.YELLOW}▶ 手动录音模式 - 按回车键停止{Style.RESET_ALL}")
                input()
                self.stop_recording.set()
            
            for thread in self.recording_threads:
                thread.join()
            
            
            self._save_audio_files()
            print(f"{Fore.GREEN}✔ 录音完成{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}✘ 录音失败: {str(e)}{Style.RESET_ALL}")
            self.stop_recording.set()
        finally:
            self.is_recording = False
            self._cleanup() #释放全局资源
        
    def _record_single_device(self,device_idx:int):
        frames = []
        stream = None
        
        try:
            stream = self.audio.open(
                format=self.config["format"],
                channels=self.config["channels"],
                rate=self.config["rate"],
                input=True,
                input_device_index=device_idx,
                frames_per_buffer=self.config["frames_per_buffer"]
            )
            
            print(f"{Fore.CYAN}● 设备 {device_idx} 开始录音{Style.RESET_ALL}")
            while not self.stop_recording.is_set():
                try:
                    data = stream.read(self.config["frames_per_buffer"],exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f'{Fore.RED}-- 设备{device_idx} 读取数据失败 :{e}{Style.RESET_ALL}')
                    break
            
            with self.recording_lock:
                self.audio_data[device_idx] = frames
        
            print(f"{Fore.LIGHTRED_EX}● 设备 {device_idx} 录音结束{Style.RESET_ALL}")
        except Exception as e:
            print(f'{Fore.RED}-- 设备{device_idx} 读取数据失败 :{e}{Style.RESET_ALL}')
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
                
    def _save_audio_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outpath = self.config.get("outpath","./")
        
        os.makedirs(outpath,exist_ok=True)
        for device_idx,frames in self.audio_data.items():
            if not frames:
                continue
            
            filename = f'd{device_idx}_{timestamp}.wav'
            file_path = os.path.join(outpath,filename)
            
            try:
                with wave.open(file_path,"wb") as wf:
                    wf.setnchannels(self.config["channels"])
                    wf.setsampwidth(self.audio.get_sample_size(self.config["format"]))
                    wf.setframerate(self.config["rate"])
                    wf.writeframes(b''.join(frames))
                
                print(f"{Fore.GREEN}✔ 设备 {device_idx} 录音已保存: {file_path}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✘ 设备 {device_idx} 保存失败: {str(e)}{Style.RESET_ALL}")

    def _cleanup(self):
        if hasattr(self, 'recording_threads'):
            self.recording_threads.clear()
        if hasattr(self, 'audio_data'):
            self.audio_data.clear()
            
    def close_audio(self) -> None:
        self.audio.terminate()
            

def format_device_info(device_info, indent=2, tip:str="设配") -> str:
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
        f"{Fore.CYAN}{tip}{Fore.RED}{index}:{Style.RESET_ALL}\n"
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


if __name__ == '__main__':
    recorder = AudioRecorder()
    # recorder.show_config()
    # recorder.record_multi_devices()
    recorder.record_multi_devices()
    recorder.close_audio()
    # recorder.show_default_device()
    # recorder.show_devices()
    
    