import time
import pandas as pd
import streamlit as st
# from gsheet import save_login
from Master import excel_merge, pdf_merge, pdf_split,excel_split

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Automation Tool", layout="centered")

# ---------------- LOGIN ----------------
# ---------- SESSION ----------
if "login" not in st.session_state:
    st.session_state.login = False

# ---------- LOGIN UI ----------
if not st.session_state.login:

    st.title("🔐 Login")

    name = st.text_input("Enter Your Name", key="login_name")
    email = st.text_input("Enter Your Email", key="login_email")

    if st.button("Login"):
        if name and email:
            st.session_state.login = True
            st.session_state.user_name = name
            st.session_state.user_email = email

            # save_login(name, email)   # save to Google Sheet

            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Please enter name and email")

# ---------- MAIN APP ----------
else:
    st.sidebar.success(f"Welcome {st.session_state.user_name}")

    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()

    st.title("📂 Data Automation Tool")

    files = None
    pdf_file = None
    output_zip = None

    # 1️⃣ Script Selection
    script = st.selectbox(
        "Select Script",
        ["Excel Merge", "PDF Merge","PDF Split","Excel Split"]
    )

    # 2️⃣ File Upload
    if script == "Excel Merge":
        files = st.file_uploader(
            "Upload Excel files",
            type=["xlsx"],
            accept_multiple_files=True
        )

    elif script == "PDF Merge":
        files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )
        
    elif script == "PDF Split":
        pdf_file = st.file_uploader(
        "Upload PDF File",
        type=["pdf"],
        key="pdf_split_file"
        )
        
        max_pages = st.number_input(
        "Max pages per split PDF",
        min_value=1,
        step=1,
        key="pdf_split_max_pages"
        )       
    
    elif script == "Excel Split":
        excel_file = st.file_uploader(
        "Upload Excel File",
        type=["xlsx"],
        key="excel_split_file"
        
        )
        split_type = st.radio(
        "Split Type",
        ["By Row", "By Column"],
        key="excel_split_type"
        )
        if split_type == "By Row":
            rows_per_file = st.number_input(
            "Rows per Excel file",
            min_value=1,
            step=1,
            key="rows_per_file"
        )

        else:
            if excel_file:
                df = pd.read_excel(excel_file)
                column_name = st.selectbox(
                    "Select Column",
                    df.columns,
                    key="split_column"
                )

            same_file = st.radio(
                "Output Type",
                ["Same Excel (Multiple Sheets)", "Separate Excel Files"],
                key="output_type"
            )

     
        # 3️⃣ Run Button
    if st.button("▶ Run"):

        # -------- PDF SPLIT --------
        if script == "PDF Split":
            if not pdf_file:
                st.error("Please upload a PDF file")
            else:
                progress = st.progress(0)
                status = st.empty()

                for i in range(100):
                    progress.progress(i + 1)
                    status.text("Splitting PDF...")
                    time.sleep(0.01)

                output_zip = pdf_split(pdf_file, max_pages)

                status.success("✅ PDF Split Completed")

                with open(output_zip, "rb") as f:
                    st.download_button(
                        label="⬇ Download Split PDFs (ZIP)",
                        data=f,
                        file_name=output_zip.split("/")[-1]
                    )

        # -------- EXCEL MERGE --------
        elif script == "Excel Merge":
            if not files:
                st.error("Please upload Excel files")
            else:
                output = excel_merge(files)
                with open(output, "rb") as f:
                    st.download_button(
                        label="⬇ Download Excel",
                        data=f,
                        file_name="merged_excel.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        # -------- PDF MERGE --------
        elif script == "PDF Merge":
            if not files:
                st.error("Please upload PDF files")
            else:
                output = pdf_merge(files)
                with open(output, "rb") as f:
                    st.download_button(
                        label="⬇ Download PDF",
                        data=f,
                        file_name="merged_pdf.pdf",
                        mime="application/pdf"
                    )

                    # 4️⃣ Download Button
                with open(output_zip, "rb") as f:
                    st.download_button(
                        label="⬇ Download Output",
                        data=f,
                        file_name=output_zip.split("/")[-1]
                    )
        elif script == "PDF Split":
            pdf_file = st.file_uploader(
            "Upload PDF File",
            type=["pdf"],
            key="pdf_split_file"
        )

        elif script == "Excel Split":
            if not excel_file:
                st.error("Please upload Excel file")
            else:
                with st.spinner("Splitting Excel..."):
                    if split_type == "By Row":
                        output = excel_split(
                            excel_file,
                            mode="row",
                            rows_per_file=rows_per_file
                        )
                        st.success("✅ Excel Split Completed")
                        st.download_button(
                            label="⬇ Download Excel",
                            data=output,
                            file_name="excel_split_by_row.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        same_excel = same_file.startswith("Same")
                        
                        output = excel_split(
                            excel_file,
                            mode="column",
                            column_name=column_name,
                            same_file=same_excel
                        )

                        st.success("✅ Excel Split Completed")
                        if same_excel:
                    # ✅ Single Excel (Multiple Sheets)
                            st.download_button(
                            label="⬇ Download Excel",
                            data=output,
                            file_name="excel_split_by_column.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                    # ✅ Multiple Excel → ZIP
                            st.download_button(
                                label="⬇ Download ZIP",
                                data=output,
                                file_name="excel_split_files.zip",
                                mime="application/zip"
                            )
                with open(output, "rb") as f:
                    st.download_button(
                        label="⬇ Download Output",
                        data=f,
                        file_name="excel_split_output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
