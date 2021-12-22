import json
from typing import Callable
import scrapy
import re
from cfi_midot.items import NgoInfo
from cfi_midot.items_loaders import RESOURCE_NAME_TO_METHOD_NAME, load_ngo_info


HEADERS = {
    "X-User-Agent": "Visualforce-Remoting",
    "Origin": "https://www.guidestar.org.il",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}


def _get_csrf(page_text):
    csrf_re = re.compile(
        r'\{"name":"getUserInfo","len":0,"ns":"","ver":43\.0,"csrf":"([^"]+)"\}'
    )
    csrf, *_ = csrf_re.findall(page_text)
    return csrf


def _get_vid(page_text):
    csrf_re = re.compile(r'RemotingProviderImpl\(\{"vf":\{"vid":"([^"]+)"')
    csrf, *_ = csrf_re.findall(page_text)
    return csrf


def generate_body_payload(
    resources: list[str],
    ngo_num: int,
    page_text: str,
) -> list[dict]:
    csrf = _get_csrf(page_text)
    vid = _get_vid(page_text)

    body_payload: list[dict] = []
    for resource_num, resource in enumerate(resources):
        body_payload.append(
            {
                "action": "GSTAR_Ctrl",
                "method": RESOURCE_NAME_TO_METHOD_NAME[resource],
                "data": [ngo_num],
                "type": "rpc",
                "tid": 3 + resource_num,
                "ctx": {"csrf": csrf, "ns": "", "vid": vid, "ver": 39},
            }
        )
    return body_payload


class GuideStarSpider(scrapy.Spider):
    name = "guidestar"
    # URL to get ngo data
    ngo_xml_data_url = "https://www.guidestar.org.il/apexremote"

    # NGO resources to be scraped
    resources = [
        "general",
        "finance",
        "top_salaries",
    ]

    def __init__(self, ngo_id: int, **kwargs) -> None:
        self.ngo_id = ngo_id
        # Used to build body_payload for ngo_data request
        self.helper_page_url = f"https://www.guidestar.org.il/organization/{ngo_id}"
        HEADERS["Referer"] = self.helper_page_url

        super().__init__(**kwargs)

    def request(self, url: str, callback: Callable) -> scrapy.Request:
        request = scrapy.Request(url=url, callback=callback)
        request.headers["User-Agent"] = HEADERS["User-Agent"]
        return request

    def start_requests(self) -> scrapy.Request:
        yield self.request(self.helper_page_url, self.scrape_xml_data)

    def scrape_xml_data(self, helper_page_response) -> scrapy.Request:

        body_payload = generate_body_payload(
            self.resources, self.ngo_id, helper_page_response.text
        )

        yield scrapy.Request(
            url=self.ngo_xml_data_url,
            method="POST",
            body=json.dumps(body_payload),
            headers=HEADERS,
            callback=self.parse_ngo_response,
        )

    def parse_ngo_response(self, response) -> NgoInfo:
        ngo_scraped_data = response.json()
        self._validate_all_resources_arrived_successfully(ngo_scraped_data)
        ngo_info_item = load_ngo_info(self.ngo_id, ngo_scraped_data)
        yield ngo_info_item

    def _validate_all_resources_arrived_successfully(
        self, ngo_scraped_data: list[dict]
    ) -> None:

        if len(ngo_scraped_data) != len(self.resources):
            raise Exception("Not all resources scraped for ngo")

        for scraped_resource in ngo_scraped_data:
            if scraped_resource["statusCode"] != 200:
                raise Exception(f"Error in resource {scraped_resource['method']}")
            if not scraped_resource["result"]["success"]:
                raise Exception(f"Error in resource {scraped_resource['method']}")


# TODO:Remove DEBUG
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl(GuideStarSpider, 580030104)
    process.start()
