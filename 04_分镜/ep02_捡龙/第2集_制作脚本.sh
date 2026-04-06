#!/bin/bash
# 第2集《捡龙》视频生成脚本
# 用法: bash 第2集_制作脚本.sh

OUTPUT_DIR="/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/镜头素材/ep02"
mkdir -p "$OUTPUT_DIR"

SCENE_POMIAO="/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/场景底图_16x9_v50/破庙/scene_pomiao_16x9_v50.png"
SCENE_POMIAO_CORNER="/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/场景底图_16x9_v50/破庙内角落/scene_pomiao_corner_16x9_v50.png"
SCENE_TIANLEI="/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/场景底图_16x9_v50/上海/scene_jiudao_tianlei_16x9.png"
SHEN_REF="/Users/ghw/Documents/xiaoshuo/ai-manju-project/05_出图/角色/沈映晚/shenyingwan_fenhong_ref.png"

echo "=== 第2集《捡龙》视频生成开始 ==="

# 镜头1：片头字幕（5秒）- 纯黑屏text2video
echo "[1/7] 生成镜头1：片头字幕..."
dreamina text2video \
  --prompt "纯黑背景，无任何光线和运动，字幕文字除外，白色黑体大字逐行居中显现：第一行'第一世'停留1秒，第二行'永宁城'停留2秒，全程无任何其他内容，4K超清，电影级写实国风，60fps，画面稳定无多余抖动" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 5 \
  --poll 60

# 镜头2：九道天雷轰炸（10秒）
echo "[2/7] 生成镜头2：九道天雷轰炸..."
dreamina multimodal2video \
  --image "$SCENE_TIANLEI" \
  --prompt "天庭乌云翻滚，紫电在云层穿梭如巨龙，一条通体漆黑的百丈巨龙在雷电中挣扎，龙鳞如墨，龙身蜿蜒数百丈，双翼展开遮天蔽日，第八道天雷劈下龙身剧震龙鳞碎裂龙血飞溅，第九道天雷劈下画面SLAP震效果全程雷电交加氛围紧张惨烈，电影级高度动态专业运镜，4K超清HDR，60fps" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 10 \
  --poll 60

# 镜头3：敖玄坠落破庙（13秒）
echo "[3/7] 生成镜头3：敖玄坠落破庙..."
dreamina multimodal2video \
  --image "$SCENE_POMIAO" \
  --prompt "破庙内，黄昏光线透进，黑龙从万丈高空坠落被迫化形为三尺白蛇砰的一声砸穿破庙屋顶，碎瓦片灰尘纷纷落下，白蛇浑身是血摔在冰冷的石板地上蜷缩在墙角，白色鳞片沾满血污奄奄一息，SP主观视角跟随龙身坠落穿越瓦片PUL冲击推进+SLAP震效果，慢动作呈现白蛇摔落慢镜头，f/o焦外淡入至蜷缩墙角，4K超清HDR，60fps，电影级" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 13 \
  --poll 60

# 镜头4：白蛇濒死（12秒）
echo "[4/7] 生成镜头4：白蛇濒死..."
dreamina multimodal2video \
  --image "$SCENE_POMIAO_CORNER" \
  --prompt "破庙内，黄昏余晖透进，白蛇蜷缩在墙角浑身是血鳞片碎裂大半奄奄一息，赤红色眼睛里有痛苦不甘和绝望，白蛇身体微微发抖它闭上眼睛准备迎接死亡，HH手持微幅晃动捕捉呼吸感，MCU特写捕捉蛇眸里的不甘，LS慢速推进展示全身伤痕累累，电影级高度动态专业运镜，4K超清HDR，60fps" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 12 \
  --poll 60

# 镜头5：沈映晚推门（15秒）
echo "[5/7] 生成镜头5：沈映晚推门..."
dreamina multimodal2video \
  --image "$SCENE_POMIAO" \
  --image "$SHEN_REF" \
  --prompt "破庙门口，黄昏时分，一只手推开破旧木门吱呀作响，夕阳从身后照进来给姑娘轮廓镀上金边，一位十八九岁少女站在门口，素青色衣裳乌发用木簪子挽着，肩上背着药篓，OTS过肩镜头越过姑娘肩膀看破庙内部，LS慢速推进从破庙全景推进至门口姑娘面部中景，金边光线轮廓感强，角色相貌服装必须与参考角色图完全一致，电影级高度动态专业运镜，4K超清HDR，60fps" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 15 \
  --poll 60

# 镜头6：发现白蛇（20秒）
echo "[6/7] 生成镜头6：发现白蛇..."
dreamina multimodal2video \
  --image "$SCENE_POMIAO_CORNER" \
  --image "$SHEN_REF" \
  --prompt "破庙内，黄昏余晖照入，沈映晚蹲下歪头打量白蛇，赤红色蛇眸与她对视，她犹豫片刻伸手轻轻触碰白蛇冰凉的身体，白蛇没有咬她只是发出嘶的一声，她心软了小心翼翼把白蛇捧起，OTS双人镜头，CRS环绕运镜以两人为中心缓慢半周环绕，MCU特写捕捉蛇眸与姑娘对视，SS跟随透视捕捉她伸手触碰白蛇的温柔慢动作，角色相貌服装必须与参考角色图完全一致，电影级高度动态专业运镜，4K超清HDR，60fps" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 20 \
  --poll 60

# 镜头7：抱蛇离开（15秒）
echo "[7/7] 生成镜头7：抱蛇离开..."
dreamina multimodal2video \
  --image "$SCENE_POMIAO" \
  --image "$SHEN_REF" \
  --prompt "破庙内，沈映晚解下披风铺在地上小心把白蛇捧起放在披风上裹好，抱进怀里转身走出破庙，夕阳在她身后形成金边轮廓光，白蛇蜷在她怀里闻到淡淡的药草香和她的体温，SS跟随透视跟随她抱起白蛇的动作，LS向后拉出至全景呈现她抱着白蛇走向门口的身影逆光剪影金边轮廓，SP主观视角从白蛇视角看她下巴和侧脸光线温暖，白蛇闭上眼睛沉沉睡去，f/o焦外淡出，角色相貌服装必须与参考角色图完全一致，电影级高度动态专业运镜，4K超清HDR，60fps" \
  --model_version seedance2.0 \
  --ratio 9:16 \
  --duration 15 \
  --poll 60

echo "=== 第2集《捡龙》全部生成完成 ==="
