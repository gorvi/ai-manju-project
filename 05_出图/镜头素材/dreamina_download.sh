#!/bin/bash
# 用法: ./dreamina_download.sh <submit_id> <shot_name> [output_dir]
# 例: ./dreamina_download.sh abc123 shot01_片头字幕

SUBMIT_ID=$1
SHOT_NAME=$2
OUT_DIR=${3:-"/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/镜头素材"}
FLAG_FILE="$OUT_DIR/已下载标志.md"
TASK_FILE="$OUT_DIR/.dreamina_tasks.json"

if [ -z "$SUBMIT_ID" ] || [ -z "$SHOT_NAME" ]; then
    echo "用法: $0 <submit_id> <shot_name>"
    exit 1
fi

# 查询结果
echo "正在查询任务 $SUBMIT_ID ..."
RESULT=$(dreamina query_result --submit_id=$SUBMIT_ID 2>/dev/null)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('gen_status',''))" 2>/dev/null)

if [ "$STATUS" = "success" ]; then
    # 下载视频
    MP4_PATH="$OUT_DIR/ep01_${SHOT_NAME}.mp4"
    dreamina get_task --submit_id=$SUBMIT_ID --output=$MP4_PATH 2>/dev/null
    
    if [ -f "$MP4_PATH" ]; then
        SIZE=$(du -h "$MP4_PATH" | cut -f1)
        echo "✅ 下载成功: ep01_${SHOT_NAME}.mp4 ($SIZE)"
        
        # 追加到标志文件
        DATE=$(date "+%Y-%m-%d %H:%M")
        {
            echo ""
            echo "## ✅ $(date '+%Y-%m-%d %H:%M') - $SHOT_NAME"
            echo "- submit_id: \`$SUBMIT_ID\`"
            echo "- 文件: ep01_${SHOT_NAME}.mp4"
            echo "- 大小: $SIZE"
        } >> "$FLAG_FILE"
        
        # 追加到JSON任务记录
        python3 -c "
import json, os
f = '$TASK_FILE'
tasks = []
if os.path.exists(f):
    with open(f) as fp:
        tasks = json.load(fp)
tasks.append({'submit_id': '$SUBMIT_ID', 'shot': '$SHOT_NAME', 'status': 'success', 'path': '$MP4_PATH', 'time': '$DATE'})
with open(f, 'w') as fp:
    json.dump(tasks, fp, ensure_ascii=False, indent=2)
"
        echo "已记录到 $FLAG_FILE"
    else
        echo "❌ 文件下载失败"
    fi
elif [ "$STATUS" = "querying" ]; then
    echo "⏳ 任务还在排队中"
elif [ "$STATUS" = "fail" ]; then
    REASON=$(echo "$RESULT" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('fail_reason',''))" 2>/dev/null)
    echo "❌ 任务失败: $REASON"
else
    echo "❓ 未知状态: $STATUS"
fi
