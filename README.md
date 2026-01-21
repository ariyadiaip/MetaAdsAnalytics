# ♾️Sistem Analisis & Optimasi Iklan Digital (RFM)

Dashboard analitik berbasis Python untuk menganalisis performa penjualan dan efektivitas iklan digital menggunakan metode **RFM Segmentation (Recency, Frequency, Monetary)** dan **K-Means Clustering**.

Aplikasi ini dirancang untuk membantu pengambilan keputusan strategis berdasarkan perilaku pelanggan dan kinerja kampanye iklan (Meta Ads).

## 📊 Fitur Utama

- **Executive Summary**
  - Scorecard kinerja bisnis (Total Revenue, Real Orders, Ads Purchase, Conversion Rate).
  - Grafik tren pendapatan harian.
  - Analisis produk terlaris dan kota dengan penjualan tertinggi.

- **RFM Segmentation (K-Means)**
  - Mengelompokkan pelanggan secara otomatis menjadi 5 segmen:
    - 🏆 **Champion (VIP)**
    - 💎 **Loyal Customer**
    - 🌟 **Potential Loyalist**
    - 👶 **New Customer**
    - 💤 **Hibernating / Low Value**
  - Visualisasi sebaran pelanggan (Scatter Plot & Bar Chart).

- **Automated Business Strategy**
  - Menghasilkan rekomendasi strategi bisnis spesifik untuk setiap segmen.
  - Integrasi data demografi (Kota) dan target usia dari data iklan.
  - Fitur download laporan strategi ke format CSV.

## 🛠️ Teknologi yang Digunakan

- **Bahasa Pemrograman:** Python 3.10+
- **Web Framework:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, NumPy, OpenPyXL
- **Machine Learning:** Scikit-Learn (K-Means Clustering, StandardScaler)
- **Visualisasi Data:** Matplotlib, Seaborn

## 📂 Struktur Folder Repository

Pastikan struktur folder Anda seperti di bawah ini agar aplikasi berjalan lancar:

```text
.
├── app.py               # Source code utama aplikasi
├── requirements.txt     # Daftar library yang dibutuhkan
├── README.md            # Dokumentasi proyek
├── assets/              # Folder aset gambar statis
│   └── meta_logo.png    # Logo meta ads
└── DATAQ3/              # Folder dataset (Excel)
    ├── Data Penjualan.xlsx
    └── Data Campaign.xlsx
```

## 🚀 Cara Menjalankan (Local Machine)

Jika Anda ingin menjalankan aplikasi ini di komputer lokal Anda:

1. **Clone Repository**
   ```bash
   git clone [https://github.com/ariyadiaip/MetaAdsAnalytics.git](https://github.com/ariyadiaip/MetaAdsAnalytics.git)
   cd MetaAdsAnalytics
   ```

2. **Buat Virtual Environment (Opsional tapi Disarankan)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi**
   ```bash
   streamlit run app.py
   ```

## 🌐 Deploy ke Streamlit Cloud

Aplikasi ini siap untuk di-deploy secara gratis menggunakan **Streamlit Community Cloud**:

1. Push kode ini ke repository GitHub Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io/).
3. Klik **"New App"**.
4. Pilih repository, branch (`main`), dan file utama (`app.py`).
5. Klik **Deploy!**

---
**© 2026 Universitas Komputer Indonesia (UNIKOM)**

*Dibuat dengan menggunakan Python & Streamlit.*