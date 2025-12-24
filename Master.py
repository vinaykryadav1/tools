import re
import os
import sys
import math
import PyPDF2
import shutil
import zipfile
import inflect
import textwrap
import calendar
import numpy as np
import pandas as pd
from sympy import isprime
from num2words import num2words
from PyPDF2 import PdfMerger

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def excel_merge(files):
    dfs = [pd.read_excel(f) for f in files]
    final_df = pd.concat(dfs, ignore_index=True)

    output_path = "output/merged_excel.xlsx"
    final_df.to_excel(output_path, index=False)

    return output_path


def pdf_merge(files):
    merger = PdfMerger()

    for pdf in files:
        merger.append(pdf)

    output_path = "output/merged_pdf.pdf"
    merger.write(output_path)
    merger.close()

    return output_path

# PDF_split

def pdf_split(file, max_pages):
    reader = PyPDF2.PdfReader(file)
    total_pages = len(reader.pages)

    base_name = file.name.replace(".pdf", "")
    output_files = []

    part = 1
    for start in range(0, total_pages, max_pages):
        writer = PyPDF2.PdfWriter()
        end = min(start + max_pages, total_pages)

        for page in range(start, end):
            writer.add_page(reader.pages[page])

        output_path = f"{OUTPUT_DIR}/{base_name}_part_{part}.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)

        output_files.append(output_path)
        part += 1

    # ZIP all split PDFs
    zip_path = f"{OUTPUT_DIR}/{base_name}_split.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in output_files:
            zipf.write(f, arcname=os.path.basename(f))

    return zip_path

#Excel Split

def excel_split(file, mode, rows_per_file=None, column_name=None, same_file=True):
    df = pd.read_excel(file, dtype="object")
    base_name = file.name.replace(".xlsx", "")

    output_files = []

    # ---------- SPLIT BY ROW ----------
    if mode == "row":
        n_files = math.ceil(len(df) / rows_per_file)

        for i in range(n_files):
            start = i * rows_per_file
            end = start + rows_per_file

            out = f"{OUTPUT_DIR}/{base_name}_part_{i+1}.xlsx"
            df.iloc[start:end].to_excel(out, index=False)
            output_files.append(out)

    # ---------- SPLIT BY COLUMN ----------
    elif mode == "column":
        groups = df.groupby(column_name)

        if same_file:
            out = f"{OUTPUT_DIR}/{base_name}_split.xlsx"
            writer = pd.ExcelWriter(out, engine="xlsxwriter")

            for name, group in groups:
                sheet = re.sub("[^a-zA-Z0-9& _-]", "", str(name))[:31]
                group.to_excel(writer, sheet_name=sheet, index=False)

            writer.close()
            return out

        else:
            for name, group in groups:
                clean = re.sub("[^a-zA-Z0-9& _-]", "", str(name))
                out = f"{OUTPUT_DIR}/{clean}.xlsx"
                group.to_excel(out, index=False)
                output_files.append(out)

    # ---------- ZIP MULTIPLE FILES ----------
    zip_path = f"{OUTPUT_DIR}/{base_name}_split.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in output_files:
            zipf.write(f, arcname=os.path.basename(f))

    return zip_path