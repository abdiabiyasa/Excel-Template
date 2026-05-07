# excel_d.py

import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO


# =========================
# DATA CLEANING
# =========================

def filter_data(df):
    return df[df['ClaimStatus'] == 'R']


def keep_last_duplicate(df):

    # cek apakah BenefitName ada
    subset_cols = ['ClaimNo']

    if 'BenefitName' in df.columns:
        subset_cols.append('BenefitName')

    duplicate_claims = df[
        df.duplicated(subset=subset_cols, keep=False)
    ]

    if not duplicate_claims.empty:
        st.write("Duplicated Claim values:")
        st.write(
            duplicate_claims[subset_cols].drop_duplicates()
        )

    return df.drop_duplicates(
        subset=subset_cols,
        keep='last'
    )


# =========================
# FILTER BENEFIT
# =========================

def filter_benefit_data(df_benefit, df_sc):

    df_benefit = df_benefit.copy()
    df_benefit.columns = df_benefit.columns.str.strip()

    # filter status claim
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

    # filter claim no
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

    # convert dates
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

        "Room Option": (
            new_df["RoomOption"]
            .fillna('')
            .astype(str)
            .str.upper()
            .str.replace(r"\s+", "", regex=True)
        ),

        "Area": new_df["Area"],
        "Plan": new_df["PPlan"],
        "PrePost": new_df["isPrePost2"],

        "Primary Diagnosis":
            new_df["PrimaryDiagnosis"].astype(str).str.upper(),

        "Secondary Diagnosis":
            new_df["SecondaryDiagnosis"]
            .fillna('')
            .astype(str)
            .str.upper(),

        "Treatment Place":
            new_df["TreatmentPlace"]
            .astype(str)
            .str.upper(),

        "Treatment Start": new_df["TreatmentStart"],
        "Treatment Finish": new_df["TreatmentFinish"],

        "Treatment Year":
            new_df["TreatmentStart"].dt.year,

        "Treatment Month":
            new_df["TreatmentStart"].dt.month,

        "Settled Date": new_df["Date"],

        "Settled Year":
            new_df["Date"].dt.year,

        "Settled Month":
            new_df["Date"].dt.month,

        "Length of Stay": new_df["LOS"],

        "Sum of Billed": new_df["Billed"],
        "Sum of Accepted": new_df["Accepted"],
        "Sum of Excess Coy": new_df["ExcessCoy"],
        "Sum of Excess Emp": new_df["ExcessEmp"],
        "Sum of Excess Total": new_df["ExcessTotal"],
        "Sum of Unpaid": new_df["Unpaid"],
    })

    # range billed
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

    df.columns = df.columns.str.strip()

    # trim object columns
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

    # convert dates
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

    # clean room option
    if "Room Option" in df.columns:

        df["Room Option"] = (
            df["Room Option"]
            .fillna('')
            .astype(str)
            .str.replace(r"\s+", "", regex=True)
        )

    # clean treatment room class
    if "Treatment Room Class" in df.columns:

        df["Treatment Room Class"] = (
            df["Treatment Room Class"]
            .fillna('')
        )

    return df.drop(
        columns=["Status_Claim", "BAmount"],
        errors='ignore'
    )
