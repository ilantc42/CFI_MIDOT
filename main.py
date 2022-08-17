from google_sheet import upload_spread_sheet
from ngo_list import ngos_ids
import csv

from ranking import rank_ngos


def scrape_ngo_finance(ngos_ids: list[int]) -> None:
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from cfi_midot.spiders.guide_star_spider import GuideStarSpider

    process = CrawlerProcess(get_project_settings())
    process.crawl(GuideStarSpider, ngos_ids)
    process.start()


if __name__ == "__main__":
    with open('./ngos_to_scrape.csv', newline='') as f:
        rows = list(csv.reader(f))
        if rows:
            ngos_ids -= set(rows[0])

    # # # Scrape ngos
    scrape_ngo_finance(list(ngos_ids))

    # # Rank scraped ngos
    rank_ngos()

    # Update spreadsheets
    upload_spread_sheet()
