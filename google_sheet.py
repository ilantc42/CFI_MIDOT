from typing import Optional
from googleapiclient import discovery
from pprint import pprint
from os import environ
from google.oauth2 import service_account
from itertools import count
import pandas as pd
import numpy as np


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


def authenticate():
    scopes = ['https://www.googleapis.com/auth/drive']
    service_account_file = 'test-001-cfi.json'

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    return credentials


def _get_batch(lst: list, n: int, counter=count()) -> list:
    """Yield successive n-sized chunks from lst."""
    i = next(counter) * n
    return lst[i:i + n]


def write_to_sheet(
        credentials, spreadsheet_id: str, sheet_name: str, values_to_write: list[list], sheet_id: Optional[int] = None,
        batch_num=5) -> None:
    service = discovery.build('sheets', 'v4', credentials=credentials)

    batch_size = len(values_to_write) // batch_num or batch_num

    body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 3,
                        "endIndex": (batch_num * batch_size) + 1
                    },
                    "inheritFromBefore": True,
                },

            },
        ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body)
    response = request.execute()
    for n in range(batch_num):
        batch = _get_batch(values_to_write, batch_size)
        if not batch:
            break

        # The A1 notation of the values to update.
        range_ = f'{sheet_name}!$A{3 + n*batch_size}'

        request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_,
                                                         valueInputOption=VALUE_INPUT_OPTION, body=dict(values=batch))
        response = request.execute()

        # TODO: Change code below to process the `response` dict:
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
                        "sheetId": sheet_id,
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


def _load_csv_values(fname: str, clear_none: Optional[str] = None) -> list[list]:
    df = pd.read_csv(f"./results/{fname}.csv")
    df.replace(np.nan, clear_none, inplace=True)
    return df.values.tolist()


def upload_spread_sheet():
    credentials = authenticate()

    ranked_ngo_values = _load_csv_values(f"{RANKED_FNAME}")
    # delete_sheet_rows(credentials, APPSHEET_SPREADSHEET_ID, APPSHEET_SHEET_ID)
    # write_to_sheet(credentials, APPSHEET_SPREADSHEET_ID, "appsheet", ranked_ngo_values, APPSHEET_SHEET_ID)

    delete_sheet_rows(credentials, PUBLIC_SPREADSHEET_ID, RANKED_SHEET_ID)
    write_to_sheet(credentials, PUBLIC_SPREADSHEET_ID, "values_ngo_ranking", ranked_ngo_values, RANKED_SHEET_ID)

    # unranked_ngo_values = _load_csv_values(UNRANKED_FNAME)
    # write_to_sheet(credentials, PUBLIC_SPREADSHEET_ID, "formulas_ngo_ranking", unranked_ngo_values)
