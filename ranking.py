import pandas as pd
import numpy as np
from cfi_midot.items import UnrankedNGOResult

from os import environ

# Files to write from
UNRANKED_FNAME = environ["UNRANKED_NGO_FNAME"]
RANKED_FNAME = environ["RANKED_NGO_FNAME"]


class Rank:
    d = 40
    c = 60
    b = 80
    a = 100


def growth_rank(growth_ratio: float) -> int:
    if growth_ratio < -0.1:
        return Rank.d
    if growth_ratio < -0.05:
        return Rank.c
    if growth_ratio < 0.05:
        return Rank.b
    return Rank.a


def balance_rank(balance_ratio: float) -> int:
    if balance_ratio < -0.1:
        return Rank.d
    if balance_ratio < -0.05:
        return Rank.c
    if balance_ratio < 0.05:
        return Rank.b
    return Rank.a


def stability_rank(max_income_ratio: float) -> int:
    if max_income_ratio < 0.5:
        return Rank.a
    if max_income_ratio < 0.7:
        return Rank.b
    if max_income_ratio < 0.9:
        return Rank.c
    return Rank.d


def percentile_label(percentile: int) -> str:
    match percentile:
        case 1:
            return "נמוך מאוד ביחס לקט' מחזור"
        case 2:
            return "נמוך ביחס לקט' מחזור"
        case 3:
            return "דומה ביחס לקט' מחזור"
        case 4:
            return "גבוה ביחס לקט' מחזור"
        case 5:
            return "גבוה מאוד ביחס לקט' מחזור"
        case _:
            raise ValueError("No matching percentile: ", percentile)


def enrich_df_with_means(df: pd.DataFrame) -> None:
    s = UnrankedNGOResult()
    grouped_df = df.groupby(s.yearly_turnover_category_label.data_key)  # type: ignore
    for ratio in ["admin_expense", "growth", "balance", "max_income"]:
        ratio_key = getattr(s, f"{ratio}_ratio").data_key
        benchmark_key = getattr(s, f"{ratio}_benchmark").data_key
        df[benchmark_key] = grouped_df[ratio_key].transform('mean')

    # Add main rank mean too
    main_rank: str = s.main_rank.data_key  # type: ignore
    df[s.main_rank_benchmark.data_key] = grouped_df[main_rank].transform('mean')


def enrich_df_with_ranks(df: pd.DataFrame) -> None:
    s = UnrankedNGOResult()

    growth_r: str = s.growth_ratio.data_key  # type: ignore
    balance_r: str = s.balance_ratio.data_key  # type: ignore
    max_income_r: str = s.max_income_ratio.data_key  # type: ignore
    df[s.growth_rank.data_key] = df[growth_r].apply(growth_rank).astype(int)
    df[s.balance_rank.data_key] = df[balance_r].apply(balance_rank).astype(int)
    df[s.stability_rank.data_key] = df[max_income_r].apply(stability_rank).astype(int)

    total_rank: str = s.main_rank.data_key  # type: ignore
    df[total_rank] = (
        0.4 * df[s.growth_rank.data_key] + 0.4 * df[s.balance_rank.data_key] + 0.2 *
        df[s.stability_rank.data_key]).astype(int)

    percentile: str = s.percentile_num.data_key  # type: ignore
    turnover_cat: str = s.yearly_turnover_category_label.data_key  # type: ignore
    grouped_df = df.groupby(turnover_cat)
    df[percentile] = np.ceil(grouped_df[total_rank].transform('rank', pct=True).values / 0.2).astype(int)
    df[s.percentile_label.data_key] = df[percentile].apply(percentile_label)


def rank_ngos() -> None:
    df = pd.read_csv(f"./results/{UNRANKED_FNAME}.csv")
    enrich_df_with_ranks(df)
    enrich_df_with_means(df)
    df.to_csv(f"./results/{RANKED_FNAME}.csv", index=False)
