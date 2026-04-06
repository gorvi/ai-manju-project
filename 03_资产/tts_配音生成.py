#!/usr/bin/env python3
"""
《我老公是条龙》TTS 配音生成脚本 v2
支持 Markdown 表格格式解析
"""
import asyncio
import edge_tts
import re
from pathlib import Path

# ========== 配置区 ==========
PROJECT_ROOT = Path("/Users/ghw/Documents/xiaoshuo/ai-manju-project")
SCRIPT_FILE  = PROJECT_ROOT / "04_分镜" / "前3集配音台本.md"
OUTPUT_DIR   = PROJECT_ROOT / "03_资产" / "配音音频"
OUTPUT_DIR.mkdir(exist_ok=True)

# 音色映射
VOICE_MAP = {
    "沈映晚":    "zh-CN-XiaoxiaoNeural",   # 温暖女声
    "敖玄内心音": "zh-CN-XiaoyiNeural",     # 卡通感内心音
    "敖玄":      "zh-CN-YunxiNeural",       # 阳光男声
    "旁白":      "zh-CN-YunyangNeural",
}

RATE_MAP = {
    "沈映晚":    "+0%",
    "敖玄内心音": "-10%",
    "敖玄":      "-5%",
    "旁白":      "+10%",
}
PITCH_MAP = {
    "沈映晚":    "+0Hz",
    "敖玄内心音": "+20Hz",
    "敖玄":      "-10Hz",
    "旁白":      "+0Hz",
}


async def generate_audio(text: str, voice: str, output_file: str, rate: str, pitch: str) -> bool:
    try:
        cm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await cm.save(output_file)
        size = Path(output_file).stat().st_size
        print(f"  ✅ {Path(output_file).name} ({size//1024}KB)")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False


def parse_table(content: str):
    """解析 Markdown 表格，返回 [(集数, 角色, 台词), ...]"""
    results = []
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        # 跳过空行和标题
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        if "| 集数 |" in line:
            in_table = True
            continue
        if line.startswith("| ---"):
            continue
        if not in_table or "|" not in line:
            if in_table:
                in_table = False
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue

        ep   = parts[1].strip()    # 集数
        spk  = parts[2].strip()     # 角色
        txt  = parts[3].strip()     # 台词

        # 跳过表头和无效行
        if ep in ("集数", "") or spk in ("角色", "") or txt in ("台词", ""):
            continue
        if not txt or len(txt) < 2:
            continue
        # 去掉台词里的引号
        txt = txt.strip('"').strip('"').strip("「").strip("」")
        if not txt:
            continue

        results.append((ep, spk, txt))
    return results


async def main():
    print("=" * 60)
    print("《我老公是条龙》TTS 配音生成器 v2")
    print("=" * 60)

    if not SCRIPT_FILE.exists():
        print(f"❌ 找不到台本: {SCRIPT_FILE}")
        return

    content = SCRIPT_FILE.read_text(encoding="utf-8")
    rows = parse_table(content)
    print(f"解析到 {len(rows)} 条有效台词\n")

    tasks = []
    for i, (ep, speaker, text) in enumerate(rows):
        voice = VOICE_MAP.get(speaker)
        if not voice:
            print(f"  ⏭️ 跳过未知角色: {speaker}")
            continue

        safe = text[:12].replace(" ", "_").replace("？", "").replace("！", "").replace("，", "")
        filename = f"ep{ep}_line{i:02d}_{safe}.mp3"
        out_path = OUTPUT_DIR / filename

        rate  = RATE_MAP.get(speaker, "+0%")
        pitch = PITCH_MAP.get(speaker, "+0Hz")

        tasks.append(generate_audio(text, voice, str(out_path), rate, pitch))

    if not tasks:
        print("⚠️ 没有找到有效台词")
        return

    print(f"开始生成 {len(tasks)} 条音频...\n")
    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r)

    print(f"\n{'='*60}")
    print(f"完成！成功 {success}/{len(tasks)} 条")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
