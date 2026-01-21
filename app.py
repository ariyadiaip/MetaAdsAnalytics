import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import re
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from PIL import Image

# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================

try:
    logo_icon = Image.open("assets/meta_logo.png") 
except FileNotFoundError:
    logo_icon = "♾️"

st.set_page_config(
    page_title="Sistem Optimasi Iklan Digital (RFM)",
    page_icon=logo_icon,
    layout="wide"
)

# =============================================================================
# CSS INJECTION
# =============================================================================
st.markdown("""
<style>
    /* Mengubah warna tabs */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1877F2 !important;
    }
            
    div[data-baseweb="tab-highlight"] {
        background-color: #1877F2 !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #1877F2 !important;
    }
            
    span[data-baseweb="tag"] {
        background-color: #1877F2 !important;
    }

    /* Mengubah warna tombol filter */
    span[data-baseweb="tag"] span {
        color: white !important;
    }
    
    div[data-baseweb="select"] > div:focus-within {
        border-color: #1877F2 !important;
    }
            
    /* Mengubah Warna Tabel */
    thead tr th {
        background-color: #1877F2 !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    tbody tr td {
        border-color: #f0f2f6 !important;
    }
            
    /* Mengubah warna tombol Download */
    div.stDownloadButton > button:first-child {
        background-color: #1877F2;
        color: white;
        border-color: #1877F2;
    }
    div.stDownloadButton > button:first-child:hover {
        background-color: #155db2;
        border-color: #155db2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNGSI-FUNGSI LOGIKA
# =============================================================================

# 1. SETUP PATH & LOAD DATA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, 'DATAQ3')

@st.cache_data
def load_and_merge_data(file_name, month_list):
    file_path = os.path.join(DATA_FOLDER, file_name)
    all_data = []
    
    # Cek apakah file ada
    if not os.path.exists(file_path):
        st.error(f"File tidak ditemukan: {file_path}. Pastikan file ada di folder 'DATAQ3'.")
        return pd.DataFrame()

    for bulan in month_list:
        try:
            # Membaca sheet spesifik
            df_temp = pd.read_excel(file_path, sheet_name=bulan)
            # Menambah penanda bulan (untuk tracking filter)
            df_temp['source_month'] = bulan
            all_data.append(df_temp)
        except Exception as e:
            st.warning(f"Gagal membaca sheet '{bulan}' di {file_name}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# 2. DATA CLEANING & PREPROCESSING
def clean_product_name(text):
    if pd.isna(text): return ""
    text = str(text).upper()
    text = re.sub(r'\s*\(.*?\)', '', text) # Hapus dalam kurung
    if ' - ' in text:
        text = text.split(' - ')[-1] # Ambil kata terakhir setelah strip
    text = re.sub(r'^\w*\d\w*\s+', '', text) # Hapus kode awalan angka
    return text.strip()

def process_data(df_sales_raw, df_ads_raw):
    # --- PROCESSING SALES ---
    df_sales = df_sales_raw.copy()
    
    # Handling kolom product/variation
    target_col_sales = 'product' if 'product' in df_sales.columns else 'variation'
    if target_col_sales not in df_sales.columns:
        st.error("Kolom 'product' atau 'variation' tidak ditemukan di Data Penjualan!")
        return None, None

    # Standarisasi Kolom
    df_sales['status'] = df_sales['status'].astype(str).str.strip().str.lower()
    df_sales = df_sales[df_sales['status'] == 'completed'] # Filter Completed
    
    df_sales['created_at'] = pd.to_datetime(df_sales['created_at'], dayfirst=True, errors='coerce')
    df_sales = df_sales.dropna(subset=['created_at'])
    
    # Standarisasi String
    cols_to_clean = ['name', 'province', 'city']
    for col in cols_to_clean:
        if col in df_sales.columns:
            df_sales[col] = df_sales[col].astype(str).str.upper().str.strip()
            
    # Regex Nama Produk
    df_sales['product_clean'] = df_sales[target_col_sales].apply(clean_product_name)
    
    # --- PROCESSING ADS ---
    df_ads = df_ads_raw.copy()
    df_ads['Purchases'] = df_ads['Purchases'].fillna(0).astype(int)
    df_ads['campaign_clean'] = df_ads['Campaign Name'].apply(clean_product_name)
    
    return df_sales, df_ads

# 3. HELPER FUNCTIONS UNTUK STRATEGI
def get_mode(series):
    return series.mode().iloc[0] if not series.mode().empty else "Unknown"

def get_ads_insight(product_name, df_ads):
    matched_ads = df_ads[df_ads['campaign_clean'] == product_name]
    if len(matched_ads) > 0:
        top_age = matched_ads.groupby('Age')['Purchases'].sum().idxmax()
        return top_age
    else:
        return "All Ages (General)"

# 4. HELPER FUNCTIONS UNTUK SCORECARDS
def format_big_number(value):
    """
    Mengubah angka besar menjadi format K (Ribu), Jt (Juta), M (Miliar)
    """
    if value >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.2f} M"
    elif value >= 1_000_000:
        return f"Rp {value / 1_000_000:.2f} Jt"
    elif value >= 1_000:
        return f"Rp {value / 1_000:.2f} K"
    else:
        return f"Rp {value:,.0f}"
    
# 5 DIALOG ABOUT US
@st.dialog("👨‍💻 Tim Pengembang")
def show_about_modal():
    st.markdown("""
    Aplikasi ini dikembangkan sebagai bagian dari **Proyek Sains Data** Program Studi **Teknik Informatika**.
    """)
    
    data_tim = [
        {"NIM": "10122084", "Nama": "Frederick Cornelius Nathaniel"},
        {"NIM": "10121305", "Nama": "Alief Sidik Gunawan"},
        {"NIM": "10122901", "Nama": "Aip Ariyadi"},
        {"NIM": "10122907", "Nama": "Vina Lestari"},
        {"NIM": "10122912", "Nama": "Annisaa Fitri"},
        {"NIM": "10124908", "Nama": "Duta Windu Darma"},
    ]
    
    df_tim = pd.DataFrame(data_tim)
    st.table(df_tim.set_index('NIM'))
    
    st.caption("© 2026 Universitas Komputer Indonesia (UNIKOM) - IF13")
    st.caption("Dibuat dengan **Python** & **Streamlit**")

# =============================================================================
# MAIN APP UI
# =============================================================================

col_logo, col_title = st.columns([1, 10]) 

with col_logo:
    try:
        st.image("assets/meta_logo.png", width=80) 
    except:
        st.write("♾️")

with col_title:
    # Gunakan margin top negatif di markdown agar lurus dengan logo
    st.markdown("""
    <h1 style='margin-bottom: 0px; margin-top: 0px;'>
        Sistem Analisis & Optimasi Strategi Iklan Digital
    </h1>
    """, unsafe_allow_html=True)

st.markdown("Dashboard ini mengintegrasikan analisis penjualan dan kinerja iklan berbasis segmentasi pelanggan **RFM**.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    # Filter Periode
    pilihan_bulan = st.selectbox(
        "Pilih Periode Analisis:",
        ["Semua Data (Q3)", "JULI", "AGUSTUS", "SEPTEMBER"]
    )

    # Informasi Data
    st.info(
        """
        **ℹ️ Sumber Data:**
        Data Penjualan & Kinerja Iklan
        **Periode Q3 2025**
        (Juli - September 2025)
        """
    )

    # About Us
    if st.button("ℹ️ Tentang"):
        show_about_modal()

# --- LOAD DATA ---
all_months = ['JULI', 'AGUSTUS', 'SEPTEMBER']

with st.spinner('Sedang memuat data...'):
    df_sales_raw = load_and_merge_data('Data Penjualan.xlsx', all_months)
    df_ads_raw = load_and_merge_data('Data Campaign.xlsx', all_months)

if df_sales_raw.empty or df_ads_raw.empty:
    st.stop() # Berhenti jika data kosong

# --- FILTERING DATA BERDASARKAN BULAN PILIHAN ---
if pilihan_bulan != "Semua Data (Q3)":
    df_sales_filtered = df_sales_raw[df_sales_raw['source_month'] == pilihan_bulan]
    df_ads_filtered = df_ads_raw[df_ads_raw['source_month'] == pilihan_bulan]
else:
    df_sales_filtered = df_sales_raw
    df_ads_filtered = df_ads_raw

# --- EXECUTE PROCESSING PIPELINE ---
df_sales_clean, df_ads_clean = process_data(df_sales_filtered, df_ads_filtered)

if df_sales_clean is not None:
    
    # --- RFM CALCULATION ---
    # Tentukan Snapshot Date (Besoknya dari transaksi terakhir di data yang difilter)
    max_date = df_sales_clean['created_at'].max()
    snapshot_date = max_date + dt.timedelta(days=1)
    
    df_rfm = df_sales_clean.groupby('name').agg({
        'created_at': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique', # Asumsi order_id unik per transaksi
        'net_revenue': 'sum'
    }).reset_index()
    
    df_rfm.rename(columns={'created_at': 'Recency', 'order_id': 'Frequency', 'net_revenue': 'Monetary'}, inplace=True)
    
    # --- CLUSTERING (K-MEANS) ---
    # Scaling
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(df_rfm[['Recency', 'Frequency', 'Monetary']])
    
    # KMeans K=5 (Fixed sesuai riset notebook)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df_rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    # Naming Segmen (Mapping berdasarkan urutan Monetary)
    cluster_summary = df_rfm.groupby('Cluster')['Monetary'].mean().reset_index()
    cluster_summary = cluster_summary.sort_values(by='Monetary', ascending=True).reset_index(drop=True)
    
    segment_names = [
        'Hibernating / Low Value',
        'New Customer',
        'Potential Loyalist',
        'Loyal Customer',
        'Champion (VIP)'
    ]
    
    cluster_map = {row['Cluster']: segment_names[i] for i, row in cluster_summary.iterrows()}
    df_rfm['Segment_Name'] = df_rfm['Cluster'].map(cluster_map)
    
    # Merge Segmen kembali ke Data Transaksi
    df_final = df_sales_clean.merge(df_rfm[['name', 'Segment_Name']], on='name', how='left')

    # --- TABS VISUALISASI ---
    tab1, tab2, tab3 = st.tabs(["📊 **Executive Summary**", "👥 **Segmentasi Pelanggan**", "🎯 **Rekomendasi Strategi**"])
    
    # === TAB 1: EXECUTIVE SUMMARY ===
    with tab1:
        st.subheader(f"Performa Bisnis - {pilihan_bulan}")
        
        # SCORECARDS
        col1, col2, col3, col4 = st.columns(4)

        total_revenue = df_sales_clean['net_revenue'].sum()
        total_orders = df_sales_clean['order_id'].nunique()
        total_purchases_ads = df_ads_clean['Purchases'].sum()
        conversion_rate = (total_orders / df_rfm.shape[0])

        # --- METRIC 1: TOTAL REVENUE (Dinamis) ---
        col1.metric(
            label="**Total Revenue**",
            value=format_big_number(total_revenue),
            help=f"Total Revenue: Rp {total_revenue:,.0f}"
        )
        
        # --- METRIC 2: TOTAL ORDER ---
        col2.metric(
            label="**Total Order (Real)**",
            value=f"{total_orders:,.0f}",
            help="Total Order ID unik yang statusnya Completed"
        )
        
        # --- METRIC 3: ADS PURCHASE ---
        col3.metric(
            label="**Total Purchase (Ads Attr.)**",
            value=f"{total_purchases_ads:,.0f}",
            help="Total konversi Purchase yang tercatat di Dashboard Iklan"
        )
        
        # --- METRIC 4: CONVERSION RATE ---
        col4.metric(
            label="**Conversion Rate (Est)**",
            value=f"{conversion_rate:.2f} Tx/User",
            help="Rata-rata transaksi per user (Total Order / Total User Unik)"
    )
        
        st.markdown("---")
        
        # GRAFIK TREN HARIAN
        st.subheader("Tren Pendapatan Harian")
        daily_revenue = df_sales_clean.groupby(df_sales_clean['created_at'].dt.date)['net_revenue'].sum().reset_index()
        fig_trend, ax_trend = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=daily_revenue, x='created_at', y='net_revenue', marker='o', ax=ax_trend, color='teal')
        ax_trend.set_title("Daily Net Revenue")
        ax_trend.set_xlabel("Tanggal")
        ax_trend.set_ylabel("Revenue (Rp)")
        plt.xticks(rotation=45)
        st.pyplot(fig_trend)

        st.markdown("---")
        
        # TOP PRODUK & TOP KOTA
        col_top1, col_top2 = st.columns(2)

        with col_top1:
            st.subheader("🏆 Top 5 Produk Terlaris")
            # Hitung Revenue per Produk, ambil 5 teratas
            top_products = df_sales_clean.groupby('product_clean')['net_revenue'].sum().sort_values(ascending=False).head(5).reset_index()
            
            fig_prod, ax_prod = plt.subplots(figsize=(6, 4))
            sns.barplot(data=top_products, y='product_clean', x='net_revenue', hue='product_clean', legend=False, palette='viridis', ax=ax_prod)
            ax_prod.set_xlabel("Total Revenue (Rp)")
            ax_prod.set_ylabel("")
            st.pyplot(fig_prod)

        with col_top2:
            st.subheader("📍 Top 5 Kota Pembelian")
            # Hitung Revenue per Kota, ambil 5 teratas
            top_cities = df_sales_clean.groupby('city')['net_revenue'].sum().sort_values(ascending=False).head(5).reset_index()
            
            fig_city, ax_city = plt.subplots(figsize=(6, 4))
            sns.barplot(data=top_cities, y='city', x='net_revenue', hue='city', legend=False, palette='magma', ax=ax_city)
            ax_city.set_xlabel("Total Revenue (Rp)")
            ax_city.set_ylabel("")
            st.pyplot(fig_city)
        # =========================================================

    # === TAB 2: SEGMENTASI PELANGGAN ===
    with tab2:
        st.subheader("Analisis Segmentasi RFM (K-Means)")

        col_seg1, col_seg2 = st.columns([1, 2])
        
        with col_seg1:
            # Hitung Jumlah Customer per Segmen
            seg_counts = df_rfm['Segment_Name'].value_counts().reset_index()
            seg_counts.columns = ['Segment_Name', 'Jumlah Customer']

            df_segment_view = seg_counts[['Segment_Name', 'Jumlah Customer']].copy()
            
            df_segment_view = df_segment_view.rename(columns={
                'Segment_Name': 'Segmen Pelanggan',
                'Jumlah Customer': 'Total User'
            })

            st.markdown("##### Disribusi Segmen")
            st.table(df_segment_view.set_index('Segmen Pelanggan'))
            
            # Horizontal Bar Chart
            total_cust = seg_counts['Jumlah Customer'].sum()
            seg_counts['Persentase'] = (seg_counts['Jumlah Customer'] / total_cust) * 100
            seg_counts['Label'] = seg_counts.apply(lambda x: f"{x['Segment_Name']} ({x['Persentase']:.1f}%)", axis=1)
            
            fig_bar_seg, ax_bar_seg = plt.subplots(figsize=(6, 4))
            fig_bar_seg.patch.set_alpha(0)
            ax_bar_seg.patch.set_alpha(0)
            
            # Plot Bar Chart Horizontal
            sns.barplot(
                data=seg_counts, 
                y='Label',          # Gunakan label yang ada persentasenya
                x='Jumlah Customer', 
                hue='Label',
                legend=False,
                palette='viridis',  # Warna distinct agar beda tiap segmen
                ax=ax_bar_seg
            )
            
            # Tambahkan Angka Jumlah Orang di Ujung Batang
            for container in ax_bar_seg.containers:
                ax_bar_seg.bar_label(container, padding=5, fmt='%d User', color='#333333')
            
            # Bersihkan chart junk
            sns.despine(left=True, bottom=True)
            ax_bar_seg.set_xlabel("")
            ax_bar_seg.set_ylabel("")
            ax_bar_seg.set_xticks([]) # Hilangkan angka sumbu X
            
            st.pyplot(fig_bar_seg)
            
        with col_seg2:
            st.markdown("##### Peta Persebaran Pelanggan")

            st.info(
                """
                **💡 Panduan Membaca Grafik:**
                * **Sumbu Y (Vertikal):** Total Uang yang dibelanjakan (Monetary). Makin ke atas, makin **Sultan**.
                * **Sumbu X (Horizontal):** Jarak hari dari pembelian terakhir (Recency). Makin ke kanan, makin **Baru Belanja**.
                """
            )

            fig_scatter, ax_scatter = plt.subplots(figsize=(8, 6))
            fig_scatter.patch.set_alpha(0)
            ax_scatter.patch.set_alpha(0)
            ax_scatter.tick_params(colors='#888888')
            ax_scatter.xaxis.label.set_color('#888888')
            ax_scatter.yaxis.label.set_color('#888888')
            ax_scatter.title.set_color('#888888')
            
            # Scatter Plot
            sns.scatterplot(
                data=df_rfm, 
                x='Recency', 
                y='Monetary', 
                hue='Segment_Name', 
                palette='viridis', 
                s=100, 
                ax=ax_scatter
            )
            
            # Hapus judul di dalam grafik
            ax_scatter.set_title("") 
            ax_scatter.set_xlabel("Recency (Hari)")
            ax_scatter.set_ylabel("Monetary (Rp)")
            
            st.pyplot(fig_scatter)

    # === TAB 3: STRATEGI BISNIS ===
    with tab3:
        st.subheader("Rekomendasi Strategi Bisnis")
        
        # --- GENERATE STRATEGY LOGIC ---
        # 1. Profiling Segmen
        segment_counts_rfm = df_rfm['Segment_Name'].value_counts().reset_index()
        segment_counts_rfm.columns = ['Segment_Name', 'Jumlah_Pelanggan']
        
        segment_profile = df_final.groupby('Segment_Name').agg({
            'city': lambda x: get_mode(x),
            'province': lambda x: get_mode(x),
            'product_clean': lambda x: get_mode(x),
            'net_revenue': 'mean'
        }).reset_index()
        
        segment_profile = segment_profile.merge(segment_counts_rfm, on='Segment_Name')
        
        # 2. Cross-Match Ads Data
        segment_profile['Target_Age_Ads'] = segment_profile['product_clean'].apply(
            lambda x: get_ads_insight(x, df_ads_clean)
        )
        
        # 3. Generate Strategy
        def generate_strategy(row):
            segmen = row['Segment_Name']
            produk = row['product_clean']
            kota = row['city']
            umur = row['Target_Age_Ads']
            
            if "Champion" in segmen or ("Loyal" in segmen and "Potential" not in segmen):
                return f"RETENTION: Tawarkan 'Exclusive Bundle' {produk}. Targetkan area {kota} (Umur {umur}). Fokus jaga loyalitas."
            elif "Potential" in segmen:
                return f"PROMOTION: Cross-sell produk {produk} ke pelanggan di {kota}. Targetkan audiens {umur} untuk naikkan frekuensi."
            elif "New" in segmen:
                return f"ONBOARDING: Dorong pembelian kedua untuk {produk}. Gunakan iklan testimoni di {kota} (Target {umur})."
            elif "Hibernating" in segmen or "Low" in segmen:
                return f"WIN-BACK: Beri diskon khusus/ongkir untuk {produk}. Fokus area {kota} saja untuk hemat budget."
            else:
                return f"GENERAL: Optimalkan iklan {produk} di {kota}."

        segment_profile['Strategi_Bisnis'] = segment_profile.apply(generate_strategy, axis=1)
        
        # --- DISPLAY OUTPUT ---
        # Filter Pilihan Segmen
        pilihan_segmen_view = st.multiselect(
            "Filter Segmen untuk Dilihat:", 
            segment_profile['Segment_Name'].unique(),
            default=segment_profile['Segment_Name'].unique()
        )
        
        df_display_strategy = segment_profile[segment_profile['Segment_Name'].isin(pilihan_segmen_view)]
        
        # Rename header untuk tampilan
        df_show = df_display_strategy[['Segment_Name', 'Jumlah_Pelanggan', 'product_clean', 'city', 'Target_Age_Ads', 'Strategi_Bisnis']].rename(columns={
            'Segment_Name': 'Segmen Pelanggan',
            'Jumlah_Pelanggan': 'Total User',
            'product_clean': 'Produk Hero',
            'city': 'Fokus Kota',
            'Target_Age_Ads': 'Target Usia',
            'Strategi_Bisnis': 'Rekomendasi Strategi'
        })
        
        st.table(df_show.set_index('Segmen Pelanggan'))
        
        # Download Button
        csv = df_show.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Strategi (CSV)",
            data=csv,
            file_name=f'Strategi_Bisnis_{pilihan_bulan}.csv',
            mime='text/csv',
        )

else:
    st.error("Terjadi kesalahan saat memproses data.")