import streamlit as st
import pandas as pd
from io import BytesIO

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Mission Review Dashboard",
    layout="wide"
)

st.title("📊 Mission Review Dashboard")

# ==================================
# UPLOAD FILE
# ==================================

uploaded_file = st.file_uploader(
    "Upload Excel / CSV",
    type=["xlsx", "csv"]
)

if uploaded_file:

    # ==================================
    # READ FILE
    # ==================================

    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success("File berhasil diupload")

    # ==================================
    # REMOVE DUPLICATE
    # ==================================

    duplicate_cols = [
        col for col in [
            'Name',
            'Task',
            'Activity',
            'Completion Date'
            'Submit'
        ]
        if col in df.columns
    ]

    if duplicate_cols:
        df = df.drop_duplicates(
            subset=duplicate_cols
        )
    else:
        df = df.drop_duplicates()

    # ==================================
    # DATA CLEANING
    # ==================================

    df['Submit'] = (
        df['Submit']
        .fillna('No')
        .astype(str)
        .str.strip()
    )

    df['Score Answer'] = pd.to_numeric(
        df['Score Answer'],
        errors='coerce'
    ).fillna(0)

    # ==================================
    # DATE CLEANING
    # ==================================

    if 'Completion Date' in df.columns:

        df['Completion Date'] = (
            df['Completion Date']
            .astype(str)
            .str.strip()
        )

        bulan_map = {
            'Jan': 'January',
            'Feb': 'February',
            'Mar': 'March',
            'Apr': 'April',
            'Mei': 'May',
            'Jun': 'June',
            'Jul': 'July',
            'Agu': 'August',
            'Sep': 'September',
            'Okt': 'October',
            'Nov': 'November',
            'Des': 'December'
        }

        for indo, eng in bulan_map.items():

            df['Completion Date'] = (
                df['Completion Date']
                .str.replace(
                    indo,
                    eng,
                    regex=False
                )
            )

        df['Completion Date'] = pd.to_datetime(
            df['Completion Date'],
            dayfirst=True,
            errors='coerce'
        )

        bulan_indonesia = {
            'January': 'Januari',
            'February': 'Februari',
            'March': 'Maret',
            'April': 'April',
            'May': 'Mei',
            'June': 'Juni',
            'July': 'Juli',
            'August': 'Agustus',
            'September': 'September',
            'October': 'Oktober',
            'November': 'November',
            'December': 'Desember'
        }

        df['Bulan'] = (
            df['Completion Date']
            .dt.month_name()
            .map(bulan_indonesia)
        )

    else:

        df['Bulan'] = 'Unknown'

    # ==================================
    # SIDEBAR FILTER
    # ==================================

    st.sidebar.header("🔍 Filter")

    urutan_bulan = [
        'Januari',
        'Februari',
        'Maret',
        'April',
        'Mei',
        'Juni',
        'Juli',
        'Agustus',
        'September',
        'Oktober',
        'November',
        'Desember'
    ]

    available_months = [
        b for b in urutan_bulan
        if b in df['Bulan'].dropna().unique()
    ]

    selected_month = st.sidebar.selectbox(
        "Bulan",
        ['All'] + available_months
    )

    cycle_list = (
        ['All']
        + sorted(
            df['Cycle']
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_cycle = st.sidebar.selectbox(
        "Cycle",
        [
            "All",
            "Daily",
            "Weekly & Monthly"
        ]
    )

    if 'Name' in df.columns:

        selected_name = st.sidebar.selectbox(
            "Nama",
            ['All']
            + sorted(
                df['Name']
                .dropna()
                .unique()
                .tolist()
            )
        )

    else:

        selected_name = 'All'

    if 'Posisi' in df.columns:

        selected_posisi = st.sidebar.selectbox(
            "Posisi",
            ['All']
            + sorted(
                df['Posisi']
                .dropna()
                .unique()
                .tolist()
            )
        )

    else:

        selected_posisi = 'All'

    if 'Branch' in df.columns:

        selected_branch = st.sidebar.selectbox(
            "Branch",
            ['All']
            + sorted(
                df['Branch']
                .dropna()
                .unique()
                .tolist()
            )
        )

    else:

        selected_branch = 'All'

    if 'Region' in df.columns:

        selected_region = st.sidebar.selectbox(
            "Region",
            ['All']
            + sorted(
                df['Region']
                .dropna()
                .unique()
                .tolist()
            )
        )

    else:

        selected_region = 'All'

    # ==================================
    # APPLY FILTER
    # ==================================

    filtered_df = df.copy()

    if selected_month != 'All':
        filtered_df = filtered_df[
            filtered_df['Bulan']
            == selected_month
        ]

    if selected_cycle == "Daily":
        filtered_df = filtered_df[
            filtered_df['Cycle']
            == 'Daily'
        ]
    elif selected_cycle == "Weekly & Monthly":
        filtered_df = filtered_df[
            filtered_df['Cycle']
            .isin(['Weekly', 'Monthly'])
    ]

    if selected_name != 'All':
        filtered_df = filtered_df[
            filtered_df['Name']
            == selected_name
        ]

    if selected_posisi != 'All':
        filtered_df = filtered_df[
            filtered_df['Posisi']
            == selected_posisi
        ]

    if selected_branch != 'All':
        filtered_df = filtered_df[
            filtered_df['Branch']
            == selected_branch
        ]

    if selected_region != 'All':
        filtered_df = filtered_df[
            filtered_df['Region']
            == selected_region
        ]

    # ==================================
    # KPI
    # ==================================

    total_submit = (
        filtered_df['Submit']
        .str.upper()
        .eq('YES')
        .sum()
    )

    total_no_submit = (
        filtered_df['Submit']
        .str.upper()
        .eq('NO')
        .sum()
    )

    total_task = (
        filtered_df['Task']
        .nunique()
        if 'Task' in filtered_df.columns
        else 0
    )

    total_activity = (
        filtered_df['Activity']
        .nunique()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Submit", f"{total_submit:,}")
    col2.metric("Total No Submit", f"{total_no_submit:,}")
    col3.metric("Total Task", f"{total_task:,}")
    col4.metric("Total Activity", f"{total_activity:,}")

    # ==================================
    # TABEL 1
    # ==================================

    summary_submit = (
        filtered_df
        .groupby(['Cycle', 'Activity'])
        .agg(
            Total_Submit=(
                'Submit',
                lambda x: (
                    x.astype(str)
                    .str.upper()
                    .eq('YES')
                    .sum()
                )
            ),
            Total_No_Submit=(
                'Submit',
                lambda x: (
                    x.astype(str)
                    .str.upper()
                    .eq('NO')
                    .sum()
                )
            )
        )
        .reset_index()
    )

    summary_submit['% Submit'] = (
        summary_submit['Total_Submit']
        /
        (
            summary_submit['Total_Submit']
            +
            summary_submit['Total_No_Submit']
        )
        * 100
    ).fillna(0).round(2)

    summary_submit = summary_submit.sort_values(
        by='Total_No_Submit',
        ascending=False
    )

    st.subheader("📋 Pengerjaan Mission")

    st.dataframe(
        summary_submit.rename(
            columns={
                'Total_Submit': 'Total Submit',
                'Total_No_Submit': 'Total No Submit'
            }
        ),
        use_container_width=True
    )

    # ==================================
    # TABEL 2
    # ==================================

    score_summary = (
        filtered_df
        .groupby(
            ['Cycle', 'Activity']
        )['Score Answer']
        .agg(
            Total_Benar=lambda x:
                (x == 10).sum(),

            Total_Salah=lambda x:
                (x == 0).sum()
        )
        .reset_index()
    )

    score_summary = score_summary.rename(
        columns={
            'Total_Benar':
                'Total Score Benar (10)',
            'Total_Salah':
                'Total Score Salah (0)'
        }
    )

    score_summary = score_summary.sort_values(
        by='Total Score Salah (0)',
        ascending=False
    )

    st.subheader(
        "🏆 Hasil Score Activity"
    )

    st.dataframe(
        score_summary,
        use_container_width=True
    )

    # ==================================
    # DOWNLOAD EXCEL
    # ==================================

    excel_file = BytesIO()

    with pd.ExcelWriter(
        excel_file,
        engine='openpyxl'
    ) as writer:

        summary_submit.to_excel(
            writer,
            sheet_name='Submit Summary',
            index=False
        )

        score_summary.to_excel(
            writer,
            sheet_name='Score Summary',
            index=False
        )

    st.download_button(
        label="⬇ Download Summary Excel",
        data=excel_file.getvalue(),
        file_name='mission_review_summary.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:

    st.info(
        "Silakan upload file Excel atau CSV."
    )
