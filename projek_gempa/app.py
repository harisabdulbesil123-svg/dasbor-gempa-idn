import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
from streamlit_option_menu import option_menu
import os # Modul mutlak untuk membaca file sistem (gambar lokal)

st.set_page_config(page_title="Pusat Analisis Gempa", layout="wide")

# ==========================================
# FUNGSI PEMBACA BATAS NEGARA & LAYER SATELIT
# ==========================================
@st.cache_data
def muat_batas_negara():
    try:
        with open("batas_indonesia.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

batas_indo = muat_batas_negara()

def dapatkan_layer_peta():
    layer = [{
        "below": 'traces',
        "sourcetype": "raster",
        "sourceattribution": "Citra Satelit",
        "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
    }]
    if batas_indo:
        layer.append({
            "sourcetype": "geojson",
            "source": batas_indo,
            "type": "line",
            "color": "yellow",
            "line": {"width": 1.5}
        })
    return layer

# ==========================================
# FUNGSI PEMBACA DATA HISTORIS LOKAL
# ==========================================
@st.cache_data
def ambil_data_historis_lokal():
    try:
        with open("gempa_historis.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        fitur = data['features']
        data_rapi = []
        for f in fitur:
            properti = f['properties']
            geometri = f['geometry']
            data_rapi.append({
                "Lokasi": properti['place'],
                "Magnitudo": properti['mag'],
                "Waktu": pd.to_datetime(properti['time'], unit='ms'),
                "Potensi Tsunami": "Ya" if properti['tsunami'] == 1 else "Tidak",
                "longitude": geometri['coordinates'][0],
                "latitude": geometri['coordinates'][1]
            })
        return pd.DataFrame(data_rapi)
    except FileNotFoundError:
        return pd.DataFrame()

df_historis = ambil_data_historis_lokal()

if not df_historis.empty:
    df_historis['radius_visual'] = df_historis['Magnitudo'] * 10

# ==========================================
# SIDEBAR (NAVIGASI BRUTALIST)
# ==========================================
with st.sidebar:
    st.title("SISTEM NAVIGASI")
    pilihan = option_menu(
        menu_title=None,
        options=["Beranda", "Gempa Terkini", "Analisis Historis"],
        icons=["", "", ""],
        menu_icon="",
        default_index=0, 
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"display": "none"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "4px 0px", "padding": "12px", "border-radius": "0px", "--hover-color": "#222222"},
            "nav-link-selected": {"background-color": "#8B0000", "font-weight": "bold", "color": "white"}
        }
    )
    
    st.markdown("---")
    st.subheader("Pengaturan Visual")
    tipe_peta = st.radio("Mode Peta:", ["Satelit Resolusi Tinggi", "Peta Jalan Standar"])
    map_style = "satellite" if tipe_peta == "Satelit Resolusi Tinggi" else "open-street-map"


# ==========================================
# HALAMAN 1: BERANDA 
# ==========================================
if pilihan == "Beranda":
    st.title("Pusat Informasi dan Dasbor Analisis Gempa Bumi")
    st.write("Sistem pemantauan geospasial dan edukasi mitigasi bencana untuk wilayah kepulauan Indonesia.")
    st.markdown("---")
    
    st.subheader("Statistik Historis (2020 - 2026)")
    
    if not df_historis.empty:
        total_gempa = len(df_historis)
        rata_rata_mag = df_historis['Magnitudo'].mean()
        max_mag = df_historis['Magnitudo'].max()
    else:
        total_gempa = 0
        rata_rata_mag = 0.0
        max_mag = 0.0

    metrik1, metrik2, metrik3 = st.columns(3)
    metrik1.metric(label="Total Gempa Terdata", value=f"{total_gempa} Kejadian", delta="Data USGS")
    metrik2.metric(label="Rata-Rata Magnitudo", value=f"{rata_rata_mag:.2f} SR", delta="Batas Min. 6.0", delta_color="off")
    metrik3.metric(label="Magnitudo Terbesar", value=f"{max_mag} SR", delta="Puncak Kerusakan", delta_color="inverse")
    
    st.markdown("---")
    
    st.subheader("Kawasan Sabuk Sirkum-Pasifik (Ring of Fire)")
    kolom_rof_kiri, kolom_rof_kanan = st.columns([1, 1])
    
    with kolom_rof_kiri:
        # LOGIKA PERTAHANAN GAMBAR LOKAL: Cek apakah file fisik ring_of_fire.jpg ada
        jalur_gambar = "ring_of_fire.jpg"
        if os.path.exists(jalur_gambar):
            # Parameter use_column_width telah dibakar dan diganti menjadi use_container_width
            st.image(jalur_gambar, caption="Peta Kawasan Cincin Api", use_container_width=True)
        else:
            # Jika kamu lupa menaruh gambar, kode tidak error, melainkan memunculkan peringatan ini
            st.warning("⚠️ SISTEM: File 'ring_of_fire.jpg' tidak ditemukan. Silakan unduh gambar Ring of Fire dan simpan di folder proyek Anda.")
        
    with kolom_rof_kanan:
        st.markdown("<h4 style='color: #8B0000; margin-top: 0;'>INDONESIA ADALAH ZONA KUNCI</h4>", unsafe_allow_html=True)
        st.write("**Apa itu Ring of Fire?**")
        st.write("Cincin Api Pasifik adalah jalur sepanjang 40.000 kilometer yang berbentuk tapal kuda, membentang dari Amerika Selatan, pesisir Amerika Utara, Jepang, hingga ke Indonesia dan Selandia Baru.")
        
        st.write("**Mengapa Ini Mematikan?**")
        st.write("Jalur ini mengunci **75% gunung berapi aktif dunia** dan menjadi lokasi terjadinya **90% gempa bumi** di seluruh planet ini. Ini adalah area di mana lempeng samudera yang berat terus-menerus menunjam ke bawah lempeng benua (Zona Subduksi).")
        
        st.write("**Status Indonesia:**")
        st.info("Indonesia menanggung beban geologis paling ekstrem. Nusantara tidak hanya dilewati oleh Cincin Api Pasifik di bagian timur, tetapi juga bertabrakan langsung dengan **Sabuk Alpide** (jalur seismik mematikan kedua di dunia) yang membentang dari barat Sumatera hingga Jawa. Secara harfiah, kita hidup di atas mesin tektonik paling aktif di Bumi.")
    
    st.markdown("---")
    
    kolom_kiri, kolom_kanan = st.columns(2)
    
    with kolom_kiri:
        st.subheader("Mekanisme Tektonik")
        st.write("Bumi tidak solid. Litosfer terpecah menjadi lempeng-lempeng tektonik yang terus bergerak akibat arus konveksi magma di bawahnya. Indonesia berada di titik tumbukan tiga lempeng utama: Indo-Australia, Eurasia, dan Pasifik. Gesekan antar lempeng ini mengakumulasi energi tekanan yang, ketika dilepaskan secara tiba-tiba, menciptakan gelombang seismik mematikan.")
        
        st.subheader("Skala Kerusakan Magnitudo")
        st.markdown("""
        - **Skala < 4.9:** Getaran dirasakan oleh manusia, kerusakan struktural sangat minim.
        - **Skala 5.0 - 5.9:** Kerusakan ringan pada bangunan dengan konstruksi buruk.
        - **Skala 6.0 - 6.9:** Kerusakan parah di area padat penduduk. Dinding runtuh, retakan tanah dangkal.
        - **Skala > 7.0:** Bencana mayor. Menghancurkan fondasi bangunan, memicu likuifaksi, dan berpotensi menghasilkan gelombang Tsunami.
        """)

    with kolom_kanan:
        st.subheader("Protokol Keselamatan Mutlak")
        st.markdown("""
        **1. DROP (MERUNDUK):** Segera jatuhkan tubuh ke lantai sebelum guncangan menjatuhkan Anda.
        
        **2. COVER (BERLINDUNG):** Berlindung di bawah struktur furnitur yang sangat kokoh. Lindungi area leher dan kepala.
        
        **3. HOLD ON (BERTAHAN):** Cengkeram kaki meja atau tempat Anda berlindung. Jangan keluar ruangan sampai guncangan benar-benar berhenti.
        """)
        
        st.subheader("Integritas Data")
        st.write("Semua lapisan data dalam sistem ini bersifat objektif dan tidak dimodifikasi:")
        st.write("1. Data Real-time ditarik dari sensor BMKG (Badan Meteorologi, Klimatologi, dan Geofisika).")
        st.write("2. Data Historis spasial ditarik dari USGS (United States Geological Survey).")


# ==========================================
# HALAMAN 2: GEMPA TERKINI 
# ==========================================
elif pilihan == "Gempa Terkini":
    st.title("Data Observasi Gempa Terkini")
    st.write("Menampilkan 5 aktivitas seismik terakhir dari jaringan sensor BMKG.")
    
    url_bmkg = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
    
    try:
        respon = requests.get(url_bmkg, timeout=10)
        
        if respon.status_code == 200:
            data_gempa = respon.json()
            daftar_gempa = data_gempa["Infogempa"]["gempa"][:5] 
            
            for gempa in daftar_gempa:
                with st.expander(f"TANGGAL: {gempa['Tanggal']} | MAGNITUDO: {gempa['Magnitude']} | LOKASI: {gempa['Wilayah']}"):
                    kolom_teks, kolom_peta = st.columns([1, 2])
                    
                    with kolom_teks:
                        st.write(f"**Waktu Observasi:** {gempa['Jam']}")
                        st.write(f"**Status Tsunami:** {gempa['Potensi']}")
                        st.write(f"**Kedalaman Hiposenter:** {gempa['Kedalaman']}")
                        st.write(f"**Titik Koordinat:** {gempa['Coordinates']}")
                    
                    with kolom_peta:
                        kordinat_mentah = gempa["Coordinates"] 
                        lintang, bujur = kordinat_mentah.split(",")
                        
                        df_peta = pd.DataFrame({
                            "latitude": [float(lintang)],
                            "longitude": [float(bujur)],
                            "radius_visual": [float(gempa['Magnitude']) * 10]
                        })
                        
                        peta_bmkg = px.scatter_mapbox(
                            df_peta, lat="latitude", lon="longitude", size="radius_visual",
                            size_max=40, zoom=5, color_discrete_sequence=["red"], opacity=0.5
                        )
                        
                        if map_style == "satellite":
                            peta_bmkg.update_layout(mapbox_style="white-bg", mapbox_layers=dapatkan_layer_peta(), margin={"r":0,"t":0,"l":0,"b":0})
                        else:
                            peta_bmkg.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                            
                        st.plotly_chart(peta_bmkg, use_container_width=True)
        else:
            st.error("Kegagalan API BMKG: Status kode tidak valid.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"KEGAGALAN SISTEM: Koneksi internet terputus atau server tujuan tidak merespons.\nLog: {e}")


# ==========================================
# HALAMAN 3: ANALISIS HISTORIS
# ==========================================
elif pilihan == "Analisis Historis":
    st.title("Dasbor Analisis Historis (2020 - 2026)")
    
    if not df_historis.empty:
        kolom_filter1, kolom_filter2 = st.columns(2)
        with kolom_filter1:
            df_historis['Tahun'] = df_historis['Waktu'].dt.year
            daftar_tahun = sorted(df_historis['Tahun'].unique().tolist())
            pilih_tahun = st.multiselect("Filter Tahun Kejadian:", daftar_tahun, default=daftar_tahun)
        with kolom_filter2:
            pilih_mag = st.slider("Filter Minimal Magnitudo:", 6.0, 9.0, 6.0)

        df_filter = df_historis[(df_historis['Tahun'].isin(pilih_tahun)) & (df_historis['Magnitudo'] >= pilih_mag)]

        if df_filter.empty:
            st.warning("Tidak ada data gempa yang memenuhi kriteria filter Anda.")
        else:
            st.markdown("---")
            st.subheader("Analisis Frekuensi dan Proporsi")
            kolom_grafik1, kolom_grafik2 = st.columns(2)
            
            with kolom_grafik1:
                df_filter['Periode'] = df_filter['Waktu'].dt.strftime('%Y-%m')
                hitung_periode = df_filter['Periode'].value_counts().reset_index()
                hitung_periode.columns = ['Periode', 'Jumlah Kejadian']
                hitung_periode = hitung_periode.sort_values('Periode')
                
                grafik_bar = px.bar(
                    hitung_periode, x='Periode', y='Jumlah Kejadian', 
                    title="Tren Jumlah Gempa per Bulan",
                    template="plotly_dark", color_discrete_sequence=["#8B0000"]
                )
                st.plotly_chart(grafik_bar, use_container_width=True)

            with kolom_grafik2:
                hitung_mag = df_filter['Magnitudo'].value_counts().reset_index()
                hitung_mag.columns = ['Magnitudo', 'Jumlah Kejadian']
                hitung_mag['Magnitudo'] = hitung_mag['Magnitudo'].astype(str) + " SR"
                
                grafik_pie = px.pie(
                    hitung_mag, names='Magnitudo', values='Jumlah Kejadian', 
                    title="Proporsi Skala Magnitudo", template="plotly_dark", hole=0.4
                )
                st.plotly_chart(grafik_pie, use_container_width=True)

            st.markdown("---")
            st.subheader("Tabel Perekaman Data")
            
            tabel_interaktif = st.dataframe(
                df_filter[['Waktu', 'Lokasi', 'Magnitudo', 'Potensi Tsunami', 'latitude', 'longitude']],
                selection_mode="single-row", 
                on_select="rerun",
                use_container_width=True
            )

            center_lat, center_lon = -2.5, 118.0
            zoom_level = 3.5

            if len(tabel_interaktif.selection.rows) > 0:
                idx = tabel_interaktif.selection.rows[0]
                target_data = df_filter.iloc[idx]
                center_lat, center_lon = target_data['latitude'], target_data['longitude']
                zoom_level = 7

            st.subheader("Pemetaan Spasial")
            
            peta = px.scatter_mapbox(
                df_filter, lat="latitude", lon="longitude", hover_name="Lokasi",
                size="radius_visual", size_max=40, opacity=0.5,
                color_discrete_sequence=["red"], zoom=zoom_level,
                center={"lat": center_lat, "lon": center_lon}, height=500
            )
            
            if map_style == "satellite":
                peta.update_layout(mapbox_style="white-bg", mapbox_layers=dapatkan_layer_peta(), margin={"r":0,"t":0,"l":0,"b":0})
            else:
                peta.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                
            st.plotly_chart(peta, use_container_width=True)

    else:
        st.error("Database 'gempa_historis.json' tidak ditemukan atau kosong. Analisis tidak dapat dijalankan.")
