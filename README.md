# Analisis Brazilian E-Commerce Public Dataset (Olist) ✨

## Setup Environment - Anaconda

```bash
conda create --name olist-dashboard python=3.10
conda activate olist-dashboard
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```bash
pip install -r requirements.txt
```

## Struktur Folder

```text
submission_olist/
├── Proyek_Analisis_Olist_Revisi_Reviewer.ipynb
├── app.py
├── requirements.txt
├── README.md
├── url.txt
├── data/
└── dashboard_data/
    ├── monthly_sales.csv
    ├── monthly_sales_by_segment.csv
    ├── rfm_customers.csv
    └── rfm_segments.csv
```

## Run Streamlit App

```bash
streamlit run app.py
```

## Dashboard

[Olist Sales & Customer Segmentation Dashboard](https://olist-sales-rfm-dashboard.streamlit.app/)un dan menjalankan dashboard interaktif.
