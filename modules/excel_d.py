# excel_d.py

import pandas as pd
import streamlit as st
from io import BytesIO


# =====================================================
# FILTER DATA
# =====================================================

def filter_data(df):
    if 'ClaimStatus' not in df.columns:
        st.error("Column 'ClaimStatus' tidak ditemukan.")
        return df

    return df[df['ClaimStatus'] == 'R']


# =====================================================
# REMOVE DUPLICATE
# =====================================================

def keep_last_duplicate(df):

    if 'ClaimNo' not in df.columns:
        st.error("Column 'ClaimNo' tidak ditemukan.")
        return df

    duplicate_claims = df[
        df.duplicated(subset='ClaimNo', keep=False)
    ]

    if not duplicate_claims.empty:
        st.write("Duplicated ClaimNo values:")
        st.write(
            duplicate_claims[['ClaimNo']].drop_duplicates()
        )

    # Jika BenefitName ada
    if 'BenefitName' in df.columns:
        return df.drop_duplicates(
            subset=['ClaimNo', 'BenefitName'],
            keep='last'
        )

    # Jika BenefitName tidak ada
    return df.drop_duplicates(
        subset=['ClaimNo'],
        keep='last'
    )


# =====================================================
# FILTER BENEFIT
# =====================================================

def filter_benefit_data(df_benefit, df_sc):

    df_benefit = df_benefit.copy()
    df_benefit.columns = df_benefit.columns.str.strip()

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
            "Column 'Status Claim' tidak ditemukan."
        )

    # Filter ClaimNo
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


# =====================================================
# TEMPLATE SC
# =====================================================

def template_sc(df):

    new_df = filter_data(df)
    new_df = keep_last_duplicate(new_df)

    # Convert date
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

        "No":
            range(1, len(new_df) + 1),

        "Policy No":
            new_df.get("PolicyNo"),

        "Client Name":
            new_df.get("ClientName"),

        "Claim No":
            new_df.get("ClaimNo"),

        "Member No":
            new_df.get("MemberNo"),

        "Emp ID":
            new_df.get("EmpID"),

        "Emp Name":
            new_df.get("EmpName"),

        "Patient Name":
            new_df.get("PatientName"),

        "Age":
            new_df.get("Age"),

        "Membership":
            new_df.get("Membership"),

        "Product Type":
            new_df.get("ProductType"),

        "Claim Type":
            new_df.get("ClaimType"),

        "Room Option":
            new_df.get("RoomOption", "")
            .fillna('')
            .astype(str)
            .str.upper()
            .str.replace(r"\s+", "", regex=True),

        "Area":
            new_df.get("Area"),

        "Plan":
            new_df.get("PPlan"),

        "PrePost":
            new_df.get("isPrePost2"),

        "Primary Diagnosis":
            new_df.get("PrimaryDiagnosis", "")
            .fillna('')
            .astype(str)
            .str.upper(),

        "Secondary Diagnosis":
            new_df.get("SecondaryDiagnosis", "")
            .fillna('')
            .astype(str)
            .str.upper(),

        "Treatment Place":
            new_df.get("TreatmentPlace", "")
            .fillna('')
            .astype(str)
            .str.upper(),

        "Treatment Start":
            new_df.get("TreatmentStart"),

        "Treatment Finish":
            new_df.get("TreatmentFinish"),

        "Treatment Year":
            new_df.get("TreatmentStart").dt.year,

        "Treatment Month":
            new_df.get("TreatmentStart").dt.month,

        "Settled Date":
            new_df.get("Date"),

        "Settled Year":
            new_df.get("Date").dt.year,

        "Settled Month":
            new_df.get("Date").dt.month,

        "Length of Stay":
            new_df.get("LOS"),

        "Sum of Billed":
            new_df.get("Billed"),

        "Sum of Accepted":
            new_df.get("Accepted"),

        "Sum of Excess Coy":
            new_df.get("ExcessCoy"),

        "Sum of Excess Emp":
            new_df.get("ExcessEmp"),

        "Sum of Excess Total":
            new_df.get("ExcessTotal"),

        "Sum of Unpaid":
            new_df.get("Unpaid"),
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


# =====================================================
# TEMPLATE BENEFIT
# =====================================================

def template_benefit(df):

    df.columns = df.columns.str.strip()

    # Trim text
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

    # Convert date
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


# =====================================================
# SAVE TO EXCEL
# =====================================================

def save_to_excel_d(
    df_sc,
    df_benefit,
    claim_ratio_df,
    filename
):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine='xlsxwriter'
    ) as writer:

        # Save sheets
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

        sheets = {
            'SC': df_sc,
            'Benefit': df_benefit,
            'Summary': claim_ratio_df
        }

        for sheet_name, df in sheets.items():

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

                            worksheet.write_number(
                                row_num,
                                col_num,
                                float(value),
                                number_format
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
                        .apply(len)
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


# =====================================================
# RUN MAIN
# =====================================================

def run_d(
    uploaded_sc,
    uploaded_benefit,
    uploaded_cr,
    policy_filter_list
):

    # Read SC
    df_sc_raw = pd.read_csv(uploaded_sc)

    # Read Benefit
    df_benefit_raw = pd.read_csv(uploaded_benefit)

    # Read Claim Ratio
    try:

        df_cr_raw = pd.read_excel(uploaded_cr)

    except Exception as e:

        st.error(
            f"Error reading Claim Ratio file: {e}"
        )

        df_cr_raw = pd.DataFrame()

    # Clean SC
    df_sc_clean = template_sc(df_sc_raw)

    # Filter policy
    if policy_filter_list:

        df_sc_clean["Policy No"] = (
            df_sc_clean["Policy No"]
            .astype(str)
            .str.strip()
        )

        df_sc_clean = df_sc_clean[
            df_sc_clean["Policy No"].isin(
                [str(p).strip() for p in policy_filter_list]
            )
        ]

    # Benefit
    df_benefit_filtered = filter_benefit_data(
        df_benefit_raw,
        df_sc_clean
    )

    df_benefit_clean = template_benefit(
        df_benefit_filtered
    )

    # Claim Ratio
    if not df_cr_raw.empty:

        df_cr_filtered = df_cr_raw.copy()

        df_cr_filtered.columns = (
            df_cr_filtered.columns.str.strip()
        )

    else:

        df_cr_filtered = pd.DataFrame()

    return (
        df_sc_clean,
        df_benefit_clean,
        df_cr_filtered
    )
