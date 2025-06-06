import argparse
import sys
import os
import json
from typing import List, Dict
from audiorec import AudioRecorder, default_config

def parse_device_list(device_string: str) -> List[int]:
    try:
        return [int(d.strip()) for d in device_string.split(',') if d.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(f"设备列表格式错误: {device_string}. 应该是逗号分隔的数字，如: 1,2,3")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="多设备音频录制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s record -d 1,2,3 -t 10 -o ./recordings
  %(prog)s record -d 1 -m 1 -r 48000 -c 2
  %(prog)s record --help
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # record 子命令
    record_parser = subparsers.add_parser(
        'record', 
        help='开始录音',
        description='录制音频文件'
    )
    
    record_parser.add_argument(
        '-o', '--output',
        help=f'输出路径 (默认: {default_config["outpath"]})'
    )
    
    record_parser.add_argument(
        '-d', '--devices',
        type=parse_device_list,
        help=f'录音设备编号，逗号分隔 (默认: {",".join(map(str, default_config["input_device_index"]))})'
    )
    
    record_parser.add_argument(
        '-t', '--time',
        type=int,
        help=f'录音时长(秒)，仅在定时模式下有效 (默认: {default_config["timing"]})'
    )
    
    record_parser.add_argument(
        '-r', '--rate',
        type=int,
        choices=[8000, 16000, 22050, 44100, 48000, 96000],
        help=f'采样率 (默认: {default_config["rate"]})'
    )
    
    record_parser.add_argument(
        '-c', '--channels',
        type=int,
        choices=[1, 2],
        help=f'声道数 (默认: {default_config["channels"]})'
    )
    
    record_parser.add_argument(
        '-m', '--mode',
        type=int,
        choices=[0, 1],
        help='录音模式: 0=定时模式, 1=手动模式 (默认: 0)'
    )
    
    record_parser.add_argument(
        '--fmt', '--format',
        type=int,
        choices=[8, 4, 2],
        help=f'采样格式 (8=低质量, 4=中等, 2=高质量, 默认: {default_config["format"]})'
    )
    
    record_parser.add_argument(
        '--frames',
        type=int,
        help=f'每帧样本数 (默认: {default_config["frames_per_buffer"]})'
    )
    
    # 添加设备列表命令
    devices_parser = subparsers.add_parser(
        'devices',
        help='列出可用的音频设备'
    )
    devices_parser.add_argument(
        '-d', '--detail',
        help=f'显示输出设备 (默认: 不显示)'
    )
    
    # 添加默认设备命令
    default_parser = subparsers.add_parser(
        'default',
        help='显示默认音频设备信息'
    )
    
    return parser

def build_config_from_args(origin_conf: Dict, args) -> Dict:
    config = origin_conf.copy()
    if hasattr(args, 'output') and args.output is not None:
        config['outpath'] = args.output
    
    if hasattr(args, 'devices') and args.devices is not None:
        config['input_device_index'] = args.devices
    
    if hasattr(args, 'time') and args.time is not None:
        config['timing'] = args.time
    
    if hasattr(args, 'rate') and args.rate is not None:
        config['rate'] = args.rate
    
    if hasattr(args, 'channels') and args.channels is not None:
        config['channels'] = args.channels
    
    if hasattr(args, 'mode') and args.mode is not None:
        config['mode'] = 'timing' if args.mode == 0 else 'manual'
    
    if hasattr(args, 'fmt') and args.fmt is not None:
        config['format'] = args.fmt
    
    if hasattr(args, 'frames') and args.frames is not None:
        config['frames_per_buffer'] = args.frames
    return config

def main():
    parser = create_parser()
    #帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        args = parser.parse_args()
        with open("config.json","r",encoding="utf-8") as f:
            config = json.load(f)
        if not config:
            config = default_config()
        recorder = AudioRecorder(config)
        
        if args.command == 'record':
            config = build_config_from_args(config,args)
            recorder.set_config(config)
            recorder.record_multi_devices()
            
        elif args.command == 'devices' and args.devices is not None:
            print("可用音频设备列表:")
            if hasattr(args,"detail"): 
                recorder.show_devices(filter=False)
                print("have")
            else:
                recorder.show_devices()
        elif args.command == 'default':
            recorder.show_default_device()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n录音被用户中断")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    finally:
        if 'recorder' in locals():
            recorder.close_audio()

if __name__ == '__main__':
    main()