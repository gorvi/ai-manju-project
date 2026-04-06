#!/usr/bin/env python3
"""
《我老公是条龙》TTS 配音生成脚本
用法：python3 tts_配音生成.py

音色选择：
  女主（沈映晚）：zh-CN-XiaoxiaoNeural（温暖女声）
  男主（敖玄）  ：zh-CN-YunxiNeural（阳光男声）
  旁白         ：zh-CN-YunyangNeural（专业播音）
"""
import asyncio
import edge_tts
import os
import json
from pathlib import Path

# ========== 配置区 ==========
PROJECT_ROOT = Path("/Users/ghw/Documents/xiaoshuo/ai-manju-project")
SCRIPT_FILE  = PROJECT_ROOT / "04_分镜" / "前3集配音台本.md"
OUTPUT_DIR   = PROJECT_ROOT / "03_资产" / "配音音频"
OUTPUT_DIR.mkdir(exist_ok=True)

# 音色映射：角色名 → Edge TTS voice
VOICE_MAP = {
    "沈映晚": "zh-CN-XiaoxiaoNeural",   # 温暖女声，适合女主
    "敖玄":   "zh-CN-YunxiNeural",       # 阳光男声，适合傲娇龙
    "旁白":   "zh-CN-YunyangNeural",    # 播音腔，适合旁白
    "内心":   "zh-CN-XiaoyiNeural",     # 卡通感，适合敖玄内心OS
}

# 语速/音调微调（可按需调整）
RATE_MAP = {
    "沈映晚": "+0%",    # 正常语速
    "敖玄":   "-5%",    # 稍慢，体现高冷
    "旁白":   "+10%",   # 稍快，节省时间
    "内心":   "-10%",   # 很慢，思考感
}
PITCH_MAP = {
    "沈映晚": "+0Hz",
    "敖玄":   "-10Hz",  # 偏低沉
    "旁白":   "+0Hz",
    "内心":   "+20Hz",  # 偏高，体现内心紧张
}


async def generate_audio(text: str, voice: str, output_file: str, rate: str = "+0%", pitch: str = "+0Hz") -> bool:
    """生成单条音频"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
        print(f"  ✅ → {Path(output_file).name}")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False


async def main():
    print("=" * 60)
    print("《我老公是条龙》TTS 配音生成器")
    print("=" * 60)

    # 读取配音台本
    if not SCRIPT_FILE.exists():
        print(f"❌ 找不到台本文件: {SCRIPT_FILE}")
        return

    content = SCRIPT_FILE.read_text(encoding="utf-8")

    # 简单解析：按行读取，"角色名："开头的是台词行
    tasks = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or "：" not in line:
            continue
        # 跳过标题行和说明行
        if line.startswith("#") or line.startswith("---") or line.startswith("说明"):
            continue

        parts = line.split("：", 1)
        if len(parts) < 2:
            continue
        speaker = parts[0].strip()
        text = parts[1].strip().strip('"').strip('"').strip("「").strip("」").strip("'").strip('"')

        if not text or len(text) < 2:
            continue
        if speaker not in VOICE_MAP:
            continue

        # 生成文件名
        safe_name = text[:15].replace(" ", "_").replace("？", "").replace("！", "").replace("，", "")
        filename = f"ep{(i//100)+1:02d}_line_{i:03d}_{safe_name}.mp3"
        out_path = OUTPUT_DIR / filename

        voice = VOICE_MAP[speaker]
        rate = RATE_MAP.get(speaker, "+0%")
        pitch = PITCH_MAP.get(speaker, "+0Hz")

        tasks.append(generate_audio(text, voice, str(out_path), rate, pitch))

    if not tasks:
        print("⚠️ 没有找到有效台词行")
        return

    print(f"\n共找到 {len(tasks)} 条台词，开始生成...\n")

    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r)
    print(f"\n{'='*60}")
    print(f"完成！成功 {success}/{len(tasks)} 条")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
