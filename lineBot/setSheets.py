import os
import decodeJson
import gspread
from google.oauth2 import service_account

HEADERS = ["会社名", "部署名", "氏名", "会社住所", "電話番号", "e-mailアドレス"]

# スプシに書き込み(引数：辞書型)
def set_sheets(dictItems: dict):

    try:
        # 認証情報の設定
        encoded_str = os.getenv('SHEETS_JSON_STR')
        dict_data = decodeJson.decode_json(encoded_str=encoded_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_info(dict_data, scopes=scope)
        client = gspread.authorize(creds)

        # Google Sheetsの特定のシートを開く
        sheets_key = os.getenv('SHEETS_KEY')
        spreadsheet = client.open_by_key(sheets_key)
        worksheet = spreadsheet.sheet1

        # 書き込むデータの生成
        item = []
        for header in HEADERS:
            item.append(dictItems.get(header, ""))

        # データの書き込み
        worksheet.append_row(item)

        return '200'
    
    except Exception as e:
        # 何かしらのエラーが出た
        return f"エラーが発生しました: {e}"

# スプシに書き込み
def set_sheets_list(addItem: list[str]):
    # 認証情報の設定
    encoded_str = os.getenv('SHEETS_JSON_STR')
    dict_data = decodeJson.decode_json(encoded_str=encoded_str)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(dict_data, scopes=scope)
    client = gspread.authorize(creds)

    # Google Sheetsの特定のシートを開く
    sheets_key = os.getenv('SHEETS_KEY')
    spreadsheet = client.open_by_key(sheets_key)
    worksheet = spreadsheet.sheet1

    # データの書き込み
    a = worksheet.append_row(addItem)

if __name__ == '__main__':
    sample_item = ["会社名テストだよ", "部署名テストだよ", "氏名テストだよ", "会社住所テストだよ", "電話番号テストだよ", "e-mailアドレステストだよ"]
    set_sheets_list(sample_item)

