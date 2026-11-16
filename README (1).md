# Analisis Brazilian E-Commerce Public Dataset (Olist)

## Deskripsi Proyek

Proyek ini menganalisis kinerja penjualan produk dan karakteristik pelanggan pada Brazilian E-Commerce Public Dataset by Olist. Analisis dilakukan melalui data wrangling, exploratory data analysis (EDA), visualisasi, dan segmentasi pelanggan menggunakan Recency, Frequency, dan Monetary (RFM).

Dashboard interaktif dibuat menggunakan Streamlit untuk menampilkan perkembangan penjualan bulanan dan karakteristik segmen pelanggan.

## Pertanyaan Bisnis

1. Bagaimana perkembangan total nilai penjualan produk setiap bulan pada periode transaksi *delivered* yang tersedia, dan bulan apa yang memiliki nilai penjualan tertinggi serta terendah?
2. Bagaimana karakteristik pelanggan berdasarkan Recency, Frequency, dan Monetary (RFM), serta segmen pelanggan mana yang perlu diprioritaskan dalam strategi retensi?

## Struktur Folder

Simpan file proyek dengan susunan berikut:

```text
submission_olist/
├── Proyek_Analisis_Olist.ipynb
├── app.py
├── requirements.txt
├── README.md
├── dashboard_data/
│   ├── monthly_sales.csv
│   ├── rfm_customers.csv
│   └── rfm_segments.csv
└── data/
    └── dataset asli Olist
```

Folder `dashboard_data` harus berada sejajar dengan `app.py`. Ketiga file CSV di dalamnya merupakan hasil ekspor dari notebook analisis.

## Persiapan Environment

Pastikan Python sudah terpasang. Disarankan menggunakan Python 3.10 atau versi yang kompatibel dengan library pada `requirements.txt`.

### Menggunakan Anaconda

```bash
conda create --name olist-dashboard python=3.10
conda activate olist-dashboard
pip install -r requirements.txt
```

### Menggunakan Shell atau Terminal

Buka terminal pada folder proyek, lalu jalankan:

```bash
pip install -r requirements.txt
```

## Menjalankan Dashboard

Pastikan struktur folder `dashboard_data` dan ketiga file CSV sudah tersedia. Kemudian, dari direktori yang sama dengan `app.py`, jalankan:

```bash
streamlit run app.py
```

Streamlit akan menampilkan alamat lokal pada terminal, biasanya:

```text
http://localhost:8501
```

Buka alamat tersebut melalui browser untuk mengakses dashboard.

## Library yang Digunakan

- **gdown**: mengunduh dataset dari Google Drive apabila diperlukan pada notebook.
- **Pandas**: membaca, membersihkan, dan mengolah data.
- **NumPy**: mendukung operasi numerik.
- **Matplotlib** dan **Seaborn**: membuat visualisasi pada proses analisis.
- **Plotly**: membuat grafik interaktif pada dashboard.
- **Streamlit**: membangun dan menjalankan dashboard interaktif.
