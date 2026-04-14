from pathlib import Path
import re

import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingImports]


BASE_DIR = Path(__file__).resolve().parent
CLEAN_DIR = BASE_DIR / "data_clean"
FIG_DIR = BASE_DIR / "report" / "figures"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def setup_output_dir() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def short_video_title(title: object, max_len: int = 10) -> str:
    text = "" if pd.isna(title) else str(title).strip()
    if not text or text in {"无标题", "nan", "None"}:
        return "自拍照"

    # Keep readable Chinese/English/digit title chars and drop emojis/symbol noise.
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text)
    if not text:
        return "自拍照"
    return text[:max_len]


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = pd.read_csv(CLEAN_DIR / "account_daily_merged_30d.csv")
    video = pd.read_csv(CLEAN_DIR / "video_performance_clean.csv")

    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    video["publish_time"] = pd.to_datetime(video["publish_time"], errors="coerce")
    return daily, video


def save_daily_play_trend(daily: pd.DataFrame) -> None:
    df = daily.sort_values("date").copy()
    df["play_7d_ma"] = df["play_total_day"].rolling(window=7, min_periods=1).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["play_total_day"], marker="o", linewidth=1.5, label="Daily Plays")
    plt.plot(df["date"], df["play_7d_ma"], linewidth=2.0, label="7-day MA")
    plt.title("30-Day Play Trend")
    plt.xlabel("Date")
    plt.ylabel("Play Count")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_daily_play_trend.png", dpi=180)
    plt.close()


def save_follow_growth_quality(daily: pd.DataFrame) -> None:
    df = daily.sort_values("date").copy()

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["followers_new"], marker="o", linewidth=1.5, label="Net New Followers")
    plt.plot(df["date"], df["followers_lost"], marker="o", linewidth=1.5, label="Unfollowers")
    plt.title("30-Day Follower Growth Quality")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_follower_growth_quality.png", dpi=180)
    plt.close()


def save_daily_engagement_rate(daily: pd.DataFrame) -> None:
    df = daily.sort_values("date").copy()
    interactions = df["like_total_day"] + df["comment_total_day"] + df["share_total_day"]
    df["engagement_rate_day"] = (interactions / df["play_total_day"]).where(df["play_total_day"] != 0)
    df["engagement_rate_7d_ma"] = df["engagement_rate_day"].rolling(window=7, min_periods=1).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["engagement_rate_day"], marker="o", linewidth=1.5, label="Daily Engagement Rate")
    plt.plot(df["date"], df["engagement_rate_7d_ma"], linewidth=2.0, label="7-day MA")
    plt.title("30-Day Engagement Rate Trend")
    plt.xlabel("Date")
    plt.ylabel("Rate")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "03_daily_engagement_rate.png", dpi=180)
    plt.close()


def save_profile_follow_conversion(daily: pd.DataFrame) -> None:
    df = daily.sort_values("date").copy()
    df["profile_to_follow_rate_day"] = (
        df["followers_new"] / df["profile_visit_day"]
    ).where(df["profile_visit_day"] != 0)
    df["profile_to_follow_rate_7d_ma"] = (
        df["profile_to_follow_rate_day"].rolling(window=7, min_periods=1).mean()
    )

    plt.figure(figsize=(10, 5))
    plt.plot(
        df["date"],
        df["profile_to_follow_rate_day"],
        marker="o",
        linewidth=1.5,
        label="Daily Profile->Follow Rate",
    )
    plt.plot(
        df["date"],
        df["profile_to_follow_rate_7d_ma"],
        linewidth=2.0,
        label="7-day MA",
    )
    plt.title("30-Day Profile-to-Follow Conversion")
    plt.xlabel("Date")
    plt.ylabel("Rate")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "04_profile_to_follow_conversion.png", dpi=180)
    plt.close()


def save_top10_videos(video: pd.DataFrame) -> None:
    df = video.sort_values("play_count", ascending=False).head(10).copy()
    labels = [short_video_title(name) for name in df["video_name"]]

    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], df["play_count"].values[::-1])
    plt.title("Top 10 Videos by Play Count")
    plt.xlabel("Play Count")
    plt.ylabel("Video")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "05_top10_videos_by_play.png", dpi=180)
    plt.close()


def save_quality_quadrant(video: pd.DataFrame) -> None:
    df = video.dropna(subset=["completion_rate", "follow_conversion_rate", "play_count"]).copy()
    if df.empty:
        return

    x_mean = df["completion_rate"].mean()
    y_mean = df["follow_conversion_rate"].mean()
    bubble_size = (df["play_count"] / df["play_count"].max()) * 800 + 40

    plt.figure(figsize=(9, 6))
    plt.scatter(df["completion_rate"], df["follow_conversion_rate"], s=bubble_size, alpha=0.6)
    plt.axvline(x=x_mean, linestyle="--", linewidth=1)
    plt.axhline(y=y_mean, linestyle="--", linewidth=1)
    plt.title("Video Quality Quadrant")
    plt.xlabel("Completion Rate")
    plt.ylabel("Follow Conversion Rate")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "06_quality_quadrant.png", dpi=180)
    plt.close()


def save_publish_heatmap(video: pd.DataFrame) -> None:
    df = video.dropna(subset=["publish_time", "play_count"]).copy()
    df["weekday"] = df["publish_time"].dt.dayofweek
    df["hour"] = df["publish_time"].dt.hour

    pivot = df.pivot_table(index="weekday", columns="hour", values="play_count", aggfunc="mean")
    pivot = pivot.reindex(index=range(7), columns=range(24))

    plt.figure(figsize=(12, 4))
    img = plt.imshow(pivot.fillna(0).values, aspect="auto")
    plt.colorbar(img, label="Average Play Count")
    plt.yticks(
        ticks=range(7),
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    )
    plt.xticks(ticks=range(0, 24, 2), labels=[str(i) for i in range(0, 24, 2)])
    plt.title("Publish Time Heatmap (Weekday x Hour)")
    plt.xlabel("Hour")
    plt.ylabel("Weekday")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "07_publish_time_heatmap.png", dpi=180)
    plt.close()


def save_content_type_comparison(video: pd.DataFrame) -> None:
    df = video.dropna(subset=["content_type", "play_count", "follower_gain_count"]).copy()
    df["content_type_display"] = (
        df["content_type"].astype(str).str.strip().replace({"": "未知", "nan": "未知"})
    )
    grouped = df.groupby("content_type_display", dropna=False).agg(
        total_play=("play_count", "sum"),
        total_follow_gain=("follower_gain_count", "sum"),
    )
    grouped["weighted_follow_conversion_rate"] = (
        grouped["total_follow_gain"] / grouped["total_play"]
    ).where(grouped["total_play"] != 0)
    grouped = grouped.sort_values("weighted_follow_conversion_rate", ascending=False)
    plot_series = grouped["weighted_follow_conversion_rate"]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(plot_series.index.astype(str), plot_series.values)
    plt.title("Content Type Comparison (Weighted Follow Conversion)")
    plt.xlabel("Content Type")
    plt.ylabel("Weighted Follow Conversion Rate")
    plt.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, plot_series.values):
        if pd.notna(value):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                f"{value:.2%}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(FIG_DIR / "08_content_type_comparison.png", dpi=180)
    plt.close()


def main() -> None:
    setup_output_dir()
    daily, video = load_data()

    save_daily_play_trend(daily)
    save_follow_growth_quality(daily)
    save_daily_engagement_rate(daily)
    save_profile_follow_conversion(daily)
    save_top10_videos(video)
    save_quality_quadrant(video)
    save_publish_heatmap(video)
    save_content_type_comparison(video)

    print(f"图表已生成: {FIG_DIR}")


if __name__ == "__main__":
    main()
