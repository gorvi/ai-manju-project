# OpenClaw 交接说明

> ⚠️ 本文件已精简，重要规则已迁移至 MEMORY.md 和 ai-manju-production SKILL.md

## 项目位置

`/Users/ghw/Documents/xiaoshuo/ai-manju-project`

## 项目核心设定

- 项目：`《我老公是条龙》`
- 第一季：30 集，单集 1.5 分钟
- 目标：爆款节奏的 AI 漫剧
- 第一季只做古代线，不做现代穿越线

## 必读文件（按顺序）

1. `SKILL.md`（即 `~/.codex/skills/ai-manju-production/SKILL.md`）
2. `00_总控/制作SOP.md`
3. `01_改编/30集分集大纲.md`
4. `02_剧本/前10集正式漫剧剧本.md`
5. `04_分镜/前3集分镜表.md`

## 当前正式可用的场景底图

目录：`05_出图/场景底图_16x9_v50/`

场景清单（v50）：
- 破庙：`scene_pomiao_16x9_v50.png`
- 破庙内角落：`scene_pomiao_corner_16x9_v50.png`
- 房间：`scene_fangjian_16x9_v50.png`
- 房间月光版：`scene_fangjian_moonlight_16x9_v50.png`
- 门槛：`scene_menkan_16x9_v50.png`
- 门槛夜景版：`scene_menkan_night_16x9_v50.png`
- 药铺：`scene_yaopu_16x9_v50.png`
- 药铺反打：`scene_yaopu_reverse_16x9_v50.png`
- 院子：`scene_yuanzi_16x9_v50.png`

## 当前正式可用的角色参考图

目录：`05_出图/角色/`

敖玄_人形（5张）：`aoxuan_human_heiyi_caiqian.png`、`aoxuan_human_heiyi_ref.png`、彩铅备份×2、三视图
敖玄_白蛇（1张）：`aoxuan_snake_ref.png`
沈映晚（7张）：粉红/粉红拖地/现代装 ref+彩铅、三视图

详见各目录下的 `目录清单.json`

## 硬规则（摘要）

详见 MEMORY.md 长期记忆，以下为核心摘要：

1. 场景底图默认 16:9，必须无人物
2. 场景底图必须符合物理现实
3. 有角色的镜头必须垫角色参考图（image2video 双垫或多垫）
4. 生成新场景底图时，优先图生图（image2image）而非纯文生图（text2image）
5. 分镜必须含素材引用（@文件名）和时长校验
6. 台词时长必须匹配镜头时长（约3-4字/秒）
7. 文件命名必须语义化，禁止引用已删除的旧路径

## 当前镜头素材状态

ep01：8个镜头视频已生成，含粗剪版 `ep01_fullRough.mp4`
