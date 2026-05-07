# excel_d.py

import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO


# =========================================================
# HELPER
# =========================================================

def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    return df


def safe_numeric(series):
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    ).fillna(0)


def safe_datetime(series):
    return pd.to_datetime(series, errors="coerce")


# =========================================================
# FILTER DATA
# =========================================================

def filter_data(df):
    return df[df["ClaimStatus"] == "R"]


def keep_last_duplicate(df):

    duplicate_claims = df[df.duplicated(subset="ClaimNo", keep=False)]

    if not duplicate_claims.empty:
        st.write("Duplicated ClaimNo values:")
        st.write(
            duplicate_claims[["ClaimNo"]].drop_duplicates()
        )

    return df.drop_duplicates(
        subset=["ClaimNo", "BenefitName"],
        keep="last"
    )


# =========================================================
# BENEFIT FILTER
# =========================================================

def filter_benefit_data(df_benefit, df_sc):

    df_benefit = normalize_columns(df_benefit)

    # filter status claim
    if "Status_Claim" in df_benefit.columns:
        df_benefit = df_benefit[
            df_benefit["Status_Claim"] == "R"
        ]

    elif "Status Claim" in df_benefit.columns:
        df_benefit = df_benefit[
            df_benefit["Status Claim"] == "R"
        ]

    else:
        st.warning("Column Status Claim not found")

    # filter claim no
    if "ClaimNo" in df_benefit.columns:
        df_benefit = df_benefit[
            df_benefit["ClaimNo"].isin(df_sc["Claim No"])
        ]

    elif "Claim No" in df_benefit.columns:
        df_benefit = df_benefit[
            df_benefit["Claim No"].isin(df_sc["Claim No"])
        ]

    return df_benefit


# =========================================================
# TEMPLATE SC
# =========================================================

def template_sc(df):

    df = filter_data(df)
    df = keep_last_duplicate(df)

    # datetime
    date_cols = [
        "TreatmentStart",
        "TreatmentFinish",
        "Date"
    ]

    for col in date_cols:
        df[col] = safe_datetime(df[col])

    transformed = pd.DataFrame({

        "No":
            range(1, len(df) + 1),

        "Policy No":
            df["PolicyNo"],

        "Client Name":
            df["ClientName"],

        "Claim No":
            df["ClaimNo"],

        "Member No":
            df["MemberNo"],

        "Emp ID":
            df["EmpID"],

        "Emp Name":
            df["EmpName"],

        "Patient Name":
            df["PatientName"],

        "Age":
            df["Age"],

        "Membership":
            df["Membership"],

        "Product Type":
            df["ProductType"],

        "Claim Type":
            df["ClaimType"],

        "Room Option":
            df["RoomOption"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.replace(r"\s+", "", regex=True),

        "Area":
            df["Area"],

        "Plan":
            df["PPlan"],

        "PrePost":
            df["isPrePost2"],

        "Primary Diagnosis":
            df["PrimaryDiagnosis"]
            .fillna("")
            .str.upper(),

        "Secondary Diagnosis":
            df["SecondaryDiagnosis"]
            .fillna("")
            .str.upper(),

        "Treatment Place":
            df["TreatmentPlace"]
            .fillna("")
            .str.upper(),

        "Treatment Start":
            df["TreatmentStart"],

        "Treatment Finish":
            df["TreatmentFinish"],

        "Treatment Year":
            df["TreatmentStart"].dt.year,

        "Treatment Month":
            df["TreatmentStart"].dt.month,

        "Settled Date":
            df["Date"],

        "Settled Year":
            df["Date"].dt.year,

        "Settled Month":
            df["Date"].dt.month,

        "Length of Stay":
            df["LOS"],

        "Sum of Billed":
            safe_numeric(df["Billed"]),

        "Sum of Accepted":
            safe_numeric(df["Accepted"]),

        "Sum of Excess Coy":
            safe_numeric(df["ExcessCoy"]),

        "Sum of Excess Emp":
            safe_numeric(df["ExcessEmp"]),

        "Sum of Excess Total":
            safe_numeric(df["ExcessTotal"]),

        "Sum of Unpaid":
            safe_numeric(df["Unpaid"]),
    })

    # range billed
    bins = [
        0,
        5_000_000,
        10_000_000,
        25_000_000,
        50_000_000,
        100_000_000,
        np.inf
    ]

    labels = [
        "<5 Mio",
        "5 - 10 Mio",
        "10 - 25 Mio",
        "25 - 50 Mio",
        "50 - 100 Mio",
        ">100 Mio"
    ]

    transformed["Range Billed"] = pd.cut(
        transformed["Sum of Billed"],
        bins=bins,
        labels=labels,
        right=False
    )

    return transformed


# =========================================================
# TEMPLATE BENEFIT
# =========================================================

def template_benefit(df):

    df = normalize_columns(df)

    # trim object
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    rename_mapping = {

        "ClientName": "Client Name",
        "PolicyNo": "Policy No",
        "ClaimNo": "Claim No",
        "MemberNo": "Member No",
        "PatientName": "Patient Name",
        "EmpID": "Emp ID",
        "EmpName": "Emp Name",
        "ClaimType": "Claim Type",
        "TreatmentPlace": "Treatment Place",
        "RoomOption": "Room Option",
        "TreatmentRoomClass": "Treatment Room Class",
        "TreatmentStart": "Treatment Start",
        "TreatmentFinish": "Treatment Finish",
        "ProductType": "Product Type",
        "BenefitName": "Benefit Name",
        "PaymentDate": "Payment Date",
        "ExcessTotal": "Excess Total",
        "ExcessCoy": "Excess Coy",
        "ExcessEmp": "Excess Emp"

    }

    df = df.rename(columns=rename_mapping)

    # datetime
    date_cols = [
        "Treatment Start",
        "Treatment Finish",
        "Payment Date"
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = safe_datetime(df[col])

    # room option
    if "Room Option" in df.columns:
        df["Room Option"] = (
            df["Room Option"]
            .fillna("")
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
        )

    return df.drop(
        columns=["Status_Claim", "BAmount"],
        errors="ignore"
    )


# =========================================================
# SAVE TO EXCEL
# =========================================================

def save_to_excel_d(
    df_sc,
    df_benefit,
    claim_ratio_df,
    filename
):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # =================================================
        # FORMAT
        # =================================================

        header_fmt = workbook.add_format({
            "bold": True,
            "border": 1,
            "align": "center"
        })

        border_fmt = workbook.add_format({
            "border": 1
        })

        num_fmt = workbook.add_format({
            "border": 1,
            "num_format": "#,##0"
        })

        date_fmt = workbook.add_format({
            "border": 1,
            "num_format": "dd/mm/yyyy"
        })

        # =================================================
        # SUMMARY
        # =================================================

        summary = workbook.add_worksheet("Summary")
        writer.sheets["Summary"] = summary

        metrics = [
            ("Total Claims", len(df_sc)),
            ("Total Billed", df_sc["Sum of Billed"].sum()),
            ("Total Accepted", df_sc["Sum of Accepted"].sum()),
            ("Total Excess", df_sc["Sum of Excess Total"].sum()),
            ("Total Unpaid", df_sc["Sum of Unpaid"].sum())
        ]

        for i, (label, value) in enumerate(metrics):

            summary.write(i, 0, label, border_fmt)
            summary.write(i, 1, value, num_fmt)

        # =================================================
        # SC SHEET
        # =================================================

        sc_sheet = workbook.add_worksheet("SC")
        writer.sheets["SC"] = sc_sheet

        # header
        for col_num, col_name in enumerate(df_sc.columns):
            sc_sheet.write(
                0,
                col_num,
                col_name,
                header_fmt
            )

        # body
        for row_num, row in enumerate(
            df_sc.to_dict("records"),
            start=1
        ):

            for col_num, (col_name, value) in enumerate(row.items()):

                if pd.isna(value) or value == 0:
                    sc_sheet.write_blank(
                        row_num,
                        col_num,
                        None,
                        border_fmt
                    )

                elif "Date" in col_name or "Treatment" in col_name:

                    try:
                        sc_sheet.write_datetime(
                            row_num,
                            col_num,
                            pd.to_datetime(value),
                            date_fmt
                        )
                    except:
                        sc_sheet.write(
                            row_num,
                            col_num,
                            value,
                            border_fmt
                        )

                elif isinstance(value, (int, float)):
                    sc_sheet.write_number(
                        row_num,
                        col_num,
                        value,
                        num_fmt
                    )

                else:
                    sc_sheet.write(
                        row_num,
                        col_num,
                        value,
                        border_fmt
                    )

        # =================================================
        # BENEFIT SHEET
        # =================================================

        benefit_sheet = workbook.add_worksheet("Benefit")
        writer.sheets["Benefit"] = benefit_sheet

        # header
        for col_num, col_name in enumerate(df_benefit.columns):
            benefit_sheet.write(
                0,
                col_num,
                col_name,
                header_fmt
            )

        # body
        for row_num, row in enumerate(
            df_benefit.to_dict("records"),
            start=1
        ):

            for col_num, (col_name, value) in enumerate(row.items()):

                if pd.isna(value) or value == 0:

                    benefit_sheet.write_blank(
                        row_num,
                        col_num,
                        None,
                        border_fmt
                    )

                elif "Date" in col_name or "Treatment" in col_name:

                    try:
                        benefit_sheet.write_datetime(
                            row_num,
                            col_num,
                            pd.to_datetime(value),
                            date_fmt
                        )

                    except:
                        benefit_sheet.write(
                            row_num,
                            col_num,
                            value,
                            border_fmt
                        )

                elif isinstance(value, (int, float)):

                    benefit_sheet.write_number(
                        row_num,
                        col_num,
                        value,
                        num_fmt
                    )

                else:

                    benefit_sheet.write(
                        row_num,
                        col_num,
                        value,
                        border_fmt
                    )

        # =================================================
        # AUTOFIT
        # =================================================

        def autofit(sheet, df):

            for idx, col in enumerate(df.columns):

                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                )

                sheet.set_column(
                    idx,
                    idx,
                    max_len + 5
                )

        autofit(sc_sheet, df_sc)
        autofit(benefit_sheet, df_benefit)

    output.seek(0)

    return output.getvalue(), filename


# =========================================================
# MAIN RUN
# =========================================================

def run_d(
    uploaded_sc,
    uploaded_benefit,
    uploaded_cr,
    policy_filter_list
):

    # read csv
    df_sc_raw = pd.read_csv(uploaded_sc)
    df_benefit_raw = pd.read_csv(uploaded_benefit)

    # read claim ratio
    try:
        df_cr_raw = pd.read_excel(uploaded_cr)

    except Exception as e:

        st.error(f"Error reading CR file: {e}")
        df_cr_raw = pd.DataFrame()

    # process sc
    df_sc_clean = template_sc(df_sc_raw)

    # filter policy
    if policy_filter_list:

        policy_filter_list = [
            str(x).strip()
            for x in policy_filter_list
        ]

        df_sc_clean["Policy No"] = (
            df_sc_clean["Policy No"]
            .astype(str)
            .str.strip()
        )

        df_sc_clean = df_sc_clean[
            df_sc_clean["Policy No"]
            .isin(policy_filter_list)
        ]

    # benefit
    df_benefit_filtered = filter_benefit_data(
        df_benefit_raw,
        df_sc_clean
    )

    df_benefit_clean = template_benefit(
        df_benefit_filtered
    )

    # claim ratio
    if not df_cr_raw.empty:

        cr_cols = [
            c for c in df_cr_raw.columns
            if c.strip().lower()
            in ["policy no", "policyno", "policy"]
        ]

        if cr_cols:

            policy_col = cr_cols[0]

            df_cr_raw[policy_col] = (
                df_cr_raw[policy_col]
                .astype(str)
                .str.strip()
            )

            if policy_filter_list:

                df_cr_filtered = df_cr_raw[
                    df_cr_raw[policy_col]
                    .isin(policy_filter_list)
                ]

            else:
                df_cr_filtered = df_cr_raw.copy()

        else:

            st.warning(
                "Policy No column not found in CR file"
            )

            df_cr_filtered = df_cr_raw.copy()

    else:
        df_cr_filtered = pd.DataFrame()

    return (
        df_sc_clean,
        df_benefit_clean,
        df_cr_filtered
    )
