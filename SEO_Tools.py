import os
import pandas as pd
import requests
import zipfile
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def run_seo_downloader(
    excel_file,
    loan_id_col,
    url_col,
    folder_columns,
    output_folder="SEO_Downloads",
    max_workers=20
):
    os.makedirs(output_folder, exist_ok=True)

    # -------- READ FILE (CSV / XLSX) ----------
    if excel_file.name.endswith(".csv"):
        df = pd.read_csv(excel_file)
    else:
        df = pd.read_excel(excel_file)

    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    downloaded = []
    failed_rows = []
    lock = Lock()

    def sanitize(text):
        return str(text).replace("/", "_").replace("\\", "_")

    def worker(row):
        try:
            loan_id = sanitize(row[loan_id_col])
            url = row[url_col]

            if not isinstance(url, str) or not url.startswith("http"):
                failed_rows.append(row)
                return

            folder = output_folder
            for col in folder_columns:
                folder = os.path.join(folder, sanitize(row[col]))

            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, f"{loan_id}.pdf")

            r = session.get(url, stream=True, timeout=20)
            if r.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(4096):
                        f.write(chunk)
                downloaded.append(file_path)
            else:
                failed_rows.append(row)

        except Exception:
            failed_rows.append(row)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _, row in df.iterrows():
            executor.submit(worker, row)

    # ---------- CREATE ZIP ----------
    zip_path = f"{output_folder}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for f in files:
                full = os.path.join(root, f)
                zipf.write(full, arcname=os.path.relpath(full, output_folder))

    # ---------- FAILED FILE EXPORT ----------
    failed_excel = None
    if failed_rows:
        failed_df = pd.DataFrame(failed_rows)
        failed_excel = f"{output_folder}_FAILED.xlsx"
        failed_df.to_excel(failed_excel, index=False)

    return {
        "zip_path": zip_path,
        "failed_excel": failed_excel,
        "downloaded": len(downloaded),
        "failed_count": len(failed_rows)
    }
