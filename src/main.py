import pandas as pd
from ngo_toolkit.uploaders.google_sheet import upload_spread_sheet
from ngo_toolkit.scrapers.api_interaction import download_registered_ngos_ids

from ngo_toolkit.ranking.ranking_service import rank_ngos
from ngo_toolkit.settings import settings

FINANCIAL_REPORT_SHEET_NAME = "NgoFinanceInfo"
GENERAL_REPORT_SHEET_NAME = "NgoGeneralInfo"
RANKED_NGO_SHEET_NAME = settings.RANKED_NGO_SHEET_NAME

def scrape_ngo_finance(ngos_ids: list[int]) -> None:
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from ngo_toolkit.scrapers.cfi_midot_scrapy.spiders.guide_star_spider import GuideStarSpider

    process = CrawlerProcess(get_project_settings())

    process.crawl(GuideStarSpider, ngos_ids)

    process.start()


def main():
    # # Download latest registered NGOs from https://data.gov.il/dataset/moj-amutot
    ngos_ids = download_registered_ngos_ids()

    # # Scrape ngos
    scrape_ngo_finance(ngos_ids)

    # Load yearly financial reports for each NGO (FINANCIAL_FNAME), group by ngo_id
    financial_df = pd.read_csv(f"data/{FINANCIAL_REPORT_SHEET_NAME}.csv")

    # Sort the financial reports by year and group by report_year
    # Each group is sorted by year in descending order
    financial_df = financial_df.sort_values(by="report_year", ascending=True).groupby(
        ["report_year"]
    )
    # Rank the NGOs for each year
    ranked_dfs = rank_ngos(financial_df)

    # Publish the results to a google spreadsheet
    # Update spreadsheets
    ngo_general_info = pd.read_csv(f"data/{GENERAL_REPORT_SHEET_NAME}.csv")
    upload_spread_sheet(ngo_general_info, ranked_dfs)

    # Save the ranks for each year to a separate csv file
    for ranked_df in ranked_dfs:
        ranked_df.to_csv(
            f"data/{RANKED_NGO_SHEET_NAME}_{ranked_df['report_year'].iloc[0]}.csv",
            index=False,
        )


if __name__ == "__main__":
    main()