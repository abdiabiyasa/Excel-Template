# excel_d.py 

import pandas as pd 
import numpy as np 
import streamlit as st 
from io import BytesIO

# =========================
# DATA CLEANING FUNCTION
# =========================

def filter_data(df):

    if 'ClaimStatus' not in df.columns:
        st.error("Column 'ClaimStatus' not found")
        return df

    return df[df['ClaimStatus'] == 'R']


def keep_last_duplicate(df):

    duplicate_claims = df[
        df.duplicated(subset='ClaimNo', keep=False)
    ]

    if not duplicate_claims.empty:

        st.write("Duplicated ClaimNo values:")
        st.write(
            duplicate_claims[['ClaimNo']]
            .drop_duplicates()
        )

    # jika ada BenefitName
    if 'BenefitName' in df.columns:

        return df.drop_duplicates(
            subset=['ClaimNo', 'BenefitName'],
            keep='last'
        )

    # jika tidak ada
    return df.drop_duplicates(
        subset=['ClaimNo'],
        keep='last'
    )


def filter_benefit_data(df_benefit, df_sc):

    df_benefit = df_benefit.copy()
    df_benefit.columns = (
        df_benefit.columns.str.strip()
    )

    # Filter status claim
    if 'Status_Claim' in df_benefit.columns:

        df_benefit = df_benefit[
            df_benefit['Status_Claim'] == 'R'
        ]

    elif 'Status Claim' in df_benefit.columns:

        df_benefit = df_benefit[
            df_benefit['Status Claim'] == 'R'
        ]

    else:

        st.warning(
            "Column 'Status Claim' not found."
        )

    # Filter claim no
    if "ClaimNo" in df_benefit.columns:

        df_benefit = df_benefit[
            df_benefit["ClaimNo"].isin(
                df_sc["Claim No"]
            )
        ]

    elif "Claim No" in df_benefit.columns:

        df_benefit = df_benefit[
            df_benefit["Claim No"].isin(
                df_sc["Claim No"]
            )
        ]

    return df_benefit


# =========================
# TEMPLATE SC
# =========================

def template_sc(df):

    new_df = filter_data(df)
    new_df = keep_last_duplicate(new_df)

    # pastikan kolom ada
    required_cols = [

        "PolicyNo",
        "ClientName",
        "ClaimNo",
        "MemberNo",
        "EmpID",
        "EmpName",
        "PatientName",
        "Age",
        "Membership",
        "ProductType",
        "ClaimType",
        "RoomOption",
        "Area",
        "PPlan",
        "isPrePost2",
        "PrimaryDiagnosis",
        "SecondaryDiagnosis",
        "TreatmentPlace",
        "TreatmentStart",
        "TreatmentFinish",
        "Date",
        "LOS",
        "Billed",
        "Accepted",
        "ExcessCoy",
        "ExcessEmp",
        "ExcessTotal",
        "Unpaid"

    ]

    for col in required_cols:

        if col not in new_df.columns:

            if col in [
                "Billed",
                "Accepted",
                "ExcessCoy",
                "ExcessEmp",
                "ExcessTotal",
                "Unpaid",
                "LOS",
                "Age"
            ]:

                new_df[col] = 0

            else:

                new_df[col] = ""

    # convert date
    date_columns = [
        "TreatmentStart",
        "TreatmentFinish",
        "Date"
    ]

    for col in date_columns:

        if col in new_df.columns:

            new_df[col] = pd.to_datetime(
                new_df[col],
                errors='coerce'
            )

    df_transformed = pd.DataFrame({

        "No": range(1, len(new_df) + 1),

        "Policy No": new_df["PolicyNo"],
        "Client Name": new_df["ClientName"],
        "Claim No": new_df["ClaimNo"],
        "Member No": new_df["MemberNo"],
        "Emp ID": new_df["EmpID"],
        "Emp Name": new_df["EmpName"],
        "Patient Name": new_df["PatientName"],
        "Age": new_df["Age"],
        "Membership": new_df["Membership"],
        "Product Type": new_df["ProductType"],
        "Claim Type": new_df["ClaimType"],

        "Room Option":

            new_df["RoomOption"]
            .fillna('')
            .astype(str)
            .str.upper()
            .str.replace(r"\s+", "", regex=True),

        "Area": new_df["Area"],
        "Plan": new_df["PPlan"],
        "PrePost": new_df["isPrePost2"],

        "Primary Diagnosis":

            new_df["PrimaryDiagnosis"]
            .astype(str)
            .str.upper(),

        "Secondary Diagnosis":

            new_df["SecondaryDiagnosis"]
            .fillna('')
            .astype(str)
            .str.upper(),

        "Treatment Place":

            new_df["TreatmentPlace"]
            .astype(str)
            .str.upper(),

        "Treatment Start":
            new_df["TreatmentStart"],

        "Treatment Finish":
            new_df["TreatmentFinish"],

        "Treatment Year":
            new_df["TreatmentStart"].dt.year,

        "Treatment Month":
            new_df["TreatmentStart"].dt.month,

        "Settled Date":
            new_df["Date"],

        "Settled Year":
            new_df["Date"].dt.year,

        "Settled Month":
            new_df["Date"].dt.month,

        "Length of Stay":
            new_df["LOS"],

        "Sum of Billed":
            pd.to_numeric(
                new_df["Billed"],
                errors='coerce'
            ).fillna(0),

        "Sum of Accepted":
            pd.to_numeric(
                new_df["Accepted"],
                errors='coerce'
            ).fillna(0),

        "Sum of Excess Coy":
            pd.to_numeric(
                new_df["ExcessCoy"],
                errors='coerce'
            ).fillna(0),

        "Sum of Excess Emp":
            pd.to_numeric(
                new_df["ExcessEmp"],
                errors='coerce'
            ).fillna(0),

        "Sum of Excess Total":
            pd.to_numeric(
                new_df["ExcessTotal"],
                errors='coerce'
            ).fillna(0),

        "Sum of Unpaid":
            pd.to_numeric(
                new_df["Unpaid"],
                errors='coerce'
            ).fillna(0),
    })

    # Range billed
    bins = [
        0,
        5000000,
        10000000,
        25000000,
        50000000,
        100000000,
        float('inf')
    ]

    labels = [
        '<5 Mio',
        '5 - 10 Mio',
        '10 - 25 Mio',
        '25 - 50 Mio',
        '50 - 100 Mio',
        '>100 Mio'
    ]

    df_transformed['Range Billed'] = pd.cut(
        df_transformed['Sum of Billed'],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    return df_transformed


# =========================
# TEMPLATE BENEFIT
# =========================

def template_benefit(df):

    df = df.copy()

    df.columns = df.columns.str.strip()

    for col in df.columns:

        if df[col].dtype == "object":

            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
            )

    rename_mapping = {

        'ClientName': 'Client Name',
        'PolicyNo': 'Policy No',
        'ClaimNo': 'Claim No',
        'MemberNo': 'Member No',
        'PatientName': 'Patient Name',
        'EmpID': 'Emp ID',
        'EmpName': 'Emp Name',
        'ClaimType': 'Claim Type',
        'TreatmentPlace': 'Treatment Place',
        'RoomOption': 'Room Option',
        'TreatmentRoomClass': 'Treatment Room Class',
        'TreatmentStart': 'Treatment Start',
        'TreatmentFinish': 'Treatment Finish',
        'ProductType': 'Product Type',
        'BenefitName': 'Benefit Name',
        'PaymentDate': 'Payment Date',
        'ExcessTotal': 'Excess Total',
        'ExcessCoy': 'Excess Coy',
        'ExcessEmp': 'Excess Emp'
    }

    df = df.rename(columns=rename_mapping)

    date_cols = [
        "Treatment Start",
        "Treatment Finish",
        "Payment Date"
    ]

    for col in date_cols:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors='coerce'
            )

    return df.drop(
        columns=["Status_Claim", "BAmount"],
        errors='ignore'
    )


# =========================
# SAVE TO EXCEL
# =========================

def save_to_excel_d(
    df_sc,
    df_benefit,
    claim_ratio_df,
    filename: str
):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine='xlsxwriter'
    ) as writer:

        df_sc.to_excel(
            writer,
            sheet_name='SC',
            index=False
        )

        df_benefit.to_excel(
            writer,
            sheet_name='Benefit',
            index=False
        )

        claim_ratio_df.to_excel(
            writer,
            sheet_name='Summary',
            index=False
        )

        workbook = writer.book

        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center'
        })

        border_format = workbook.add_format({
            'border': 1
        })

        number_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0'
        })

        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        })

        for sheet_name, df in {

            'SC': df_sc,
            'Benefit': df_benefit,
            'Summary': claim_ratio_df

        }.items():

            worksheet = writer.sheets[sheet_name]

            # Header
            for col_num, value in enumerate(df.columns):

                worksheet.write(
                    0,
                    col_num,
                    value,
                    header_format
                )

            # Body
            for row_num, row in enumerate(
                df.itertuples(index=False),
                start=1
            ):

                for col_num, value in enumerate(row):

                    col_name = df.columns[col_num]

                    # Date
                    if pd.api.types.is_datetime64_any_dtype(
                        df[col_name]
                    ):

                        if pd.notna(value):

                            worksheet.write_datetime(
                                row_num,
                                col_num,
                                pd.to_datetime(value),
                                date_format
                            )

                        else:

                            worksheet.write_blank(
                                row_num,
                                col_num,
                                None,
                                border_format
                            )

                    # Numeric
                    elif pd.api.types.is_numeric_dtype(
                        df[col_name]
                    ):

                        if pd.isna(value):

                            worksheet.write_blank(
                                row_num,
                                col_num,
                                None,
                                number_format
                            )

                        else:

                            try:

                                worksheet.write_number(
                                    row_num,
                                    col_num,
                                    float(value),
                                    number_format
                                )

                            except Exception:

                                worksheet.write(
                                    row_num,
                                    col_num,
                                    str(value),
                                    border_format
                                )

                    # Text
                    else:

                        worksheet.write(
                            row_num,
                            col_num,
                            str(value),
                            border_format
                        )

            # Autofit
            for i, col in enumerate(df.columns):

                try:

                    max_len = max(

                        df[col]
                        .astype(str)
                        .apply(lambda x: len(str(x)))
                        .max(),

                        len(str(col))
                    )

                except Exception:

                    max_len = len(str(col))

                worksheet.set_column(
                    i,
                    i,
                    max_len + 5
                )

    output.seek(0)

    return output.getvalue(), filename
