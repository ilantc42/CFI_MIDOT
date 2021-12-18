from cfi_midot.items import (
    NgoInfo,
    NgoGeneralInfo,
    NgoFinanceInfo,
    NgoTopRecipientSalary,
    NgoTopRecipientsSalaries,
)


RESOURCE_NAME_TO_METHOD_NAME = {
    "general": "getMalkarDetails",
    "finance": "getMalkarFinances",
    "top_salaries": "getMalkarWageEarners",
    # "donations": "getMalkarDonations",
}


def _map_between_scraped_and_ngo_item(data_mapper: dict, scraped_data: dict) -> dict:
    ngo_item_data = {}
    for malkar_attr_name, ngo_attr_name in data_mapper.items():
        ngo_item_data[ngo_attr_name] = scraped_data.pop(malkar_attr_name)
    return ngo_item_data


def _malkar_details_parser(scraped_data) -> NgoGeneralInfo:
    general_data_mapper = {
        "Name": "ngo_name",
        "orgGoal": "ngo_goal",
        "orgYearFounded": "ngo_year_founded",
        # TODO add more fields
    }
    ngo_general = _map_between_scraped_and_ngo_item(general_data_mapper, scraped_data)
    return NgoGeneralInfo(**ngo_general)


def _malkar_finance_parser(scraped_data) -> NgoFinanceInfo:
    # We use only the last year data
    scraped_data_from_last_year, *_ = scraped_data

    finance_data_mapper = {
        "Allocations_Government": "allocations_from_government",
        "Allocations_LocalAuthority": "allocations_from_local_authority",
        "Allocations_Other": "allocations_from_other_sources",
        "Donations_Aboard": "donations_from_aboard",
        "Donations_Country": "donations_from_israel",
        "Donations_ValueForMoney": "donations_value_for_money",
        "Expenses_Other": "expenses_other",
        "Expenses_OtherActivities": "expenses_for_activities",
        "Expenses_OtherManagement": "expenses_for_management",
        "Expenses_Salary": "expenses_salary_For_management",
        "Expenses_SalaryActivities": "expenses_salary_For_activities",
        "Incomes_MembersFee": "other_income_members_fee",
        "Incomes_OtherSource": "other_income_from_other_sources",
        "Incomes_ServicesForCountry": "service_income_from_country",
        "Incomes_ServicesForLocalAuthority": "service_income_from_local_authority",
        "Incomes_ServicesForOther": "service_income_from_other",
        "Year": "report_year",
    }
    ngo_finance = _map_between_scraped_and_ngo_item(
        finance_data_mapper, scraped_data_from_last_year
    )
    ngo_finance["report_year"] = int(ngo_finance["report_year"])
    return NgoFinanceInfo(**ngo_finance)


def _malkar_wage_earners_parser(scraped_data) -> NgoTopRecipientsSalaries:
    # We use only the last year data
    scraped_data_from_last_year, *_ = scraped_data

    # We assumes that Amount is in NIS
    earner_salary_mapper = {
        "MainLabel": "recipient_title",
        "Amount": "gross_salary_in_nis",
    }

    top_earners_salaries = []
    for earner_salary in scraped_data_from_last_year["Data"]:
        earner_salary_data = _map_between_scraped_and_ngo_item(
            earner_salary_mapper, earner_salary
        )
        top_earners_salaries.append(NgoTopRecipientSalary(**earner_salary_data))
    report_year = int(
        scraped_data_from_last_year["Label"].replace(" - שכר לשנה ברוטו", "")
    )
    return NgoTopRecipientsSalaries(
        report_year=report_year, top_earners_salaries=top_earners_salaries
    )


METHOD_NAME_TO_ITEM_PARSER = {
    "getMalkarDetails": _malkar_details_parser,
    "getMalkarFinances": _malkar_finance_parser,
    "getMalkarWageEarners": _malkar_wage_earners_parser,
}


def load_ngo_info(ngo_id, ngo_scraped_result: list[dict]) -> NgoInfo:
    resource_items = {}
    for scraped_result in ngo_scraped_result:
        parser = METHOD_NAME_TO_ITEM_PARSER[scraped_result["method"]]
        scraped_data = scraped_result["result"]["result"]
        resource_item = parser(scraped_data)
        resource_items[resource_item.resource_name] = resource_item
    return NgoInfo.from_resource_items(ngo_id, resource_items)
