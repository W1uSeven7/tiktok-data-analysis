from pathlib import Path

import pandas as pd  # pyright: ignore[reportMissingImports]
import plotly.express as px  # pyright: ignore[reportMissingImports]
import plotly.graph_objects as go  # pyright: ignore[reportMissingImports]
import streamlit as st  # pyright: ignore[reportMissingImports]


BASE_DIR = Path(__file__).resolve().parent
CLEAN_DIR = BASE_DIR / "data_clean"
DAILY_FILE = CLEAN_DIR / "account_daily_merged_30d.csv"
VIDEO_FILE = CLEAN_DIR / "video_performance_clean.csv"


def short_title(title: object, max_len: int = 8) -> str:
    if pd.isna(title):
        return "自拍照"
    text = str(title).strip()
    if not text or text.lower() == "nan" or text == "无标题":
        return "自拍照"
    cleaned = "".join(ch for ch in text if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff"))
    if not cleaned:
        return "自拍照"
    return cleaned[:max_len]


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DAILY_FILE.exists():
        raise FileNotFoundError(f"缺少文件: {DAILY_FILE}")
    if not VIDEO_FILE.exists():
        raise FileNotFoundError(f"缺少文件: {VIDEO_FILE}")

    daily = pd.read_csv(DAILY_FILE)
    video = pd.read_csv(VIDEO_FILE)

    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    video["publish_time"] = pd.to_datetime(video["publish_time"], errors="coerce")

    return daily, video


def add_daily_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy().sort_values("date")
    interactions = out["like_total_day"] + out["comment_total_day"] + out["share_total_day"]
    out["engagement_rate_day"] = (interactions / out["play_total_day"]).where(out["play_total_day"] != 0)
    out["profile_to_follow_rate_day"] = (
        out["followers_new"] / out["profile_visit_day"]
    ).where(out["profile_visit_day"] != 0)
    out["play_7d_ma"] = out["play_total_day"].rolling(window=7, min_periods=1).mean()
    return out


def kpi_cards(daily: pd.DataFrame, video: pd.DataFrame) -> None:
    total_play_30d = int(daily["play_total_day"].sum())
    total_new_followers_30d = int(daily["followers_new"].sum())
    avg_engagement_rate_30d = (
        ((daily["like_total_day"] + daily["comment_total_day"] + daily["share_total_day"]).sum())
        / daily["play_total_day"].sum()
        if daily["play_total_day"].sum() > 0
        else 0
    )

    weighted_follow_conversion = (
        video["follower_gain_count"].sum() / video["play_count"].sum()
        if video["play_count"].sum() > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("近30日总播放", f"{total_play_30d:,}")
    c2.metric("近30日净增粉", f"{total_new_followers_30d:,}")
    c3.metric("近30日互动率", f"{avg_engagement_rate_30d:.2%}")
    c4.metric("作品加权转粉率", f"{weighted_follow_conversion:.2%}")


def chart_play_trend(daily: pd.DataFrame) -> None:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["play_total_day"], mode="lines+markers", name="日播放量"))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["play_7d_ma"], mode="lines", name="7日均线"))
    fig.update_layout(title="近30日播放趋势", xaxis_title="日期", yaxis_title="播放量", height=380)
    st.plotly_chart(fig, use_container_width=True)


def chart_growth_quality(daily: pd.DataFrame) -> None:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["date"], y=daily["followers_new"], name="净增粉"))
    fig.add_trace(go.Bar(x=daily["date"], y=daily["followers_lost"], name="取关粉"))
    fig.update_layout(
        title="涨粉质量（净增 vs 取关）", xaxis_title="日期", yaxis_title="人数", barmode="group", height=380
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_top_videos(video: pd.DataFrame) -> None:
    top = video.sort_values("play_count", ascending=False).head(10).copy()
    top["title_short"] = top["video_name"].map(short_title)

    fig = px.bar(
        top.sort_values("play_count", ascending=True),
        x="play_count",
        y="title_short",
        orientation="h",
        title="播放量 TOP10 作品",
        labels={"play_count": "播放量", "title_short": "视频标题简写"},
        text="play_count",
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(height=460)
    st.plotly_chart(fig, use_container_width=True)


def chart_quality_quadrant(video: pd.DataFrame) -> None:
    q = video.dropna(subset=["completion_rate", "follow_conversion_rate", "play_count"]).copy()
    if q.empty:
        st.info("四象限图无可用数据。")
        return

    q["title_short"] = q["video_name"].map(short_title)
    q["bubble_size"] = (q["play_count"] / q["play_count"].max()) * 60 + 8

    fig = px.scatter(
        q,
        x="completion_rate",
        y="follow_conversion_rate",
        size="bubble_size",
        hover_data=["title_short", "play_count", "follower_gain_count"],
        title="作品质量四象限（完播率 vs 转粉率）",
        labels={"completion_rate": "完播率", "follow_conversion_rate": "转粉率"},
    )
    fig.update_layout(height=430)
    st.plotly_chart(fig, use_container_width=True)


def chart_content_weighted_conversion(video: pd.DataFrame) -> None:
    d = video.dropna(subset=["content_type", "play_count", "follower_gain_count"]).copy()
    d["content_type_display"] = (
        d["content_type"].astype(str).str.strip().replace({"": "未知", "nan": "未知"})
    )
    grouped = d.groupby("content_type_display").agg(
        total_play=("play_count", "sum"),
        total_follow_gain=("follower_gain_count", "sum"),
    )
    grouped["weighted_follow_conversion_rate"] = (
        grouped["total_follow_gain"] / grouped["total_play"]
    ).where(grouped["total_play"] != 0)
    grouped = grouped.sort_values("weighted_follow_conversion_rate", ascending=False).reset_index()

    fig = px.bar(
        grouped,
        x="content_type_display",
        y="weighted_follow_conversion_rate",
        title="不同体裁加权转粉率（总涨粉/总播放）",
        labels={
            "content_type_display": "体裁",
            "weighted_follow_conversion_rate": "加权转粉率",
        },
        text=grouped["weighted_follow_conversion_rate"].map(lambda x: f"{x:.2%}" if pd.notna(x) else "-"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)


def insight_summary(daily: pd.DataFrame, video: pd.DataFrame) -> None:
    st.subheader("自动洞察摘要")

    peak_play_row = daily.loc[daily["play_total_day"].idxmax()]
    peak_follow_row = daily.loc[daily["followers_new"].idxmax()]

    d = video.dropna(subset=["content_type", "play_count", "follower_gain_count"]).copy()
    d["content_type_display"] = (
        d["content_type"].astype(str).str.strip().replace({"": "未知", "nan": "未知"})
    )
    grouped = d.groupby("content_type_display").agg(
        total_play=("play_count", "sum"),
        total_follow_gain=("follower_gain_count", "sum"),
        video_count=("video_name", "count"),
    )
    grouped["weighted_follow_conversion_rate"] = (
        grouped["total_follow_gain"] / grouped["total_play"]
    ).where(grouped["total_play"] != 0)
    best_type = grouped.sort_values("weighted_follow_conversion_rate", ascending=False).head(1)

    top_video = video.sort_values("follow_conversion_rate", ascending=False).head(1).copy()
    top_video_name = short_title(top_video["video_name"].iloc[0]) if not top_video.empty else "无"
    top_video_conv = top_video["follow_conversion_rate"].iloc[0] if not top_video.empty else 0

    col_i, col_a = st.columns(2)
    with col_i:
        st.markdown("**3条洞察**")
        insights = [
            f"播放峰值出现在 {peak_play_row['date'].date()}，当日播放量 {int(peak_play_row['play_total_day']):,}。",
            f"涨粉峰值出现在 {peak_follow_row['date'].date()}，当日净增粉 {int(peak_follow_row['followers_new']):,}。",
            f"当前筛选下转粉率最高作品为「{top_video_name}」，转粉率 {top_video_conv:.2%}。",
        ]
        for text in insights:
            st.write(f"- {text}")

    with col_a:
        st.markdown("**2条行动建议**")
        actions: list[str] = []
        if not best_type.empty:
            best_name = best_type.index[0]
            best_rate = best_type["weighted_follow_conversion_rate"].iloc[0]
            best_count = int(best_type["video_count"].iloc[0])
            actions.append(
                f"优先加大发布「{best_name}」体裁（样本 {best_count} 条），当前加权转粉率 {best_rate:.2%}。"
            )

        avg_profile_conv = daily["profile_to_follow_rate_day"].mean(skipna=True)
        actions.append(
            f"持续优化主页承接（当前平均主页转粉率 {avg_profile_conv:.2%}），重点测试封面与置顶内容。"
        )
        for text in actions:
            st.write(f"- {text}")


def export_panel(daily: pd.DataFrame, video: pd.DataFrame) -> None:
    st.subheader("导出当前筛选结果")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="下载作品筛选结果 CSV",
            data=video.to_csv(index=False).encode("utf-8-sig"),
            file_name="video_filtered_export.csv",
            mime="text/csv",
        )
    with c2:
        st.download_button(
            label="下载账号日维度筛选结果 CSV",
            data=daily.to_csv(index=False).encode("utf-8-sig"),
            file_name="daily_filtered_export.csv",
            mime="text/csv",
        )


def sidebar_filters(daily: pd.DataFrame, video: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    st.sidebar.header("筛选器")

    min_date = daily["date"].min().date()
    max_date = daily["date"].max().date()
    date_range = st.sidebar.date_input("近30日日期范围", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    daily_filtered = daily[(daily["date"].dt.date >= start_date) & (daily["date"].dt.date <= end_date)].copy()

    types = sorted(video["content_type"].dropna().astype(str).unique().tolist())
    selected_types = st.sidebar.multiselect("作品体裁", options=types, default=types)

    play_min, play_max = int(video["play_count"].min()), int(video["play_count"].max())
    play_range = st.sidebar.slider("作品播放量范围", min_value=play_min, max_value=play_max, value=(play_min, play_max))

    video_filtered = video.copy()
    if selected_types:
        video_filtered = video_filtered[video_filtered["content_type"].astype(str).isin(selected_types)]
    video_filtered = video_filtered[
        (video_filtered["play_count"] >= play_range[0]) & (video_filtered["play_count"] <= play_range[1])
    ]

    return daily_filtered, video_filtered


def main() -> None:
    st.set_page_config(page_title="抖音数据分析看板", layout="wide")
    st.title("抖音账号数据交互式看板")
    st.caption("数据源: data_clean/account_daily_merged_30d.csv + data_clean/video_performance_clean.csv")

    daily, video = load_data()
    daily = add_daily_metrics(daily)
    daily_f, video_f = sidebar_filters(daily, video)

    if daily_f.empty or video_f.empty:
        st.warning("当前筛选条件无数据，请放宽筛选范围。")
        return

    kpi_cards(daily_f, video_f)

    col1, col2 = st.columns(2)
    with col1:
        chart_play_trend(daily_f)
    with col2:
        chart_growth_quality(daily_f)

    col3, col4 = st.columns(2)
    with col3:
        chart_top_videos(video_f)
    with col4:
        chart_quality_quadrant(video_f)

    chart_content_weighted_conversion(video_f)
    insight_summary(daily_f, video_f)
    export_panel(daily_f, video_f)

    st.subheader("筛选后明细预览")
    display_cols = [
        "video_name",
        "publish_time",
        "content_type",
        "play_count",
        "follower_gain_count",
        "follow_conversion_rate",
        "engagement_rate",
    ]
    st.dataframe(video_f[display_cols].sort_values("publish_time", ascending=False), use_container_width=True)


if __name__ == "__main__":
    main()
