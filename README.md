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
tiktok-data-analysis/
├─ dataset/
├─ data_clean/
├─ report/figures/
├─ tiktok.py
├─ generate_charts.py
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
