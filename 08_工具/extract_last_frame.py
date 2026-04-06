#!/usr/bin/env python3
"""
提取视频最后一帧为图片
用法:
    python3 extract_last_frame.py <视频文件> [输出图片路径]
    python3 extract_last_frame.py video.mp4
    python3 extract_last_frame.py video.mp4 output.png
"""

import subprocess
import sys
import os
import shutil

def extract_last_frame(video_path: str, output_path: str = None) -> str:
    """提取视频最后一帧，返回图片路径"""
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    
    # 如果没有指定输出路径，自动生成
    if not output_path:
        basename = os.path.basename(video_path)
        name = os.path.splitext(basename)[0]
        output_path = f"{name}_last_frame.png"
    
    # 使用 ffmpeg 提取最后一帧
    # -sseof -0.1: 从文件末尾往前0.1秒
    # -update 1: 只输出一帧
    # -q:v 2: 输出质量
    cmd = [
        'ffmpeg', '-sseof', '-0.1',
        '-i', video_path,
        '-update', '1',
        '-q:v', '2',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 执行失败: {result.stderr}")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 extract_last_frame.py <视频文件> [输出图片路径]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = extract_last_frame(video_path, output_path)
        size = os.path.getsize(result)
        print(f"✓ 已保存: {result} ({size/1024:.1f} KB)")
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)
