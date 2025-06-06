import pyaudio
import wave
import numpy as np
import time
from datetime import datetime

# 音频参数配置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def list_audio_devices():
    """列出所有音频输入设备"""
    audio = pyaudio.PyAudio()
    
    print(f"{ audio.get_default_input_device_info().get('name','error') }")
    print("可用的音频输入设备:")
    input_devices = []
    
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"设备 {i}: {info['name']} (采样率: {info['defaultSampleRate']})")
            input_devices.append(i)
    
    audio.terminate()
    return input_devices

def record_audio(duration, filename=None, device_index=None):
    """录制指定时长的音频"""
    audio = pyaudio.PyAudio()
    
    # 生成文件名
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
    
    print(f"开始录音 {duration} 秒...")
    print(f"文件将保存为: {filename}")
    
    # 打开音频流
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    total_frames = int(RATE / CHUNK * duration)
    
    # 录音循环
    for i in range(total_frames):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # 显示进度
        progress = (i + 1) / total_frames * 100
        print(f"\r录音进度: {progress:.1f}%", end="", flush=True)
    
    print("\n录音完成!")
    
    # 关闭音频流
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # 保存音频文件
    save_audio_file(frames, filename)
    
    return filename

def save_audio_file(frames, filename):
    """保存音频数据到WAV文件"""
    audio = pyaudio.PyAudio()
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    audio.terminate()
    print(f"音频已保存: {filename}")

# 使用示例
if __name__ == "__main__":
    # 查看可用设备
    devices = list_audio_devices()
    # # 录音5秒
    filename = record_audio(5, "test.wav")
