from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Olist Sales & RFM Dashboard", page_icon="📊", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dashboard_data"

@st.cache_data
def load_data():
    required = {
        "monthly": DATA_DIR / "monthly_sales.csv",
        "segments": DATA_DIR / "rfm_segments.csv",
        "customers": DATA_DIR / "rfm_customers.csv",
        "monthly_segment": DATA_DIR / "monthly_sales_by_segment.csv",
    }
    missing = [p.name for p in required.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("File belum ditemukan: " + ", ".join(missing))
    monthly = pd.read_csv(required["monthly"])
    segments = pd.read_csv(required["segments"])
    customers = pd.read_csv(required["customers"])
    monthly_segment = pd.read_csv(required["monthly_segment"])
    monthly["order_month"] = pd.to_datetime(monthly["order_month"])
    monthly_segment["order_month"] = pd.to_datetime(monthly_segment["order_month"])
    for df, cols in [
        (monthly, ["total_sales"]),
        (monthly_segment, ["total_sales"]),
        (segments, ["Customer_Count", "Avg_Recency", "Avg_Frequency", "Avg_Monetary", "Total_Monetary", "Customer_Percentage"]),
        (customers, ["Recency", "Frequency", "Monetary"]),
    ]:
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return monthly, segments, customers, monthly_segment

st.title("📊 Brazilian E-Commerce: Sales & RFM Dashboard")
st.caption("Analisis penjualan produk dan karakteristik pelanggan berdasarkan transaksi berstatus delivered.")
try:
    monthly_sales, rfm_segments, rfm_customers, monthly_by_segment = load_data()
except Exception as exc:
    st.error("Data dashboard belum lengkap. Jalankan kembali cell ekspor pada notebook, lalu unggah seluruh CSV ke folder dashboard_data.")
    st.code("monthly_sales.csv\nmonthly_sales_by_segment.csv\nrfm_customers.csv\nrfm_segments.csv")
    st.exception(exc)
    st.stop()

st.sidebar.header("🎯 Filter Dashboard")
segment_options = sorted(rfm_customers["Segment"].dropna().unique())
selected_segment = st.sidebar.selectbox("Segmen Pelanggan", ["Semua Segmen"] + segment_options)
if selected_segment == "Semua Segmen":
    filtered_customers = rfm_customers.copy()
    filtered_monthly = monthly_sales.copy()
else:
    filtered_customers = rfm_customers[rfm_customers["Segment"] == selected_segment].copy()
    filtered_monthly = monthly_by_segment[monthly_by_segment["Segment"] == selected_segment].copy()

# Semua KPI dan visualisasi pelanggan dihitung dari data yang sudah difilter.
# Grafik penjualan juga memakai data penjualan yang sudah dikelompokkan per segmen.
total_sales = filtered_monthly["total_sales"].sum()
total_customers = filtered_customers["customer_unique_id"].nunique()
total_orders = int(filtered_customers["Frequency"].sum())
avg_monetary = filtered_customers["Monetary"].mean() if not filtered_customers.empty else 0

st.subheader("Ringkasan Kinerja")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penjualan", f"R$ {total_sales:,.2f}")
c2.metric("Jumlah Pelanggan", f"{total_customers:,}")
c3.metric("Total Pesanan", f"{total_orders:,}")
c4.metric("Rata-rata Monetary", f"R$ {avg_monetary:,.2f}")
st.caption("Seluruh KPI dan grafik mengikuti filter segmen yang dipilih.")
st.divider()

st.subheader("1. Perkembangan Penjualan Bulanan")
if not filtered_monthly.empty:
    filtered_monthly = filtered_monthly.sort_values("order_month")
    fig_sales = px.line(filtered_monthly, x="order_month", y="total_sales", markers=True,
                        labels={"order_month": "Bulan", "total_sales": "Total Penjualan (R$)"},
                        title="Tren Total Penjualan Produk per Bulan")
    fig_sales.update_layout(hovermode="x unified")
    st.plotly_chart(fig_sales, use_container_width=True)
    high = filtered_monthly.loc[filtered_monthly["total_sales"].idxmax()]
    low = filtered_monthly.loc[filtered_monthly["total_sales"].idxmin()]
    a, b = st.columns(2)
    a.info(f"**Penjualan tertinggi:** {high['order_month']:%B %Y} — R$ {high['total_sales']:,.2f}")
    b.info(f"**Penjualan terendah:** {low['order_month']:%B %Y} — R$ {low['total_sales']:,.2f}")
else:
    st.info("Tidak ada data penjualan untuk segmen ini.")
st.divider()

st.subheader("2. Distribusi Pelanggan Berdasarkan Segmen")
if selected_segment == "Semua Segmen":
    segment_view = (filtered_customers.groupby("Segment", as_index=False)
                    .agg(Customer_Count=("customer_unique_id", "nunique")))
else:
    segment_view = pd.DataFrame({"Segment": [selected_segment], "Customer_Count": [total_customers]})
a, b = st.columns(2)
with a:
    fig_count = px.bar(segment_view, x="Segment", y="Customer_Count", color="Segment",
                       title="Jumlah Pelanggan per Segmen",
                       labels={"Segment": "Segmen", "Customer_Count": "Jumlah Pelanggan"})
    fig_count.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_count, use_container_width=True)
with b:
    fig_share = px.pie(segment_view, names="Segment", values="Customer_Count",
                       title="Proporsi Pelanggan", hole=0.35)
    st.plotly_chart(fig_share, use_container_width=True)
st.divider()

st.subheader("3. Distribusi Metrik RFM")
a, b, c = st.columns(3)
with a:
    fig_recency = px.histogram(filtered_customers, x="Recency", nbins=30,
                               title="Distribusi Recency",
                               labels={"Recency": "Hari sejak transaksi terakhir"})
    st.plotly_chart(fig_recency, use_container_width=True)
with b:
    fig_frequency = px.histogram(filtered_customers, x="Frequency", nbins=30,
                                 title="Distribusi Frequency",
                                 labels={"Frequency": "Jumlah Pesanan"})
    st.plotly_chart(fig_frequency, use_container_width=True)
with c:
    fig_monetary = px.histogram(filtered_customers, x="Monetary", nbins=40,
                                title="Distribusi Monetary",
                                labels={"Monetary": "Total Pembelian (R$)"})
    st.plotly_chart(fig_monetary, use_container_width=True)
st.divider()

st.subheader("4. Ringkasan RFM Segmen Terpilih")
if not filtered_customers.empty:
    summary = (filtered_customers.groupby("Segment", as_index=False)
               .agg(Customer_Count=("customer_unique_id", "nunique"),
                    Avg_Recency=("Recency", "mean"),
                    Avg_Frequency=("Frequency", "mean"),
                    Avg_Monetary=("Monetary", "mean"),
                    Total_Monetary=("Monetary", "sum")))
    summary["Customer_Percentage"] = summary["Customer_Count"] / total_customers * 100
    st.dataframe(summary.rename(columns={"Segment": "Segmen", "Customer_Count": "Jumlah Pelanggan",
        "Avg_Recency": "Rata-rata Recency (hari)", "Avg_Frequency": "Rata-rata Frequency",
        "Avg_Monetary": "Rata-rata Monetary (R$)", "Total_Monetary": "Total Monetary (R$)",
        "Customer_Percentage": "Persentase (%)"}), use_container_width=True, hide_index=True)

st.subheader("5. Detail Pelanggan")
st.caption("Menampilkan maksimal 100 pelanggan dengan nilai Monetary tertinggi pada hasil filter.")
cols = ["customer_unique_id", "Recency", "Frequency", "Monetary", "RFM_score", "Segment"]
show = filtered_customers.sort_values("Monetary", ascending=False)[cols].head(100).rename(columns={
    "customer_unique_id": "ID Pelanggan", "Recency": "Recency (hari)",
    "Frequency": "Frequency", "Monetary": "Monetary (R$)",
    "RFM_score": "Skor RFM", "Segment": "Segmen"})
st.dataframe(show, use_container_width=True, hide_index=True)
st.download_button("⬇️ Download Data Pelanggan", filtered_customers.to_csv(index=False).encode("utf-8"),
                   file_name="data_pelanggan_rfm.csv", mime="text/csv")
st.caption("Brazilian E-Commerce Public Dataset by Olist | Dicoding Data Analysis Project")
