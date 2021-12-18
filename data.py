from oauth2client.service_account import ServiceAccountCredentials
import gspread
import util


def lastRow(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list))


def getData():
    scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
            ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            './.sheets_token.json', scope
            )
    gc = gspread.authorize(credentials)
    sheet = gc.open(util.getenv("SHEET_NAME")).sheet1
    odai_list = [cell.value for cell in sheet.range(
        "B2:C{}".format(lastRow(sheet))
    )]
    return [i for i in zip(*[iter(odai_list)]*2)]


if __name__ == "__main__":
    print(getData())
