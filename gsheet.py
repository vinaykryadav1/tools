import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def save_login(name, email):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "Credentials.json",
        scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("login_logs").sheet1

    sheet.append_row([
        name,
        email,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
