from glob import glob
from typing import Counter, List, Optional
from marshmallow import fields
from googleapiclient import discovery
from pprint import pprint
from os import environ
from google.oauth2 import service_account
from itertools import count
import pandas as pd
import numpy as np

from cfi_midot.items import OrderedSchema


# Files to write from
UNRANKED_FNAME = environ["UNRANKED_NGO_FNAME"]
RANKED_FNAME = environ["RANKED_NGO_FNAME"]
# The ID of the spreadsheet to update.
PUBLIC_SPREADSHEET_ID = environ["PUBLIC_SPREADSHEET_ID"]
APPSHEET_SPREADSHEET_ID = environ["APPSHEET_SPREADSHEET_ID"]
APPSHEET_SHEET_ID = int(environ["APPSHEET_SHEET_ID"])
UNRANKED_SHEET_ID = int(environ["UNRANKED_SHEET_ID"])
RANKED_SHEET_ID = int(environ["RANKED_SHEET_ID"])
# How the input data should be interpreted.
VALUE_INPUT_OPTION = 'RAW'



# Dynamically change the report year. 
def _get_ranked_sheet_schema(report_year: int) -> OrderedSchema:

    class RankedSheetSchema(OrderedSchema):
        
        # Org
        ngo_id = fields.Int(data_key="מזהה עמותה")
        ngo_name = fields.Str(attribute="ngo_name", allow_none=True, data_key="שם עמותה")
        main_activity_field = fields.Str(
            attribute="main_activity_field", allow_none=True, data_key="תחום פעילות מרכזי")
        last_financial_report_year = fields.Integer(
            attribute="report_year", data_key="שנת דוח כספי אחרון")
        yearly_turnover_category_label = fields.String(
            attribute="yearly_turnover_category_label", allow_none=True,
            data_key=f"קטגוריית מחזור שנתי לשנת {report_year}",)
        _ = fields.Str(dump_default=None)

        # -- Ranks --
        main_rank_benchmark = fields.Number(dump_default=None,
                                            data_key="ציון ממוצע לקטגורית מחזור")
        main_rank = fields.Number(dump_default=None,
                                data_key=f"ציון כלכלי משוקלל לשנת {report_year}")

        percentile_num = fields.Integer(allow_none=True, dump_default=None,
                                        data_key="מספר חמישיון")
        percentile_label = fields.String(allow_none=True, dump_default=None,
                                        data_key="חמישיון ביחס לקטגורית מחזור")

        __ = fields.Str(dump_default=None)
        # -- Sub Ranks --
        growth_rank = fields.Number(dump_default=None,
                                    data_key=f"ציון {report_year}- צמיחה")
        balance_rank = fields.Number(dump_default=None,
                                    data_key=f"ציון {report_year}- גירעון/יתרה")
        stability_rank = fields.Number(dump_default=None,
                                    data_key=f"ציון {report_year}- גיוון מקורות הכנסה")
        ___ = fields.Str(dump_default=None)

        admin_expense_ratio = fields.Number(
            attribute="admin_expense_ratio", allow_none=True,
            data_key="אחוז הוצאות עבור הנהלה")
        admin_expense_benchmark = fields.Number(
            dump_default=None,
            data_key="בנצמרק אחוז הנהלה")
        ____ = fields.Str(dump_default=None)
        # -----------------------------------------------------------------------------------------------------------------------------------------------

        # Growth params---------------
        growth_benchmark = fields.Number(
            dump_default=None,
            data_key="בנצמרק צמיחה")
        growth_ratio = fields.Number(attribute="growth_ratio", data_key=f"אחוז צמיחה - {report_year}-{report_year-2}")
        yearly_turnover = fields.Number(load_default=None, data_key=f"מחזור שנתי לשנת {report_year}")
        yearly_turnover_1 = fields.Number(load_default=None, attribute=f"yearly_turnover_{report_year-1}", data_key=f"מחזור שנתי לשנת {report_year-1}")
        yearly_turnover_2 = fields.Number(load_default=None, attribute=f"yearly_turnover_{report_year-2}", data_key=f"מחזור שנתי לשנת {report_year-2}")
        yearly_turnover_3 = fields.Number(load_default=None, attribute=f"yearly_turnover_{report_year-3}", data_key=f"מחזור שנתי לשנת {report_year-3}")

        
        
        _____ = fields.Str(dump_default=None)
        # -----------------------------------------------------------------------------------------------------------------------------------------------

        # Profit Params-------------------
        balance_benchmark = fields.Number(dump_default=None, data_key="בנצמרק גרעון")
        balance_ratio = fields.Number(attribute="balance_ratio",
                                    data_key=f"אחוז יתרה לשנת {report_year}")
        last_annual_balance = fields.Number(attribute="annual_balance",
                                            data_key=f"יתרה לשנת {report_year}")
        ______ = fields.Str(dump_default=None)
        # -----------------------------------------------------------------------------------------------------------------------------------------------

        # Stability Params
        max_income_benchmark = fields.Number(
            dump_default=None,
            data_key="בנצמרק גיוון")
        max_income_source_label = fields.String(
            attribute="max_income_source_label", allow_none=True,
            data_key="מקור הכנסה מרכזי")
        max_income_ratio = fields.Number(
            attribute="max_income_ratio", allow_none=True,
            data_key="אחוז מקור הכנסה מרכזי ביחס לסך הכנסות")

        # Income sources ratios
        total_allocations_income_ratio = fields.Number(
            attribute="total_allocations_income_ratio", allow_none=True, data_key="אחוז הכנסות מהקצאות")
        total_donations_income_ratio = fields.Number(
            attribute="total_donations_income_ratio", allow_none=True, data_key="אחוז הכנסות מתרומות")
        total_service_income_ratio = fields.Number(
            attribute="total_service_income_ratio", allow_none=True, data_key="אחוז הכנסות מפעילות")
        total_other_income_ratio = fields.Number(
            attribute="total_other_income_ratio", allow_none=True, data_key="אחוז הכנסות אחרות")
        # Computed totals
        total_allocations_income = fields.Number(
            attribute="total_allocations_income", data_key="הכנסות מהקצאות")
        total_donations_income = fields.Number(
            attribute="total_donations_income", data_key="הכנסות מתרומות")
        total_service_income = fields.Number(
            attribute="total_service_income", data_key="הכנסות מפעילות")
        total_other_income = fields.Number(
            attribute="total_other_income", data_key="הכנסות אחרות")
        _______ = fields.Str(dump_default=None)

        # -----------------------------------------------------------------------------------------------------------------------------------------------
        # Mangemnet
        expenses_for_management = fields.Number(
            attribute="expenses_for_management"
        )
        expenses_salary_for_management = fields.Number(
            attribute="expenses_salary_for_management"
        )
        ________ = fields.Str(dump_default=None)
        
    return RankedSheetSchema


def authenticate():
    scopes = ['https://www.googleapis.com/auth/drive']
    service_account_file = 'test-001-cfi.json'

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    return credentials


def _get_batch(lst: list, n: int, counter: count) -> list:
    """Yield successive n-sized chunks from lst."""
    i = next(counter) * n
    return lst[i:i + n]


def write_to_sheet(
        credentials, spreadsheet_id: str, sheet_name: str, values_to_write: list[list], sheet_id: Optional[int] = None,
        batch_num=5) -> None:
    """ Assumes the sheet is already created and has the first two rows filled with headers and data."""

    service = discovery.build('sheets', 'v4', credentials=credentials)

    batch_size = len(values_to_write) // batch_num or batch_num
    counter = count()
    for n in range(batch_num):
        batch = _get_batch(values_to_write, batch_size, counter)
        if not batch:
            break

        # The A1 notation of the values to update.
        range_ = f'{sheet_name}!$A{3+n*batch_size}'

        request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_,
                                                         valueInputOption=VALUE_INPUT_OPTION, body=dict(values=batch))
        response = request.execute()

        # TODO: Change code below to process the `response` dict.
        pprint(response)


def delete_sheet_rows(
        credentials, spreadsheet_id: str, sheet_id: int) -> None:
    service = discovery.build('sheets', 'v4', credentials=credentials)

    # The A1 notation of the values to update.
    request_body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetName": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 4,
                    }
                }
            }
        ]
    }
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    pprint(response)


def _get_publish_sheet_values(general_info: pd.DataFrame, ranked_dfs: List[pd.DataFrame]) -> dict[int, list]:
    """Get the values to publish to the public spreadsheet.
    seperated by years 
    """
    values = dict()
    for idx, ranked_df in enumerate(ranked_dfs):
        # Add general info to each ranked df
        df_to_publish = ranked_df.merge(general_info, on="ngo_id", how="left")
        df_to_publish = df_to_publish.replace(np.nan, None, regex=True)
        # Dump the ranked df to a list of dicts
        rank_year = int(df_to_publish["report_year"].iloc[0])
        sheet_schema = _get_ranked_sheet_schema(rank_year)
        records = sheet_schema(many=True).dump(df_to_publish.to_dict(orient="records"))
        # # Flatten the list of dicts to a list of lists
        records = [list(record.values()) for record in records]
        
        values[rank_year] = records
    
    return values

def load_all_ranked_years() -> List[list]:
    # Find all available ranking csv files and load them to dataframe.
    ranked_years  = []
    ranked_files = glob(f"./results/{RANKED_FNAME}_*.csv")
    for ranked_file in ranked_files:
        ranked_year = pd.read_csv(ranked_file)
        ranked_year.replace(np.nan, "", inplace=True)
        ranked_years.append(ranked_year.values.tolist())
    return ranked_years


def upload_spreadsheets():
    credentials = authenticate()
    
    ranked_ngo_values = load_all_ranked_years()
    
    for ranked_ngo_value in ranked_ngo_values:
        write_to_sheet(credentials, PUBLIC_SPREADSHEET_ID, "ngo_ranking_2020", ranked_ngo_value)


def upload_spread_sheet(general_info: pd.DataFrame, ranked_dfs: List[pd.DataFrame]) -> None:
    credentials = authenticate()

    publish_sheet_values = _get_publish_sheet_values(general_info, ranked_dfs)
    for year, ranks in publish_sheet_values.items():
        # delete_sheet_rows(credentials, PUBLIC_SPREADSHEET_ID, )
        write_to_sheet(credentials, PUBLIC_SPREADSHEET_ID, f"ngo_ranking_{year}", ranks)

    
    # write_to_sheet(credentials, PUBLIC_SPREADSHEET_ID, "ngo_ranking_2021", ranked_ngo_values, 2050523732)
    # unranked_ngo_values = _load_csv_values(UNRANKED_FNAME)


    # delete_sheet_rows(credentials, APPSHEET_SPREADSHEET_ID, APPSHEET_SHEET_ID)
    # write_to_sheet(credentials, APPSHEET_SPREADSHEET_ID, "ngo_ranking_2020", ranked_ngo_values, APPSHEET_SHEET_ID)

    # # delete_sheet_rows(credentials, APPSHEET_SPREADSHEET_ID, APPSHEET_SHEET_ID)
    # write_to_sheet(credentials, APPSHEET_SPREADSHEET_ID, "ngo_ranking", ranked_ngo_values, APPSHEET_SHEET_ID)
