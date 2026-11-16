from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# Folder data berada sejajar dengan app.py
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dashboard_data"

st.set_page_config(
    page_title="Brazilian E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown("Analisis Penjualan dan Segmentasi Pelanggan Menggunakan RFM")

@st.cache_data
def load_data():
    monthly = pd.read_csv(DATA_DIR / "monthly_sales.csv")
    segments = pd.read_csv(DATA_DIR / "rfm_segments.csv")
    customers = pd.read_csv(DATA_DIR / "rfm_customers.csv")

    monthly["order_month"] = pd.to_datetime(monthly["order_month"])
    monthly["total_sales"] = pd.to_numeric(
        monthly["total_sales"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    for col in ["Avg_Recency", "Avg_Frequency", "Avg_Monetary",
                "Total_Monetary", "Customer_Percentage"]:
        if col in segments.columns:
            segments[col] = pd.to_numeric(
                segments[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            )

    for col in ["Recency", "Frequency", "Monetary", "R_score",
                "F_score", "M_score", "RFM_score"]:
        if col in customers.columns:
            customers[col] = pd.to_numeric(customers[col], errors="coerce")

    return monthly, segments, customers

try:
    monthly_sales, rfm_segments, rfm_customers = load_data()
except Exception as exc:
    st.error("Data dashboard belum ditemukan atau gagal dibaca.")
    st.write(f"Pastikan folder `{DATA_DIR.name}` berada sejajar dengan `app.py` dan berisi:")
    st.code("monthly_sales.csv\nrfm_segments.csv\nrfm_customers.csv")
    st.exception(exc)
    st.stop()

# Filter segmen pelanggan
st.sidebar.header("🎯 Filter Dashboard")
st.sidebar.caption("Pilih segmen pelanggan untuk melihat detail analisis.")
segment_options = sorted(rfm_customers["Segment"].dropna().unique())
selected_segment = st.sidebar.selectbox(
    "Segmen Pelanggan",
    ["Semua Segmen"] + segment_options
)

if selected_segment == "Semua Segmen":
    filtered_customers = rfm_customers.copy()
else:
    filtered_customers = rfm_customers[
        rfm_customers["Segment"] == selected_segment
    ]

st.sidebar.divider()
st.sidebar.metric("Jumlah Pelanggan", f"{len(filtered_customers):,}")

# KPI
total_sales = monthly_sales["total_sales"].sum()
total_customers = rfm_customers["customer_unique_id"].nunique()
total_orders = int(rfm_customers["Frequency"].sum())
avg_monetary = rfm_customers["Monetary"].mean()

st.subheader("Ringkasan Kinerja E-Commerce")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penjualan", f"R$ {total_sales:,.2f}")
c2.metric("Total Pelanggan", f"{total_customers:,}")
c3.metric("Total Transaksi", f"{total_orders:,}")
c4.metric("Rata-rata Pembelian", f"R$ {avg_monetary:,.2f}")

st.divider()

# Penjualan bulanan
st.subheader("1. Perkembangan Penjualan Bulanan")
fig_sales = px.line(
    monthly_sales.sort_values("order_month"),
    x="order_month",
    y="total_sales",
    markers=True,
    labels={
        "order_month": "Bulan",
        "total_sales": "Total Penjualan (R$)"
    },
    title="Tren Total Penjualan Produk per Bulan"
)
fig_sales.update_layout(hovermode="x unified")
st.plotly_chart(fig_sales, use_container_width=True)

if not monthly_sales.empty:
    highest = monthly_sales.loc[monthly_sales["total_sales"].idxmax()]
    lowest = monthly_sales.loc[monthly_sales["total_sales"].idxmin()]
    left, right = st.columns(2)
    left.info(
        f"**Penjualan tertinggi:** {highest['order_month']:%B %Y} "
        f"sebesar R$ {highest['total_sales']:,.2f}"
    )
    right.info(
        f"**Penjualan terendah:** {lowest['order_month']:%B %Y} "
        f"sebesar R$ {lowest['total_sales']:,.2f}"
    )

st.divider()

# Segmentasi RFM
st.subheader("2. Segmentasi Pelanggan Berdasarkan RFM")
col1, col2 = st.columns(2)

with col1:
    fig_count = px.bar(
        rfm_segments.sort_values("Customer_Count", ascending=False),
        x="Segment",
        y="Customer_Count",
        color="Segment",
        title="Jumlah Pelanggan pada Setiap Segmen",
        labels={"Segment": "Segmen Pelanggan", "Customer_Count": "Jumlah Pelanggan"}
    )
    fig_count.update_layout(showlegend=False, xaxis_tickangle=-35)
    st.plotly_chart(fig_count, use_container_width=True)

with col2:
    fig_share = px.pie(
        rfm_segments,
        names="Segment",
        values="Customer_Count",
        title="Proporsi Pelanggan Berdasarkan Segmen",
        hole=0.35
    )
    st.plotly_chart(fig_share, use_container_width=True)

st.divider()

# Karakteristik pelanggan
st.subheader("3. Karakteristik Pelanggan")
col1, col2 = st.columns(2)

with col1:
    fig_frequency = px.histogram(
        filtered_customers,
        x="Frequency",
        nbins=30,
        title="Distribusi Frekuensi Pembelian",
        labels={"Frequency": "Jumlah Transaksi"}
    )
    st.plotly_chart(fig_frequency, use_container_width=True)

with col2:
    fig_monetary = px.histogram(
        filtered_customers,
        x="Monetary",
        nbins=40,
        title="Distribusi Nilai Pembelian",
        labels={"Monetary": "Total Pembelian (R$)"}
    )
    st.plotly_chart(fig_monetary, use_container_width=True)

st.divider()

# Detail pelanggan
st.subheader("4. Detail Pelanggan")
st.write("Tabel menampilkan maksimal 100 pelanggan dengan nilai pembelian tertinggi pada segmen yang dipilih.")

display_columns = [
    "customer_unique_id", "Recency", "Frequency",
    "Monetary", "RFM_score", "Segment"
]
display_data = (
    filtered_customers[display_columns]
    .sort_values("Monetary", ascending=False)
    .head(100)
    .rename(columns={
        "customer_unique_id": "ID Pelanggan",
        "Recency": "Recency (hari)",
        "Frequency": "Frequency",
        "Monetary": "Monetary (R$)",
        "RFM_score": "Skor RFM",
        "Segment": "Segmen"
    })
)
st.dataframe(display_data, use_container_width=True, hide_index=True)

csv_data = filtered_customers.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Data Pelanggan",
    data=csv_data,
    file_name="data_pelanggan_rfm.csv",
    mime="text/csv"
)

st.divider()
st.subheader("5. Ringkasan Segmen RFM")
summary_columns = [
    "Segment", "Customer_Count", "Avg_Recency",
    "Avg_Frequency", "Avg_Monetary", "Total_Monetary",
    "Customer_Percentage"
]
summary = rfm_segments[summary_columns].rename(columns={
    "Segment": "Segmen Pelanggan",
    "Customer_Count": "Jumlah Pelanggan",
    "Avg_Recency": "Rata-rata Recency",
    "Avg_Frequency": "Rata-rata Frequency",
    "Avg_Monetary": "Rata-rata Monetary (R$)",
    "Total_Monetary": "Total Monetary (R$)",
    "Customer_Percentage": "Persentase Pelanggan (%)"
})
st.dataframe(summary, use_container_width=True, hide_index=True)

st.caption("Brazilian E-Commerce Public Dataset by Olist | Dicoding Data Analysis Project")
