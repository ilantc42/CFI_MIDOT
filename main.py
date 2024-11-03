from os import environ
import pandas as pd
from google_sheet import upload_spread_sheet
from ngo_list import ngos_ids
import csv

from ranking_service import rank_ngos

FINANCIAL_REPORT_FNAME = "NgoFinanceInfo"
RANKED_FNAME = environ["RANKED_NGO_FNAME"]


def scrape_ngo_finance(ngos_ids: list[int]) -> None:
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from cfi_midot.spiders.guide_star_spider import GuideStarSpider

    process = CrawlerProcess(get_project_settings())
    process.crawl(GuideStarSpider, ngos_ids)
    process.start()


if __name__ == "__main__":
    # with open('./ngos_to_scrape.csv', newline='') as f:
    #     rows = list(csv.reader(f))
    #     if rows:
    #         ngos_ids -= set(rows[0]) # type: ignore

    # Scrape ngos
    scrape_ngo_finance(list(ngos_ids))

    # Load yearly financial reports for each NGO (FINANCIAL_FNAME), group by ngo_id
    financial_df = pd.read_csv(f"./results/{FINANCIAL_REPORT_FNAME}.csv")

    # Sort the financial reports by year and group by report_year
    # Each group is sorted by year in descending order
    financial_df = financial_df.sort_values(by="report_year", ascending=True).groupby(
        ["report_year"]
    )
    # Rank the NGOs for each year
    ranked_dfs = rank_ngos(financial_df)

    # Publish the results to a google spreadsheet
    # Update spreadsheets
    ngo_general_info = pd.read_csv(f"./results/NgoGeneralInfo.csv")
    upload_spread_sheet(ngo_general_info, ranked_dfs)

    # Save the ranks for each year to a separate csv file
    for ranked_df in ranked_dfs:
        ranked_df.to_csv(
            f"./results/{RANKED_FNAME}_{ranked_df['report_year'].iloc[0]}.csv",
            index=False,
        )
