#!/usr/bin/env python3
"""
将图片转换为影视彩铅风格
用法:
    python3 image_to_caiqian.py <图片文件>
    python3 image_to_caiqian.py image.png
"""

import subprocess
import sys
import os
import json

def convert_to_caiqian(image_path: str) -> str:
    """将图片转换为影视彩铅风格，返回输出路径"""
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # 获取原文件名和目录
    basename = os.path.basename(image_path)
    name = os.path.splitext(basename)[0]
    ext = os.path.splitext(basename)[1]
    
    # 输出路径：原名 + _caiqian
    output_path = os.path.join(
        os.path.dirname(image_path),
        f"{name}_caiqian{ext}"
    )
    
    print(f"输入: {image_path}")
    print(f"输出: {output_path}")
    
    # 调用 dreamina image2image
    cmd = [
        'dreamina', 'image2image',
        '--images', image_path,
        '--prompt', '仅面部改为影视真实彩铅风格，其余部分保持原图不变，最高清，细腻铅笔手绘质感',
        '--model_version', '4.0',
        '--resolution_type', '4k',
        '--ratio', '9:16',
        '--poll', '120'
    ]
    
    print(f"正在生成彩铅风格...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"dreamina 执行失败: {result.stderr}")
    
    # 解析输出获取结果
    output = result.stdout
    print(f"输出结果: {output}")
    
    # 下载生成的图片
    try:
        data = json.loads(output)
        if data.get('gen_status') == 'success':
            image_url = data.get('result_json', {}).get('images', [{}])[0].get('image_url', '')
            if image_url:
                download_cmd = ['curl', '-L', image_url, '-o', output_path]
                subprocess.run(download_cmd, check=True)
                print(f"✓ 已保存: {output_path}")
                return output_path
    except:
        pass
    
    # 如果没有直接返回图片路径，说明需要查询
    # 从输出中找 submit_id
    if 'submit_id' in output:
        try:
            data = json.loads(output)
            submit_id = data.get('submit_id', '')
            # 查询结果
            query_cmd = ['dreamina', 'query_result', f'--submit_id={submit_id}']
            query_result = subprocess.run(query_cmd, capture_output=True, text=True)
            qdata = json.loads(query_result.stdout)
            if qdata.get('gen_status') == 'success':
                image_url = qdata.get('result_json', {}).get('images', [{}])[0].get('image_url', '')
                if image_url:
                    subprocess.run(['curl', '-L', image_url, '-o', output_path], check=True)
                    print(f"✓ 已保存: {output_path}")
                    return output_path
        except Exception as e:
            print(f"查询结果失败: {e}")
    
    print(f"⚠ 请手动检查结果")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 image_to_caiqian.py <图片文件>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        result = convert_to_caiqian(image_path)
        size = os.path.getsize(result)
        print(f"文件大小: {size/1024:.1f} KB")
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)
