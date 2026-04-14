from pathlib import Path
import pandas as pd  # pyright: ignore[reportMissingImports]


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "dataset"
OUT_DIR = BASE_DIR / "data_clean"


def to_numeric(series: pd.Series) -> pd.Series:
    """Extract numeric values from string/object columns."""
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Avoid division-by-zero and return NaN for invalid rows."""
    result = numerator / denominator
    return result.where(denominator.notna() & (denominator != 0))


def add_video_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add four core derived metrics for video-level analysis."""
    interactions = (
        df["like_count"] + df["comment_count"] + df["share_count"] + df["favorite_count"]
    )
    df["engagement_rate"] = safe_divide(interactions, df["play_count"])
    df["follow_conversion_rate"] = safe_divide(df["follower_gain_count"], df["play_count"])
    df["profile_to_follow_rate"] = safe_divide(
        df["follower_gain_count"], df["profile_visit_count"]
    )
    df["retention_quality_score"] = df["completion_rate"] * (1 - df["bounce_rate_2s"])
    return df


def clean_video_table(file_path: Path) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    rename_map = {
        "作品名称": "video_name",
        "发布时间": "publish_time",
        "体裁": "content_type",
        "审核状态": "review_status",
        "播放量": "play_count",
        "完播率": "completion_rate",
        "5s完播率": "completion_rate_5s",
        "封面点击率": "cover_ctr",
        "2s跳出率": "bounce_rate_2s",
        "平均播放时长": "avg_watch_time_sec",
        "点赞量": "like_count",
        "分享量": "share_count",
        "评论量": "comment_count",
        "收藏量": "favorite_count",
        "主页访问量": "profile_visit_count",
        "粉丝增量": "follower_gain_count",
    }
    df = df.rename(columns=rename_map)

    # Some exports may omit low-value/all-zero columns; backfill them for pipeline stability.
    expected_video_cols = [
        "video_name",
        "publish_time",
        "content_type",
        "review_status",
        "play_count",
        "completion_rate",
        "completion_rate_5s",
        "cover_ctr",
        "bounce_rate_2s",
        "avg_watch_time_sec",
        "like_count",
        "share_count",
        "comment_count",
        "favorite_count",
        "profile_visit_count",
        "follower_gain_count",
    ]
    for col in expected_video_cols:
        if col not in df.columns:
            df[col] = pd.NA

    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")

    numeric_cols = [
        "play_count",
        "completion_rate",
        "completion_rate_5s",
        "cover_ctr",
        "bounce_rate_2s",
        "avg_watch_time_sec",
        "like_count",
        "share_count",
        "comment_count",
        "favorite_count",
        "profile_visit_count",
        "follower_gain_count",
    ]
    for col in numeric_cols:
        df[col] = to_numeric(df[col])

    df = add_video_derived_metrics(df)
    df = df.sort_values("publish_time", ascending=False).reset_index(drop=True)
    return df


def build_daily_indicator_map(raw_dir: Path) -> dict:
    file_to_metric = {
        "daily_plays.xlsx": "play_total_day",
        "daily_profile_visits.xlsx": "profile_visit_day",
        "daily_likes.xlsx": "like_total_day",
        "daily_shares.xlsx": "share_total_day",
        "daily_comments.xlsx": "comment_total_day",
        "daily_cover_ctr.xlsx": "cover_ctr_day",
        "daily_new_followers.xlsx": "followers_new",
        "daily_unfollowers.xlsx": "followers_lost",
        "daily_total_followers.xlsx": "followers_total",
    }
    mapping = {}
    for file_name, metric_col in file_to_metric.items():
        path = raw_dir / file_name
        if path.exists():
            mapping[path] = metric_col
    return mapping


def clean_daily_table(daily_file_map: dict) -> pd.DataFrame:
    merged = None

    for file_path, std_col in daily_file_map.items():
        df = pd.read_excel(file_path)
        df = df.rename(columns={"日期": "date"})

        value_cols = [c for c in df.columns if c != "date"]
        if len(value_cols) != 1:
            raise ValueError(f"{file_path.name} 应仅包含1个指标列，实际为: {value_cols}")

        value_col = value_cols[0]
        df = df.rename(columns={value_col: std_col})

        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df[std_col] = to_numeric(df[std_col])

        merged = df if merged is None else merged.merge(df, on="date", how="outer")

    merged = merged.sort_values("date").reset_index(drop=True)
    return merged


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    video_file = RAW_DIR / "video_list.xlsx"
    if not video_file.exists():
        raise FileNotFoundError(f"未找到作品列表文件: {video_file}")

    daily_file_map = build_daily_indicator_map(RAW_DIR)
    if not daily_file_map:
        raise FileNotFoundError("未找到任何 daily_*.xlsx 文件")

    video_df = clean_video_table(video_file)
    daily_df = clean_daily_table(daily_file_map)

    video_csv = OUT_DIR / "video_performance_clean.csv"
    daily_csv = OUT_DIR / "account_daily_merged_30d.csv"
    video_xlsx = OUT_DIR / "video_performance_clean.xlsx"
    daily_xlsx = OUT_DIR / "account_daily_merged_30d.xlsx"

    video_df.to_csv(video_csv, index=False, encoding="utf-8-sig")
    daily_df.to_csv(daily_csv, index=False, encoding="utf-8-sig")
    video_df.to_excel(video_xlsx, index=False)
    daily_df.to_excel(daily_xlsx, index=False)

    print("清洗与合并完成:")
    print(f"- 作品维度: {video_xlsx} ({video_df.shape[0]}行, {video_df.shape[1]}列)")
    print(f"- 账号日维度: {daily_xlsx} ({daily_df.shape[0]}行, {daily_df.shape[1]}列)")


if __name__ == "__main__":
    main()
