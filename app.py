import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import math
import streamlit as st
st.markdown("""
    <style>
    /* Mengubah warna latar belakang aplikasi */
    .stApp {
        background-color: #f4f6f9;
    }
    /* Mengubah gaya box sidebar */
    [data-testid="stSidebar"] {
        background-color: #e3e8ee;
    }
    /* Mengubah warna teks judul utama */
    h1 {
        color: #1b4332;
    }
    </style>
""", unsafe_allow_html=True)
import math
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Kalkulator JPH - Bina Marga 2021",
    page_icon="🛣️",
    layout="wide",
)

# =========================================================
# 2. JUDUL DAN HEADER APLIKASI
# =========================================================
st.title("🛣️ Kalkulator Jarak Pandang Henti (JPH)")
st.caption(
    "Aplikasi Perhitungan Geometri Jalan Berdasarkan **Pedoman Desain Geometrik"
    " Jalan (Bina Marga 2021)**"
)

st.markdown("---")

# =========================================================
# 3. ANTAARMUKA INPUT (SIDEBAR STREAMLIT)
# =========================================================
st.sidebar.header("📋 Parameter Perencanaan")

# Input Kecepatan Rencana (VR)
vr = st.sidebar.number_input(
    "Kecepatan Rencana / Desain (VR) [km/jam]",
    min_value=20,
    max_value=120,
    value=80,
    step=5,
    help="Kecepatan target operasional kendaraan pada ruas jalan",
)

# Input Kelandaian Jalan (G)
g_percent = st.sidebar.number_input(
    "Kelandaian Jalan (G) [%]",
    min_value=-15.0,
    max_value=15.0,
    value=-0.63,
    step=0.1,
    format="%.2f",
    help=(
        "Nilai (-) untuk jalan menurun, (+) untuk jalan menanjak, 0% untuk"
        " datar"
    ),
)

# Input Jarak Pandang Lapangan (Opsional)
jph_lapangan = st.sidebar.number_input(
    "Jarak Pandang Eksisting Lapangan (m) [Opsional]",
    min_value=0.0,
    value=150.0,
    step=5.0,
    help="Jarak pandang bebas aktual di lokasi fisik lapangan",
)

# Expander Parameter Standar Bina Marga 2021
with st.sidebar.expander("⚙️ Parameter Standar Bina Marga 2021"):
  t_reaksi = st.number_input(
      "Waktu Tanggap / Reaksi (t) [detik]",
      min_value=1.0,
      max_value=5.0,
      value=2.5,
      step=0.1,
  )
  a_decel = st.number_input(
      "Tingkat Perlambatan (a) [m/detik²]",
      min_value=1.0,
      max_value=10.0,
      value=3.4,
      step=0.1,
  )
  g_grav = 9.81

# =========================================================
# 4. LOGIKA PERHITUNGAN (RUMUS BINA MARGA 2021)
# =========================================================
# Konversi kelandaian ke desimal
g_decimal = g_percent / 100.0

# Jarak Tanggap Reaksi (Jht)
jht = 0.278 * vr * t_reaksi

# Faktor Gesekan Ekuivalen (f_eq = a / g)
f_eq = a_decel / g_grav

# Penyebut rumus pengereman
denom = f_eq + g_decimal

# Penanganan Error jika kelandaian turunan terlalu ekstrem
if denom <= 0:
  st.error(
      "⚠️ **Peringatan Bahaya:** Kombinasi kelandaian turunan terlalu curam"
      " melebihi batas koefisien gesek! Kendaraan tidak dapat berhenti secara"
      " teoritis."
  )
  st.stop()

# Jarak Pengereman (Jhf)
jhf = (vr**2) / (254 * denom)

# Total JPH
jph_total = jht + jhf
jph_pembulatan = math.ceil(jph_total)

# =========================================================
# 5. TAMPILAN HASIL & METRIK UTAMA
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
  st.metric(
      label="1. Jarak Tanggap (Jht)",
      value=f"{jht:.2f} m",
      delta=f"Waktu Reaksi: {t_reaksi}s",
      delta_color="off",
  )

with col2:
  st.metric(
      label="2. Jarak Pengereman (Jhf)",
      value=f"{jhf:.2f} m",
      delta=f"Kelandaian: {g_percent:+.2f}%",
      delta_color="off",
  )

with col3:
  st.metric(
      label="3. Total JPH Desain",
      value=f"{jph_total:.2f} m",
      delta=f"Dibulatkan: {jph_pembulatan} m",
  )

st.markdown("---")

# =========================================================
# 6. EVALUASI KEAMANAN & VISUALISASI GRAFIK
# =========================================================
col_eval1, col_eval2 = st.columns([1, 1])

with col_eval1:
  st.subheader("🛡️ Evaluasi Keamanan Lokasi")
  if jph_lapangan >= jph_total:
    st.success(f"""
        ### **DESAIN AMAN**  
        * **Jarak Pandang Lapangan:** {jph_lapangan:.2f} m  
        * **JPH Desain Minimum:** {jph_total:.2f} m  
        * **Kelebihan Jarak Aman:** +{jph_lapangan - jph_total:.2f} m  
        
        Kondisi ruang bebas pandang di lokasi memenuhi syarat pengereman kendaraan.
        """)
  else:
    st.error(f"""
        ### **TIDAK AMAN**  
        * **Jarak Pandang Lapangan:** {jph_lapangan:.2f} m  
        * **JPH Desain Minimum:** {jph_total:.2f} m  
        * **Kekurangan Jarak:** -{jph_total - jph_lapangan:.2f} m  
        
        **Rekomendasi Penanganan Teknis:**  
        1. Pembersihan tebing atau penghalang visual di bahu/ruang bebas samping jalan.  
        2. Penurunan batas Kecepatan Rencana ($V_R$) pada segmen jalan ini.  
        3. Pemasangan rambu peringatan dini sebelum titik bahaya.
        """)

with col_eval2:
  st.subheader("📊 Grafik Komposisi JPH")
  fig, ax = plt.subplots(figsize=(6, 2.8))
  ax.barh(
      ["JPH Desain"], [jht], color="#2E7D32", label=f"Jht (Reaksi): {jht:.1f} m"
  )
  ax.barh(
      ["JPH Desain"],
      [jhf],
      left=[jht],
      color="#E65100",
      label=f"Jhf (Rem): {jhf:.1f} m",
  )

  ax.set_xlabel("Jarak (meter)")
  max_x = max(jph_total * 1.25, jph_lapangan * 1.15)
  ax.set_xlim(0, max_x)

  # Garis pembanding batas lapangan
  ax.axvline(
      x=jph_lapangan,
      color="red",
      linestyle="--",
      linewidth=2,
      label=f"Batas Lapangan ({jph_lapangan:.0f} m)",
  )

  ax.legend(loc="upper right", fontsize=8)
  plt.tight_layout()
  st.pyplot(fig)

st.markdown("---")

# =========================================================
# 7. REFERENSI DATA & TEORI
# =========================================================
st.subheader("📚 Tabel Referensi Bina Marga 2021 (Tabel 5-11)")
st.caption(
    "JPH Mobil Penumpang pada Berbagai Kondisi Kelandaian Jalan (PDGJ No."
    " 13/P/BM/2021)"
)

ref_data = {
    "VR (km/jam)": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    "Jht (m)": [13.9, 20.9, 27.8, 34.8, 41.7, 48.7, 55.6, 62.6, 69.5, 76.5, 83.4],
    "Datar (0%) [m]": [20, 35, 50, 65, 85, 105, 130, 160, 185, 220, 250],
    "Menurun (-3%) [m]": [20, 33, 49, 68, 89, 113, 140, 169, 201, 236, 273],
    "Menurun (-6%) [m]": [20, 34, 52, 72, 95, 120, 149, 181, 216, 253, 294],
    "Menanjak (+3%) [m]": [19, 31, 46, 63, 81, 103, 126, 151, 179, 209, 241],
    "Menanjak (+6%) [m]": [18, 30, 44, 60, 78, 99, 121, 145, 171, 199, 229],
}

df_ref = pd.DataFrame(ref_data)
st.dataframe(df_ref, use_container_width=True)

with st.expander("📖 Dasar Teori & Rumus Perhitungan"):
  st.write("**1. Total Jarak Pandang Henti ($JPH$):**")
  st.latex(r"JPH = J_{ht} + J_{hf}")

  st.write("**2. Jarak Tanggap Reaksi ($J_{ht}$):**")
  st.latex(r"J_{ht} = 0.278 \times V_R \times t")

  st.write("**3. Jarak Pengereman ($J_{hf}$):**")
  st.latex(
      r"J_{hf} = \frac{V_R^2}{254 \times \left(\frac{a}{9.81} \pm G\right)}"
  )

  st.markdown("""
    **Keterangan Variabel:**
    * **$V_R$** = Kecepatan Rencana / Desain ($\text{km/jam}$)
    * **$t$** = Waktu tanggap reaksi pengemudi ($2.5 \text{ detik}$)
    * **$a$** = Tingkat perlambatan kendaraan ($3.4 \text{ m/s}^2$)
    * **$9.81$** = Percepatan gravitasi ($\text{m/s}^2$)
    * **$G$** = Kelandaian jalan dalam desimal ($G = \% / 100$)
    """)
