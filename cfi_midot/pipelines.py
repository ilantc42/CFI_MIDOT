from scrapy.exporters import CsvItemExporter

from cfi_midot.items import (
    NgoFinanceInfoSchema,
    NgoGeneralInfoSchema,
    NgoInfo,
)
from os import environ



def item_type(item):
    return type(item).__name__


class GuideStarMultiCSVExporter(object):
    defined_items = ["NgoFinanceInfo", "NgoTopRecipientsSalaries", 
                     "filtered_ngos", "NgoGeneralInfo"]

    def open_spider(self, spider):
        self.files = dict(
            [(name, open(f"results/{name}.csv", "w+b")) for name in self.defined_items]
        )
        self.exporters = dict(
            [(name, CsvItemExporter(self.files[name])) for name in self.defined_items]
        )

        for exporter in self.exporters.values():
            exporter.start_exporting()

    def _multi_exporter_for_item(self, item: NgoInfo) -> None:

        if item.financial_info:
            financial_info = NgoFinanceInfoSchema(many=True).dump(item.financial_info)
            for report in financial_info:
                self.exporters["NgoFinanceInfo"].export_item(report)

        if item.general_info:
            general_info = NgoGeneralInfoSchema().dump(item.general_info)
            self.exporters["NgoGeneralInfo"].export_item(general_info)

        # if item.top_earners_info:
        #     top_earners_info = NgoTopRecipientsSalariesSchema(many=True).dump(
        #         item.top_earners_info
        #     )
        #     for report in top_earners_info:
        #         self.exporters["NgoTopRecipientsSalaries"].export_item(top_earners_info)

    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item: NgoInfo | dict, spider):
        if isinstance(item, dict):
            self.exporters["filtered_ngos"].export_item(item)
        else:
            self._multi_exporter_for_item(item)
        return item
