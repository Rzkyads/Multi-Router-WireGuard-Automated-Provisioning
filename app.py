import requests
import streamlit as st

st.set_page_config(
    page_title="Cyaneum WGC",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "http://127.0.0.1:8000/api/v1"

# Inisialisasi Session State untuk Auth
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- STYLING CSS KUSTOM MODERN OCEAN & DUSK ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0b1329; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Header Utama */
    .main-header { 
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        padding: 1.5rem 2rem; 
        border-bottom: 1px solid #1e293b; 
        border-radius: 12px;
        margin-bottom: 1.5rem; 
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-title { font-size: 1.8rem; font-weight: 700; color: #38bdf8; margin: 0px; letter-spacing: -0.5px; }
    .sub-title { color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }
    
    /* Kartu Kontainer */
    div.stForm, .custom-card { 
        background-color: #111827; 
        border: 1px solid #1f2937; 
        padding: 1.5rem; 
        border-radius: 12px; 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    /* Tombol Utama */
    .stButton>button { 
        background-color: #0284c7; 
        color: white; 
        border-radius: 8px; 
        font-weight: 600; 
        border: none; 
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { 
        background-color: #0369a1; 
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    
    /* Metrik Card Custom */
    .metric-container {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        text-align: left;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #38bdf8; }
    .metric-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
    
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

# ================= HALAMAN LOGIN / REGISTRASI =================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; margin-top: 4rem;'><h1"
            " style='color: #38bdf8; font-size: 2.5rem;'>🌐 Cyaneum WGC</h1><p"
            " style='color: #94a3b8; font-size: 1rem;'>WireGuard Control &"
            " Provisioning System</p></div>",
            unsafe_allow_html=True,
        )

        auth_tab1, auth_tab2 = st.tabs(["🔑 Masuk (Login)", "📝 Registrasi Akun"])

        with auth_tab1:
            with st.form("login_form"):
                l_user = st.text_input("Username")
                l_pass = st.text_input("Password", type="password")
                l_submit = st.form_submit_button("Masuk ke Sistem")

            if l_submit:
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"username": l_user, "password": l_pass},
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.logged_in = True
                        st.session_state.username = data["username"]
                        st.session_state.role = data["role"]
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login gagal."))
                except Exception as e:
                    st.error(f"Koneksi error: {str(e)}")

        with auth_tab2:
            with st.form("register_form"):
                r_user = st.text_input("Buat Username Baru")
                r_pass = st.text_input("Buat Password", type="password")
                r_submit = st.form_submit_button("Daftar Akun")

            if r_submit:
                if not r_user or not r_pass:
                    st.error("Username dan password wajib diisi.")
                else:
                    try:
                        res = requests.post(
                            f"{API_BASE}/auth/register",
                            json={"username": r_user, "password": r_pass},
                        )
                        if res.status_code == 200:
                            st.success(res.json().get("message"))
                        else:
                            st.error(res.json().get("detail", "Registrasi gagal."))
                    except Exception as e:
                        st.error(f"Koneksi error: {str(e)}")
    st.stop()


# ================= AMBIL DATA API AWAL =================
try:
    routers_res = requests.get(f"{API_BASE}/routers")
    routers = routers_res.json() if routers_res.status_code == 200 else []
except:
    routers = []

try:
    clients_res = requests.get(f"{API_BASE}/wg/clients")
    clients = clients_res.json() if clients_res.status_code == 200 else []
except:
    clients = []

router_options = {r["router_name"]: r["id"] for r in routers}


# ================= DASHBOARD UTAMA =================
st.markdown(
    f"""
    <div class="main-header">
        <div>
            <p class="main-title">🌐 Cyaneum WGC</p>
            <p class="sub-title">WireGuard Control & Provisioning System</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="text-align: right;">
                <span style="color: #38bdf8; font-weight: 600; display: block;">👤 {st.session_state.username}</span> 
                <span style="background: #1e293b; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; color: #94a3b8; border: 1px solid #334155;">{st.session_state.role.upper()}</span>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Tombol Logout di sidebar kecil
if st.sidebar.button("🚪 Keluar (Logout)") :
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# Navigasi Tab Utama
tabs_list = [
    "🚀 Provisioning Klien",
    "⚙️ Manajemen Router",
    "👥 Manajemen User",
    "📜 Audit Log",
]
tabs = st.tabs(tabs_list)

tab_provision = tabs[0]
tab_router = tabs[1]
tab_user_mgmt = tabs[2]
tab_logs = tabs[3]

# --- TAB 1: PROVISIONING KLIEN ---
with tab_provision:
    # Baris Ringkasan Metrik Atas
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""<div class="metric-container"><div class="metric-label">Total Klien Aktif</div><div class="metric-value">{len(clients)}</div></div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""<div class="metric-container"><div class="metric-label">Total Router Terdaftar</div><div class="metric-value">{len(routers)}</div></div>""",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""<div class="metric-container"><div class="metric-label">Subnet Pool</div><div class="metric-value" style="font-size: 1.2rem; margin-top: 5px;">10.10.0.0/24</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.3], gap="large")

    with col_left:
        st.markdown("### ➕ Tambah Klien VPN Baru")
        if not router_options:
            st.warning(
                "⚠️ Belum ada router MikroTik terdaftar. Tambahkan di tab Manajemen Router terlebih dahulu."
            )
        else:
            with st.form("provision_form"):
                selected_router_name = st.selectbox(
                    "Pilih Router MikroTik Tujuan",
                    options=list(router_options.keys()),
                )
                client_name = st.text_input(
                    "Nama Klien / Perangkat", placeholder="Contoh: vpn-laptop-budi"
                )
                private_key = st.text_input(
                    "WireGuard Private Key",
                    type="password",
                    placeholder="Masukkan 44-char private key",
                )
                submitted = st.form_submit_button("🚀 Generate & Provision ke Router")

            if submitted:
                if not client_name or not private_key:
                    st.error("Nama klien dan Private Key wajib diisi!")
                else:
                    payload = {
                        "client_name": client_name,
                        "private_key": private_key,
                        "router_id": router_options[selected_router_name],
                    }
                    res = requests.post(f"{API_BASE}/wg/generate", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(
                            f"Berhasil diprovision ke {selected_router_name}! IP: {data['client_ip']}"
                        )
                        st.code(data["config_text"], language="ini")
                    else:
                        st.error(res.json().get("detail", "Gagal memproses provisioning."))

    with col_right:
        st.markdown("### 📊 Daftar Klien Aktif Terdaftar")
        if clients:
            for c in clients:
                r_name = next(
                    (r["router_name"] for r in routers if r["id"] == c["router_id"]),
                    "Unknown",
                )
                st.markdown(
                    f"""
                    <div style="background: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.05rem; color: #f8fafc;">{c['client_name']}</strong><br>
                            <span style="color: #38bdf8; font-size: 0.85rem;">IP: {c['allocated_ip']}</span> &nbsp;|&nbsp; 
                            <span style="color: #94a3b8; font-size: 0.85rem;">Gateway: {r_name}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Tombol aksi terpisah agar tata letak rapi
                if st.button("🗑️ Revoke Klien", key=f"del_{c['id']}"):
                    requests.delete(f"{API_BASE}/wg/clients/{c['id']}")
                    st.rerun()
        else:
            st.info("Belum ada klien VPN aktif yang terdaftar di database.")

# --- TAB 2: MANAJEMEN ROUTER ---
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
            r_port = st.number_input("API Port RouterOS", value=8728)
            r_user = st.text_input("API Username", value="admin")
            r_pass = st.text_input("API Password", type="password")
            r_iface = st.text_input("Interface WireGuard", value="wg0")
            r_submit = st.form_submit_button("💾 Simpan Konfigurasi Router")
        if r_submit:
            payload = {
                "router_name": r_name,
                "host": r_host,
                "port": r_port,
                "username": r_user,
                "password": r_pass,
                "wg_interface": r_iface,
            }
            res = requests.post(f"{API_BASE}/routers", json=payload)
            if res.status_code == 200:
                st.success("Router berhasil disimpan!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Gagal menyimpan router."))

    with col_r2:
        st.markdown("### 🌐 Armada Router Aktif")
        if routers:
            for r in routers:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: #111827; border: 1px solid #1f2937; padding: 1.2rem; border-radius: 8px; margin-bottom: 0.75rem;">
                            <h4 style="margin: 0 0 5px 0; color: #38bdf8;">🖧 {r['router_name']}</h4>
                            <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">IP: <code>{r['host']}:{r['port']}</code> | Interface: <code>{r['wg_interface']}</code></p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        f"🗑️ Hapus Router {r['router_name']}", key=f"del_r_{r['id']}"
                    ):
                        requests.delete(f"{API_BASE}/routers/{r['id']}")
                        st.rerun()
        else:
            st.info("Belum ada armada router MikroTik yang terdaftar.")

# --- TAB 3: MANAJEMEN USER ---
with tab_user_mgmt:
    st.markdown("### 👥 Manajemen Pengguna & Approval Akun")
    if st.session_state.role != "root":
        st.warning("⚠️ Anda harus masuk sebagai Root Admin untuk mengakses menu ini.")
    else:
        users_res = requests.get(f"{API_BASE}/users")
        all_users = users_res.json() if users_res.status_code == 200 else []

        for u in all_users:
            with st.container():
                uc1, uc2, uc3 = st.columns([2, 2, 2])
                with uc1:
                    st.markdown(f"**{u['username']}**")
                    st.caption(f"Role: `{u['role']}`")
                with uc2:
                    status_badge = (
                        "🟢 **Approved**" if u["is_approved"] else "🟡 **Pending**"
                    )
                    st.markdown(status_badge)
                with uc3:
                    if not u["is_approved"]:
                        if st.button("✅ Approve", key=f"app_{u['id']}"):
                            requests.put(f"{API_BASE}/users/{u['id']}/approve")
                            st.rerun()
                    if u["role"] != "root":
                        if st.button("🗑️ Hapus", key=f"del_u_{u['id']}"):
                            requests.delete(f"{API_BASE}/users/{u['id']}")
                            st.rerun()
                st.markdown(
                    "<hr style='margin: 0.5rem 0px; border-color: #1e293b;'>",
                    unsafe_allow_html=True,
                )

# --- TAB 4: AUDIT LOG ---
with tab_logs:
    st.markdown("### 📜 Sistem Audit Log Aktivitas")
    if st.button("🔄 Refresh Log"):
        st.rerun()

    logs_res = requests.get(f"{API_BASE}/audit-logs")
    logs = logs_res.json() if logs_res.status_code == 200 else []

    if logs:
        for log in logs:
            st.markdown(
                f"- `[{log['timestamp']}]` **{log['username']}** —"
                f" `[{log['action']}]`: _{log['details']}_"
            )
    else:
        st.info("Belum ada catatan aktivitas log.")
