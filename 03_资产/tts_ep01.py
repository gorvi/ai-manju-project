#!/usr/bin/env python3
"""
《我老公是条龙》第1集 TTS 配音生成脚本
直接从 ep01_任务列表_v3_运镜版.json 读取 dialogue 字段，
只生成 TTS 配音（跳过 subtitle 类型）。
"""

import asyncio
import edge_tts
import json
import sys
from pathlib import Path
from datetime import datetime

# ========== 配置区 ==========
PROJECT_ROOT = Path("/Users/ghw/Documents/xiaoshuo/ai-manju-project")
TASK_JSON    = PROJECT_ROOT / "04_分镜" / "ep01_任务列表_v3_运镜版.json"
OUTPUT_DIR   = PROJECT_ROOT / "03_资产" / "配音音频" / "第1集"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_audio(text: str, voice: str, output_file: str,
                         rate: str = "+0%", pitch: str = "+0Hz") -> bool:
    """生成单条配音"""
    try:
        cm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await cm.save(output_file)
        size = Path(output_file).stat().st_size
        print(f"  ✅ {Path(output_file).name} ({size // 1024}KB)")
        return True
    except Exception as e:
        print(f"  ❌ {text[:20]}... → {e}")
        return False


async def main():
    print("=" * 60)
    print("《我老公是条龙》第1集 TTS 配音生成器")
    print("=" * 60)

    if not TASK_JSON.exists():
        print(f"❌ 找不到任务文件: {TASK_JSON}")
        return

    tasks_data = json.loads(TASK_JSON.read_text(encoding="utf-8"))

    tts_items = []
    for shot in tasks_data:
        shot_id  = shot["id"]
        shot_name = shot["name"]
        for dlg in shot.get("dialogue", []):
            if dlg.get("type") == "tts":
                tts_items.append({
                    "shot_id":   shot_id,
                    "shot_name": shot_name,
                    "text":      dlg["text"],
                    "speaker":   dlg.get("speaker", ""),
                    "voice":     dlg.get("voice", "zh-CN-XiaoxiaoNeural"),
                    "rate":      dlg.get("rate", "+0%"),
                    "pitch":     dlg.get("pitch", "+0Hz"),
                    "emotion":   dlg.get("emotion", ""),
                })

    if not tts_items:
        print("⚠️ 未找到 TTS 配音（dialogue 中无 type=tts）")
        return

    print(f"共 {len(tts_items)} 条 TTS 配音：\n")
    for i, item in enumerate(tts_items, 1):
        print(f"  [{i}] {item['shot_id']} {item['shot_name']}")
        print(f"      角色: {item['speaker']}")
        print(f"      台词: {item['text']}")
        print(f"      情绪: {item['emotion']}")
        print()

    print(f"开始生成音频...\n")

    coros = []
    for i, item in enumerate(tts_items):
        safe = item["text"][:15].replace(" ", "_").replace("？", "") \
            .replace("！", "").replace("，", "").replace("。", "").replace("…", "")
        filename = f"ep01_{item['shot_id'].split('_')[-1]}_{item['speaker']}_{safe}.mp3"
        out_path = OUTPUT_DIR / filename

        coros.append(generate_audio(
            item["text"], item["voice"], str(out_path),
            rate=item["rate"], pitch=item["pitch"]
        ))

    results = await asyncio.gather(*coros)
    success = sum(1 for r in results if r)

    print(f"\n{'=' * 60}")
    print(f"完成！成功 {success}/{len(tts_items)} 条")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
