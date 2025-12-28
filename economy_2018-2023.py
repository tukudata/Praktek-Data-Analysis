import streamlit as st
import pandas as pd
import wbgapi as wb
import plotly.express as px

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="World Economic Growth", layout="wide")

st.title("🌎 Pertumbuhan Ekonomi Dunia (5 Tahun Terakhir)")
st.markdown("""
Data ini diambil langsung dari **World Bank API**. 
Indikator yang digunakan: *GDP per capita growth (annual %)*.
""")

# --- 1. IDENTIFIKASI KODE WILAYAH ---
# Kita akan mengambil grup wilayah besar agar grafik tidak terlalu penuh
regions = {
    'WLD': 'Dunia (Rata-rata)',
    'EAS': 'Asia Timur & Pasifik',
    'ECS': 'Eropa & Asia Tengah',
    'LCN': 'Amerika Latin & Karibia',
    'MEA': 'Timur Tengah & Afrika Utara',
    'NAC': 'Amerika Utara',
    'SAS': 'Asia Selatan',
    'SSF': 'Afrika Sub-Sahara'
}

@st.cache_data
def load_economy_data():
    # Mengambil data 5 tahun terakhir (misal: 2018-2023 karena data 2024-2025 sering belum lengkap)
    # NY.GDP.PCAP.KD.ZG = GDP per capita growth (annual %)
    df = wb.data.DataFrame('NY.GDP.PCAP.KD.ZG', list(regions.keys()), time=range(2018, 2024), labels=True)
    return df

try:
    df = load_economy_data()
    
    # --- 2. DATA CLEANING ---
    # Memutar tabel (Reshape) agar cocok untuk Plotly
    df_melted = df.melt(id_vars='Country', var_name='Tahun', value_name='Pertumbuhan (%)')
    df_melted['Tahun'] = df_melted['Tahun'].str.replace('YR', '') # Membersihkan format tahun 'YR2018' -> '2018'
    df_melted = df_melted.sort_values(['Country', 'Tahun'])

    # --- 3. VISUALISASI INTERAKTIF ---
    st.subheader("📉 Grafik Pertumbuhan PDB Tahunan (%)")
    
    fig = px.line(
        df_melted, 
        x='Tahun', 
        y='Pertumbuhan (%)', 
        color='Country',
        markers=True,
        title="Tren Pertumbuhan Ekonomi per Wilayah",
        labels={'Country': 'Wilayah'}
    )

    # Menambah garis nol untuk membedakan pertumbuhan (+) dan resesi (-)
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Titik Resesi")
    
    fig.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # --- 4. TABEL ANALISIS ---
    st.subheader("📋 Data Perbandingan Wilayah")
    
    # Menghitung rata-rata pertumbuhan selama 5 tahun
    avg_growth = df_melted.groupby('Country')['Pertumbuhan (%)'].mean().reset_index()
    avg_growth.columns = ['Wilayah', 'Rata-rata Pertumbuhan 5 Thn (%)']
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        st.write("Top Wilayah Berdasarkan Rata-rata Pertumbuhan:")
        st.table(avg_growth.sort_values(by='Rata-rata Pertumbuhan 5 Thn (%)', ascending=False))

except Exception as e:
    st.error(f"Gagal mengambil data dari World Bank. Pesan: {e}")