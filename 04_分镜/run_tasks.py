#!/usr/bin/env python3
"""
AI漫剧视频批量生成任务执行器 v4
支持新格式：{epid, episode_name, shots[{shotid, name, duration, enabled, dialogue, params}]}
按 epid 分目录输出，shotid 格式：ep02_shot01
"""

import hashlib
import json
import subprocess
import time
import os
import sys
import re
from datetime import datetime

# 配置
OUTPUT_BASE = "/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/镜头素材"
LOG_DIR     = "/Users/ghw/Documents/xiaoshuo/ai-manju-project/04_分镜"
MAX_WAIT    = 900   # 15分钟超时
POLL_INT    = 30    # 轮询间隔秒


def prompt_fingerprint(prompt):
    """对完整prompt内容算MD5指纹，用于精准查重"""
    return hashlib.md5(prompt.encode()).hexdigest()[:16]


def get_existing_tasks():
    """获取Dreamina队列中排队任务"""
    try:
        r = subprocess.run(["dreamina", "list_task"],
                          capture_output=True, text=True, timeout=30)
        tasks_list = json.loads(r.stdout + r.stderr)
        result = {}
        for t in tasks_list:
            status = t.get("gen_status", "")
            if status in ("fail", "success"):
                continue
            sid = t.get("submit_id", "")
            gtype = t.get("gen_task_type", "")
            prompt = t.get("prompt", "")
            fp = prompt_fingerprint(prompt)
            result.setdefault(fp, []).append((gtype, sid))
        return result
    except Exception as e:
        print(f"   ⚠️ 查询已有任务失败: {e}")
        return {}


def build_command(params):
    p = params
    has_images = bool(p.get("images"))
    has_audio  = bool(p.get("audios"))

    if has_images or has_audio:
        cmd = [
            "dreamina", "multimodal2video",
            "--prompt", p["prompt"],
            "--model_version", p.get("model_version", "seedance2.0"),
            "--ratio", p.get("ratio", "9:16"),
            "--duration", str(p.get("duration", 5)),
            "--poll", "0"
        ]
        for img in p.get("images", []):
            cmd += ["--image", img]
        for audio in p.get("audios", []):
            cmd += ["--audio", audio]
    else:
        cmd = [
            "dreamina", "text2video",
            "--prompt", p["prompt"],
            "--model_version", p.get("model_version", "seedance2.0"),
            "--ratio", p.get("ratio", "9:16"),
            "--duration", str(p.get("duration", 5)),
            "--poll", "0"
        ]
    return cmd


def run_task(cmd, shotid, task_name, timeout=300):
    print(f"\n{'='*60}")
    print(f"🚀 [{shotid}] {task_name}")
    short = ' '.join(cmd[:4]) + " ..."
    print(f"   {short}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        m = re.search(r'"submit_id":\s*"([^"]+)"', output)
        if m:
            submit_id = m.group(1)
            print(f"   ✅ submit_id: {submit_id}")
            return submit_id, output
        print(f"   ❌ 未找到submit_id\n   输出: {output[:300]}")
        return None, output
    except subprocess.TimeoutExpired:
        print(f"   ❌ 命令执行超时")
        return None, ""
    except Exception as e:
        print(f"   ❌ 执行出错: {e}")
        return None, str(e)


def poll_and_download(submit_id, output_path, shotid, task_name,
                      max_wait=MAX_WAIT, interval=POLL_INT):
    print(f"   ⏳ 等待生成结果（每{interval}秒轮询，最多{max_wait}s）...")

    query_cmd = ["dreamina", "query_result", f"--submit_id={submit_id}"]
    start = time.time()
    timeout_triggered = False

    while True:
        elapsed = int(time.time() - start)
        if elapsed >= max_wait:
            print(f"   ⏸️ 等待超时（{max_wait}s），任务已在Dreamina队列中，submit_id={submit_id}")
            timeout_triggered = True
            break

        time.sleep(interval)
        elapsed = int(time.time() - start)

        try:
            r = subprocess.run(query_cmd, capture_output=True, text=True, timeout=30)
            qout = r.stdout + r.stderr

            if '"gen_status": "success"' in qout:
                m = re.search(r'"video_url":\s*"([^"]+)"', qout)
                if m:
                    video_url = m.group(1)
                    print(f"   📥 视频就绪，下载中...")
                    dl = subprocess.run(["curl", "-L", video_url, "-o", output_path],
                                        capture_output=True, timeout=120)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        size = os.path.getsize(output_path) / 1024 / 1024
                        print(f"   ✅ 完成: {os.path.basename(output_path)} ({size:.1f}MB)")
                        return True
                    print(f"   ❌ 下载失败或文件过小")
                    return False

            elif '"gen_status": "fail"' in qout:
                fail_m = re.search(r'"fail_reason":\s*"([^"]+)"', qout)
                reason = fail_m.group(1) if fail_m else "未知"
                print(f"   ❌ 生成失败: {reason}")
                return False
            else:
                print(f"   ⏳ 生成中... ({elapsed}s)")

        except Exception as e:
            print(f"   ⚠️ 查询异常: {e}，继续等待...")

    return None if timeout_triggered else False


def main():
    if len(sys.argv) < 2:
        print("用法: python3 run_tasks.py <任务列表.json>")
        sys.exit(1)

    task_file = sys.argv[1]
    if not os.path.isabs(task_file):
        task_file = os.path.join(os.path.dirname(__file__), task_file)

    with open(task_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 解析顶级字段（支持新旧两种格式）
    # 新格式：{epid, episode_name, shots:[...]}
    # 旧格式：[{"id": ..., "params": ...}, ...]
    if "shots" in data:
        epid = data.get("epid", "ep00")
        episode_name = data.get("episode_name", "")
        shots = data["shots"]
        print(f"📺 {epid} {episode_name}，共 {len(shots)} 个镜头")
    else:
        epid = "ep01"
        episode_name = ""
        shots = data
        print(f"📺 旧格式 JSON，共 {len(shots)} 个镜头")

    # 输出目录：镜头素材/{epid}/
    output_dir = os.path.join(OUTPUT_BASE, epid)
    os.makedirs(output_dir, exist_ok=True)

    log_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(LOG_DIR, f"执行日志_{epid}_{log_ts}.txt")

    print(f"任务文件: {task_file}")
    print(f"输出目录: {output_dir}")
    print(f"日志文件: {log_file}")
    print(f"超时设置: {MAX_WAIT}s/镜头\n")

    existing_tasks = get_existing_tasks()
    if existing_tasks:
        print(f"Dreamina排队中: {len(existing_tasks)} 个任务\n")

    with open(log_file, 'w', encoding='utf-8') as lf:
        lf.write(f"执行开始: {datetime.now().isoformat()}\n")
        lf.write(f"任务文件: {task_file}\n")
        lf.write(f"epid: {epid} {episode_name}\n\n")

        success = 0; skip = 0; disabled = 0; fail = 0; queued = 0

        for shot in shots:
            shotid = shot.get("shotid", shot.get("id", "shot_?"))
            task_name = shot.get("name", "未命名")
            duration = shot.get("duration", 5)
            enabled = shot.get("enabled", True)

            if not enabled:
                print(f"\n🚫 [{shotid}] {task_name} [已禁用]")
                lf.write(f"[{shotid}] {task_name} → 已禁用\n")
                disabled += 1
                continue

            # 从 shotid 解析集号和镜号
            # 格式：ep02_shot01
            m = re.match(r'(ep\d+)_shot(\d+)', shotid)
            if m:
                ep_num = m.group(1)   # ep02
                shot_num = m.group(2) # 01
            else:
                ep_num = epid
                shot_num = shotid.split("_")[-1]

            output_file = f"{ep_num}_shot{shot_num.zfill(2)}_{task_name}.mp4"
            output_path = os.path.join(output_dir, output_file)

            if os.path.exists(output_path):
                print(f"\n⏭️ [{shotid}] {task_name} → 文件已存在，跳过")
                lf.write(f"[{shotid}] {task_name} → 跳过（已存在）\n")
                skip += 1
                continue

            params = shot.get("params", {})
            cmd = build_command(params)

            # 用prompt指纹查重
            fp = prompt_fingerprint(params.get("prompt", ""))
            if fp in existing_tasks:
                entries = existing_tasks[fp]
                gtype, matched_sid = entries[0]
                sids = ", ".join(s for _, s in entries)
                print(f"   ⏭️ [fingerprint:{fp}] 已在队列（{gtype} {sids}），跳过提交")
                lf.write(f"[{shotid}] {task_name} → 跳过（prompt重复 {sids}）\n")
                queued += 1
                continue

            submit_id, raw = run_task(cmd, shotid, task_name)

            if submit_id:
                ok = poll_and_download(submit_id, output_path, shotid, task_name)
                if ok:
                    lf.write(f"[{shotid}] {task_name} → 成功 ({output_file})\n")
                    success += 1
                elif ok is None:
                    lf.write(f"[{shotid}] {task_name} → 排队中（submit_id={submit_id}，超时{MAX_WAIT}s）\n")
                    queued += 1
                else:
                    lf.write(f"[{shotid}] {task_name} → 失败\n")
                    fail += 1
            else:
                lf.write(f"[{shotid}] {task_name} → 失败（无法获取submit_id）\n")
                fail += 1

        lf.write(f"\n执行结束: {datetime.now().isoformat()}\n")
        lf.write(f"成功: {success} | 跳过: {skip} | 禁用: {disabled} | 排队中: {queued} | 失败: {fail}\n")

    print(f"\n{'='*60}")
    print(f"完成！成功:{success} 跳过:{skip} 禁用:{disabled} 排队中:{queued} 失败:{fail}")
    print(f"日志: {log_file}")
    print(f"{'='*60}")
    if queued > 0:
        print(f"\n⚠️ 有{queued}个任务超时但已在Dreamina队列中")
        print(f"   可去Dreamina网页查看，或稍后重新运行脚本（会检测已排队任务跳过）")

if __name__ == "__main__":
    main()
