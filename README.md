<<<<<<< HEAD
TikTok Data Analysis
1. Project Overview
本项目基于抖音创作者平台数据，构建从数据清洗、指标计算到可视化分析与交互看板的完整分析流程，用于支持内容运营策略优化与涨粉决策。

2. Key Highlights
- 构建账号日维度（30天）+ 作品维度（近一年）双层数据集
- 设计并计算互动率、转粉率、主页转粉率、留存质量分等核心指标
- 针对0值/缺失值与小样本偏差引入加权口径（总涨粉/总播放）
- 输出8类可视化结果（趋势、TOP、四象限、热力、体裁对比等）
- 开发Streamlit + Plotly交互式看板，支持筛选、洞察与导出

3. Data Source
- 来源：抖音创作者平台导出数据
- 时间范围：
  - 账号日维度：近30日
  - 作品维度：近一年（约13个月）
- 核心文件：
  - `dataset/video_list.xlsx`
  - `dataset/daily_*.xlsx`

4. Metric Definitions
- 互动率 = (点赞 + 评论 + 分享 + 收藏) / 播放量
- 转粉率 = 粉丝增量 / 播放量
- 主页转粉率 = 粉丝增量 / 主页访问量
- 留存质量分 = 完播率 × (1 - 2s跳出率)
- 加权转粉率（体裁）= 体裁总涨粉 / 体裁总播放

5. Workflow
1. 数据清洗与字段标准化（`tiktok.py`）
2. 衍生指标计算与数据集输出（`data_clean/`）
3. 静态图表生成（`generate_charts.py`）
4. 交互式看板构建（`dashboard_app.py`）

6. Visual Results
图表输出目录：`report/figures/`
- 30日播放趋势
- 涨粉质量（净增 vs 取关）
- 日互动率趋势
- 主页转粉率趋势
- 播放TOP10作品
- 质量四象限（完播率 vs 转粉率）
- 发布时间热力图
- 体裁加权转粉率对比

7. Dashboard Features
- 日期、体裁、播放区间筛选
- KPI联动展示
- 自动洞察（3条）+ 行动建议（2条）
- 当前筛选结果CSV导出

8. Project Structure
=======
# 抖音数据分析项目

## 1. 项目简介
本项目围绕抖音创作者平台数据，搭建了从数据清洗、指标构建、可视化分析到交互式看板的完整流程，用于支持内容策略优化与涨粉决策。

## 2. 项目亮点
- 构建双层数据集：账号日维度（近30日）+ 作品维度（近一年）。
- 设计并落地核心指标：互动率、转粉率、主页转粉率、留存质量分。
- 针对0值、缺失值和小样本偏差，采用加权口径（总涨粉/总播放）提升结论稳健性。
- 产出多视角图表（趋势、TOP、四象限、热力图、体裁对比）。
- 开发交互式看板，支持筛选、KPI联动、自动洞察与CSV导出。

## 3. 数据来源
- 来源：抖音创作者平台导出数据。
- 时间范围：
  - 账号日维度：近30天。
  - 作品维度：约13个月。
- 原始数据目录：`dataset/`。

## 4. 核心指标定义
- `engagement_rate = (like_count + comment_count + share_count + favorite_count) / play_count`
- `follow_conversion_rate = follower_gain_count / play_count`
- `profile_to_follow_rate = follower_gain_count / profile_visit_count`
- `retention_quality_score = completion_rate * (1 - bounce_rate_2s)`
- `weighted_follow_conversion_rate = total_follow_gain / total_play`（分组加权口径）

## 5. 分析流程
1. 清洗并标准化多源 Excel 字段（`tiktok.py`）。
2. 合并并输出清洗后的分析数据（`data_clean/`）。
3. 生成静态分析图表（`generate_charts.py`）。
4. 启动交互式可视化看板（`dashboard_app.py`）。

## 6. 可视化输出
图表生成目录：`report/figures/`
- 近30日播放趋势
- 涨粉质量（净增粉 vs 取关）
- 日互动率趋势
- 主页转粉率趋势
- 播放量TOP10作品
- 质量四象限（完播率 vs 转粉率）
- 发布时间热力图
- 不同体裁加权转粉率对比

## 7. 看板功能
- 日期范围、体裁、播放量区间筛选。
- KPI指标卡联动更新。
- 自动洞察（3条）+ 行动建议（2条）。
- 一键导出当前筛选结果为CSV。

## 8. 项目结构
```text
>>>>>>> fa5b68e (为README新增项目说明容)
tiktok-data-analysis/
├─ dataset/
├─ data_clean/
├─ report/figures/
├─ tiktok.py
├─ generate_charts.py
<<<<<<< HEAD
└─ dashboard_app.py

9. Quick Start
python tiktok.py
python generate_charts.py
streamlit run dashboard_app.py

10. Findings
发布时段在18:00左右的作品流量表现更优
图文体裁的加权转粉率高于1min视频体裁（当前样本）

11. Future Work
引入更多行为特征（封面元素、文案特征等）
扩展为周/月自动报告
增加A/B策略评估模块
=======
├─ dashboard_app.py
└─ README.md
```

## 9. 快速开始
```bash
python tiktok.py
python generate_charts.py
streamlit run dashboard_app.py
```

## 10. 当前阶段结论
- 晚上18:00左右发布的作品，整体流量表现更优。
- 图文体裁的加权转粉率高于1min视频体裁。

## 11. 后续优化方向
- 增加更丰富的内容特征（标题、封面、文案特征等）。
- 扩展周报/月报自动化输出。
- 增加A/B策略评估模块。
>>>>>>> fa5b68e (为README新增项目说明容)
