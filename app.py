import requests
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Cyaneum WireGuard NCM",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Kustomisasi CSS untuk Tampilan Elegan, Minimalis ala Cyaneum Ocean-Dusk
st.markdown(
    """
    <style>
    /* Global Styling */
    .stApp {
        background-color: #0b1329;
        color: #f8fafc;
    }
    
    /* Header Utama */
    .main-header {
        padding: 1.5rem 0rem 1rem 0rem;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4px;
    }

    /* Container Card Styling */
    div.stForm, div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Styling Tombol */
    .stButton>button {
        width: 100%;
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0369a1;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.4);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header & Branding
st.markdown(
    """
    <div class="main-header">
        <p class="main-title">🌐 Cyaneum Network Management</p>
        <p class="sub-title">Multi-Router WireGuard Automated Provisioning & Client Dashboard</p>
    </div>
""",
    unsafe_allow_html=True,
)

API_BASE = "http://127.0.0.1:8000/api/v1"

# Navigasi Tab Utama
tab_provision, tab_router = st.tabs(
    ["🚀 Provisioning Klien", "⚙️ Manajemen Router MikroTik"]
)

# ================= TAB 1: PROVISIONING KLIEN =================
with tab_provision:
  col_left, col_right = st.columns([1, 1.2], gap="large")

  # Ambil data router untuk dropdown
  try:
    routers_res = requests.get(f"{API_BASE}/routers")
    routers = routers_res.json() if routers_res.status_code == 200 else []
  except:
    routers = []

  router_options = {r["router_name"]: r["id"] for r in routers}

  with col_left:
    st.markdown("### ➕ Tambah Klien VPN Baru")
    if not router_options:
      st.warning(
          "⚠️ Belum ada router MikroTik terdaftar. Silakan tambahkan router di"
          " tab sebelah terlebih dahulu."
      )
    else:
      with st.form("provision_form"):
        selected_router_name = st.selectbox(
            "Pilih Router MikroTik Tujuan",
            options=list(router_options.keys()),
            help="Pilih gateway router tempat peer WireGuard akan didaftarkan.",
        )
        client_name = st.text_input(
            "Nama Klien / Perangkat",
            placeholder="Contoh: vpn-laptop-budi",
        )
        private_key = st.text_input(
            "WireGuard Private Key",
            type="password",
            placeholder="Masukkan 44 karakter Base64 key...",
        )
        submitted = st.form_submit_button(
            "🚀 Generate & Provision ke Router"
        )

      if submitted:
        if not client_name or not private_key:
          st.error("Nama klien dan Private Key wajib diisi!")
        else:
          payload = {
              "client_name": client_name,
              "private_key": private_key,
              "router_id": router_options[selected_router_name],
          }
          try:
            res = requests.post(f"{API_BASE}/wg/generate", json=payload)
            if res.status_code == 200:
              data = res.json()
              st.success(
                  f"Berhasil diprovision ke **{data['router_name']}**! IP:"
                  f" `{data['client_ip']}`"
              )
              st.markdown("#### 📋 Konfigurasi Klien Siap Salin")
              st.code(data["config_text"], language="ini")
            else:
              st.error(
                  f"Gagal: {res.json().get('detail', 'Terjadi kesalahan.')}"
              )
          except Exception as e:
            st.error(f"Koneksi ke backend gagal: {str(e)}")

  with col_right:
    col_title, col_btn = st.columns([2, 1])
    with col_title:
      st.markdown("### 📊 Daftar Klien Aktif")
    with col_btn:
      if st.button("🔄 Refresh"):
        st.rerun()

    try:
      clients_res = requests.get(f"{API_BASE}/wg/clients")
      clients = clients_res.json() if clients_res.status_code == 200 else []
    except:
      clients = []

    if clients:
      for c in clients:
        with st.container():
          rc1, rc2, rc3 = st.columns([2, 1.5, 1])
          with rc1:
            st.markdown(f"**{c['client_name']}**")
            st.caption(f"IP: `{c['allocated_ip']}`")
          with rc2:
            r_name = next(
                (r["router_name"] for r in routers if r["id"] == c["router_id"]),
                "Router Terhapus",
            )
            st.caption(f"Gateway: `{r_name}`")
          with rc3:
            if st.button("Revoke", key=f"del_{c['id']}"):
              del_res = requests.delete(f"{API_BASE}/wg/clients/{c['id']}")
              if del_res.status_code == 200:
                st.success("Dicabut!")
                st.rerun()
              else:
                st.error("Gagal.")
          st.markdown(
              "<hr style='margin: 0.5rem 0px; border-color: #1e293b;'>",
              unsafe_allow_html=True,
          )
    else:
      st.info("Belum ada klien VPN yang terdaftar di database.")


# ================= TAB 2: MANAJEMEN ROUTER =================
with tab_router:
  col_r1, col_r2 = st.columns([1, 1.3], gap="large")

  with col_r1:
    st.markdown("### ⚙️ Registrasi Router MikroTik Baru")
    with st.form("router_form"):
      r_name = st.text_input(
          "Nama Router", placeholder="Contoh: RB5009-HQ-Jakarta"
      )
      r_host = st.text_input(
          "Host / IP Publik Router", placeholder="Contoh: 36.85.12.50"
      )
      r_port = st.number_input(
          "API Port RouterOS", value=8728, step=1, help="Default API port: 8728"
      )
      r_user = st.text_input("API Username", value="admin")
      r_pass = st.text_input("API Password", type="password")
      r_iface = st.text_input(
          "Interface WireGuard",
          value="wg0",
          help="Nama interface WG di MikroTik v7",
      )
      r_submit = st.form_submit_button("💾 Simpan Konfigurasi Router")

    if r_submit:
      if not r_name or not r_host or not r_user:
        st.error("Nama, Host, dan Username wajib diisi!")
      else:
        r_payload = {
            "router_name": r_name,
            "host": r_host,
            "port": r_port,
            "username": r_user,
            "password": r_pass,
            "wg_interface": r_iface,
        }
        try:
          r_res = requests.post(f"{API_BASE}/routers", json=r_payload)
          if r_res.status_code == 200:
            st.success(f"Router **{r_name}** berhasil disimpan!")
            st.rerun()
          else:
            st.error(
                f"Gagal menyimpan: {r_res.json().get('detail', 'Error')}"
            )
        except Exception as e:
          st.error(f"Gagal terhubung ke server: {str(e)}")

  with col_r2:
    rc_title, rc_refresh = st.columns([3, 1])
    with rc_title:
      st.markdown("### 🌐 Armada Router Aktif & Status")
    with rc_refresh:
      if st.button("🔄 Cek Status"):
        st.rerun()

    if routers:
      for r in routers:
        with st.container():
          # Uji koneksi online/offline secara live
          try:
            test_res = requests.post(
                f"{API_BASE}/routers/{r['id']}/test-connection", timeout=4
            )
            status_data = test_res.json()
            is_online = status_data.get("status") == "online"
          except:
            is_online = False

          status_badge = (
              "🟢 **ONLINE**"
              if is_online
              else "🔴 **OFFLINE / TIMEOUT**"
          )

          st.markdown(f"#### 🖧 {r['router_name']} &nbsp;&nbsp; {status_badge}")
          st.caption(
              f"IP: `{r['host']}` | Port API: `{r['port']}` | Interface:"
              f" `{r['wg_interface']}`"
          )

          # Expandable untuk melihat Detail Lengkap Kredensial & Hapus
          with st.expander(f"🔍 Lihat Detail & Kredensial - {r['router_name']}"):
            st.markdown(f"- **Host / IP:** `{r['host']}`")
            st.markdown(f"- **Port API:** `{r['port']}`")
            st.markdown(f"- **Username API:** `{r['username']}`")
            st.markdown(f"- **Password API:** `********`") # Password hidden for UI
            st.markdown(f"- **Interface WireGuard:** `{r['wg_interface']}`")

            if st.button(
                f"🗑️ Hapus Router {r['router_name']}", key=f"del_r_{r['id']}"
            ):
              del_r_res = requests.delete(f"{API_BASE}/routers/{r['id']}")
              if del_r_res.status_code == 200:
                st.success("Router berhasil dihapus.")
                st.rerun()
              else:
                st.error(
                    f"Gagal menghapus: {del_r_res.json().get('detail', 'Error')}"
                )

          st.markdown(
              "<hr style='margin: 0.6rem 0px; border-color: #1e293b;'>",
              unsafe_allow_html=True,
          )
    else:
      st.info(
          "Belum ada router MikroTik yang terdaftar. Tambahkan lewat form di"
          " sebelah kiri."
      )
