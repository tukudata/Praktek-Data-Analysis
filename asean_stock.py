import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="ASEAN Index Tracker", layout="wide")

st.title("📈 ASEAN Composite Index Performance (Last 5 Years)")
st.markdown("Membandingkan performa indeks harga saham gabungan negara-negara ASEAN.")

# --- 1. DAFTAR TICKER INDEKS ---
asean_map = {
    "Indonesia (IHSG)": "^JKSE",
    "Singapore (STI)": "^STI",
    "Malaysia (KLCI)": "^KLSE",
    "Thailand (SET)": "SET.BK",
    "Philippines (PSEi)": "^PSEI",
    "Vietnam (VN-Index)": "^VNINDEX"
}

# --- 2. FUNGSI AMBIL DATA ---
@st.cache_data
def get_stock_data():
    tickers = list(asean_map.values())
    # Mengambil data 5 tahun terakhir
    df = yf.download(tickers, period="5y")['Close']
    
    # Mapping nama kolom dari ticker ke nama negara
    inv_map = {v: k for k, v in asean_map.items()}
    df = df.rename(columns=inv_map)
    return df

try:
    data = get_stock_data()
    
    # --- 3. PERHITUNGAN PERSENTASE ---
    # Menghitung persentase perubahan total dari awal periode hingga sekarang
    first_price = data.iloc[0]
    last_price = data.iloc[-1]
    total_change = ((last_price - first_price) / first_price * 100).round(2)

    # --- 4. NORMALISASI DATA (Base 100) ---
    # Agar perbandingan apel-ke-apel, semua mulai dari angka 100
    data_norm = (data / data.iloc[0] * 100).round(2)

    # --- 5. TAMPILAN KPI (Persentase Kenaikan/Penurunan) ---
    st.subheader("🚀 Total Growth (5 Years)")
    cols = st.columns(len(total_change))
    
    for i, (country, pct) in enumerate(total_change.items()):
        cols[i].metric(label=country, value=f"{pct}%", delta=f"{pct}%")

    st.divider()

    # --- 6. VISUALISASI PLOTLY (Interaktif) ---
    st.subheader("📉 Normalized Growth Chart (Base 100)")
    st.caption("Semua indeks diset ke angka 100 pada awal periode untuk melihat pertumbuhan murni.")

    fig = go.Figure()

    for country in data_norm.columns:
        fig.add_trace(go.Scatter(
            x=data_norm.index, 
            y=data_norm[country],
            mode='lines',
            name=country,
            hovertemplate=f"<b>{country}</b><br>Growth: %{{y}}%<extra></extra>"
        ))

    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Tahun",
        yaxis_title="Growth % (Base 100)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. TABEL DATA MENTAH ---
    with st.expander("Lihat Harga Penutupan Terakhir (Raw Data)"):
        st.write(data.tail(10))

except Exception as e:
    st.error(f"Gagal mengambil data dari Yahoo Finance. Pastikan koneksi internet aktif. Error: {e}")