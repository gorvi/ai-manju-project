#!/usr/bin/env python3
"""
ep01_asset_generate.py  — 通用版资产图片生成器
参考 run_tasks.py 结构，从 JSON 配置读取资产列表并执行。

用法:
    python3 ep01_asset_generate.py [资产配置文件.json] [--asset N]

示例:
    python3 ep01_asset_generate.py                                        # 默认读取同目录 *_wechat.json
    python3 ep01_asset_generate.py my_asset.json                          # 指定配置文件
    python3 ep01_asset_generate.py --asset 2                             # 仅生成 ID=2 的资产
    python3 ep01_asset_generate.py --list                                 # 仅列出资产不执行
"""

import json
import subprocess
import time
import os
import sys
import re
from datetime import datetime

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))


def find_default_config():
    """查找同目录下最新的资产 JSON 配置"""
    files = [f for f in os.listdir(ASSET_DIR) if f.startswith("ep01_") and f.endswith(".json")]
    if not files:
        return None
    # 按修改时间排序，取最新的
    files.sort(key=lambda f: os.path.getmtime(os.path.join(ASSET_DIR, f)), reverse=True)
    return os.path.join(ASSET_DIR, files[0])


def load_assets(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 支持单对象或多对象数组
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "assets" in data:
            return data["assets"]
        else:
            return [data]
    return []


def normalize_asset(asset):
    """
    统一资产格式，支持两种结构：
      A. { type, params: { prompt, images, ... } }
      B. { generation: { mode, prompt, images, ... } }  ← 当前 JSON 使用这种
    统一转换为 A 格式。
    """
    gen = asset.get("generation", {})
    if gen:
        return {
            "id": asset.get("id"),
            "name": asset.get("name"),
            "type": gen.get("mode") or gen.get("type") or "text2image",
            "output": asset.get("output", f"asset_{asset.get('id','1')}.png"),
            "params": {
                "prompt": gen["prompt"],
                "model_version": gen.get("model_version", "seedance3.0"),
                "ratio": gen.get("ratio", "9:16"),
                "duration": gen.get("duration", 5),
                "images": gen.get("images", []),
                "negative_prompt": gen.get("negative_prompt", ""),
                "steps": gen.get("steps"),
                "guidance_scale": gen.get("guidance_scale"),
            }
        }
    else:
        return asset


def build_command(asset):
    """根据资产类型构建 dreamina 命令"""
    asset = normalize_asset(asset)
    p = asset["params"]
    t = asset.get("type", "text2image")

    no_duration_modes = {"image2image", "image_upscale", "frames2video"}

    base = [
        "dreamina",
        t,
        "--prompt", p["prompt"],
        "--model_version", p.get("model_version", "seedance3.0"),
        "--ratio", p.get("ratio", "9:16"),
    ]

    # image2image / frames2video 等不支持 --duration
    if t not in no_duration_modes:
        base += ["--duration", str(p.get("duration", 5)), "--poll", "0"]
    else:
        base += ["--poll", "0"]

    # image2image 使用 --images（复数），其他 multimodal 系列使用 --image（单数）
    img_flag = "--images" if t == "image2image" else "--image"
    for img in p.get("images", []):
        base += [img_flag, img]

    return base


def submit_and_download(asset, output_base, interval=15, timeout=300):
    name = asset.get("name", asset.get("id", "?"))
    asset_id = asset.get("id", "?")
    output_file = asset.get("output", f"asset_{asset_id}.png")
    output_path = os.path.join(output_base, output_file)
    norm = normalize_asset(asset)
    t = norm.get("type", "text2image")

    print(f"\n{'='*60}")
    print(f"🚀 [资产{asset_id}] {name}")
    print(f"   类型: {t} | 输出: {output_file}")
    print(f"{'='*60}")

    # 文件存在检查
    if os.path.exists(output_path):
        size = os.path.getsize(output_path) / 1024
        print(f"   ⏭️  已存在，跳过: {output_file} ({size:.0f}KB)")
        return True

    cmd = build_command(asset)

    # 提交任务
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        raw = result.stdout + result.stderr
        m = re.search(r'"submit_id":\s*"([^"]+)"', raw)
        if not m:
            print(f"   ❌ 提交失败，未找到 submit_id")
            print(f"   输出: {raw[:400]}")
            return False
        submit_id = m.group(1)
        print(f"   ✅ submit_id: {submit_id}")
    except subprocess.TimeoutExpired:
        print(f"   ❌ 命令执行超时（60s）")
        return False
    except Exception as e:
        print(f"   ❌ 执行出错: {e}")
        return False

    # 轮询结果
    print(f"   ⏳ 轮询中（每{interval}s，最多{timeout}s）...")
    query_cmd = ["dreamina", "query_result", f"--submit_id={submit_id}"]
    start = time.time()

    while True:
        time.sleep(interval)
        elapsed = int(time.time() - start)

        try:
            q = subprocess.run(query_cmd, capture_output=True, text=True, timeout=30)
            qout = q.stdout + q.stderr

            if '"gen_status": "success"' in qout:
                # 优先取图片
                img_m = re.search(r'"image_url":\s*"([^"]+)"', qout)
                vid_m = re.search(r'"video_url":\s*"([^"]+)"', qout)
                url = (img_m or vid_m)
                url = url.group(1) if url else None

                if not url:
                    print(f"   ❌ 成功但未找到资源URL")
                    return False

                kind = "图片" if img_m else "视频"
                print(f"   📥 下载{kind}中... ({url[:50]}...)")
                dl = subprocess.run(
                    ["curl", "-L", url, "-o", output_path],
                    capture_output=True, timeout=120
                )

                if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
                    size = os.path.getsize(output_path) / 1024
                    print(f"   ✅ 完成: {output_file} ({size:.0f}KB)")
                    return True
                else:
                    print(f"   ❌ 下载失败或文件过小")
                    return False

            elif '"gen_status": "fail"' in qout:
                reason = re.search(r'"fail_reason":\s*"([^"]+)"', qout)
                reason = reason.group(1) if reason else "未知"
                print(f"   ❌ 生成失败: {reason}")
                return False
            else:
                print(f"   ⏳ 生成中... ({elapsed}s)")

        except Exception as e:
            print(f"   ⚠️ 查询出错: {e}")

        if elapsed >= timeout:
            print(f"   ⚠️ 等待超时（{timeout}s）")
            return False


def main():
    os.makedirs(ASSET_DIR, exist_ok=True)

    # 解析参数
    config_path = None
    targets = None
    list_only = False

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--list":
            list_only = True
        elif arg == "--asset" and i < len(sys.argv) - 1:
            targets = [int(sys.argv[i + 1])]
        elif arg.endswith(".json"):
            config_path = arg

    # 确定配置文件
    if not config_path:
        config_path = find_default_config()

    if not config_path or not os.path.exists(config_path):
        print(f"❌ 未找到资产配置文件")
        print(f"   搜索目录: {ASSET_DIR}")
        print(f"   提示: python3 ep01_asset_generate.py <配置文件.json>")
        sys.exit(1)

    assets = load_assets(config_path)
    print(f"📋 配置文件: {os.path.basename(config_path)}")
    print(f"📦 资产数量: {len(assets)}")

    if list_only:
        print("\n资产列表:")
        for a in assets:
            status = "✅" if os.path.exists(os.path.join(ASSET_DIR, a.get("output", ""))) else "⏳"
            print(f"  [{a.get('id','?')}] {a.get('name','?')} — {status} {a.get('output','')}")
        return

    assets_to_run = [a for a in assets if targets is None or a.get("id") in targets]

    log_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(ASSET_DIR, f"asset_log_{log_ts}.txt")

    success = fail = 0
    with open(log_file, "w", encoding="utf-8") as lf:
        lf.write(f"执行开始: {datetime.now().isoformat()}\n")
        lf.write(f"配置文件: {config_path}\n\n")
        for asset in assets_to_run:
            ok = submit_and_download(asset, ASSET_DIR)
            aid = asset.get("id", "?")
            name = asset.get("name", "?")
            lf.write(f"[{aid}] {name} → {'成功' if ok else '失败'}\n")
            success += ok
            fail += 1 - ok
        lf.write(f"\n成功: {success} | 失败: {fail}\n")

    print(f"\n{'='*60}")
    print(f"✅ 完成！成功:{success} 失败:{fail}")
    print(f"📄 日志: {os.path.basename(log_file)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
