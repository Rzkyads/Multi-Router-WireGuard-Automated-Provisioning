import requests
import streamlit as st

st.set_page_config(
    page_title="Cyaneum WireGuard NCM",
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

# Styling CSS Kustom Ocean & Dusk
st.markdown(
    """
    <style>
    .stApp { background-color: #0b1329; color: #f8fafc; }
    .main-header { padding: 1.5rem 0rem 1rem 0rem; border-bottom: 1px solid #1e293b; margin-bottom: 2rem; }
    .main-title { font-size: 2rem; font-weight: 700; color: #38bdf8; margin-bottom: 0px; }
    .sub-title { color: #94a3b8; font-size: 0.95rem; }
    div.stForm { background-color: #111827; border: 1px solid #1f2937; padding: 1.5rem; border-radius: 12px; }
    .stButton>button { width: 100%; background-color: #0284c7; color: white; border-radius: 8px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #0369a1; }
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
            "<div style='text-align: center; margin-top: 3rem;'><h1"
            " style='color: #38bdf8;'>🌐 Cyaneum NCM</h1><p"
            " style='color: #94a3b8;'>Secure WireGuard Management System</p></div>",
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


# ================= DASHBOARD UTAMA (SETELAH LOGIN) =================
st.markdown(
    f"""
    <div class="main-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <p class="main-title">🌐 Cyaneum Network Management</p>
            <p class="sub-title">Multi-Router WireGuard Automated Provisioning & Client Dashboard</p>
        </div>
        <div style="text-align: right;">
            <span style="color: #38bdf8; font-weight: 600;">👤 {st.session_state.username}</span> 
            <span style="background: #1e293b; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; color: #94a3b8;">{st.session_state.role.upper()}</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Tombol Logout di Sidebar/Atas
if st.sidebar.button("🚪 Keluar (Logout)"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# Navigasi Menu Utama (Termasuk Manajemen User & Audit Log)
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

# Ambil data router bersama
try:
    routers_res = requests.get(f"{API_BASE}/routers")
    routers = routers_res.json() if routers_res.status_code == 200 else []
except:
    routers = []
router_options = {r["router_name"]: r["id"] for r in routers}

# --- TAB 1: PROVISIONING KLIEN ---
with tab_provision:
    col_left, col_right = st.columns([1, 1.2], gap="large")
    with col_left:
        st.markdown("### ➕ Tambah Klien VPN Baru")
        if not router_options:
            st.warning(
                "⚠️ Belum ada router MikroTik terdaftar. Tambahkan di tab sebelah."
            )
        else:
            with st.form("provision_form"):
                selected_router_name = st.selectbox(
                    "Pilih Router MikroTik", options=list(router_options.keys())
                )
                client_name = st.text_input(
                    "Nama Klien", placeholder="Contoh: vpn-laptop"
                )
                private_key = st.text_input(
                    "WireGuard Private Key", type="password"
                )
                submitted = st.form_submit_button("🚀 Generate & Provision")
            if submitted:
                if not client_name or not private_key:
                    st.error("Semua field wajib diisi!")
                else:
                    payload = {
                        "client_name": client_name,
                        "private_key": private_key,
                        "router_id": router_options[selected_router_name],
                    }
                    res = requests.post(f"{API_BASE}/wg/generate", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Berhasil diprovision! IP: `{data['client_ip']}`")
                        st.code(data["config_text"], language="ini")
                    else:
                        st.error(res.json().get("detail", "Error"))

    with col_right:
        st.markdown("### 📊 Daftar Klien Aktif")
        clients_res = requests.get(f"{API_BASE}/wg/clients")
        clients = clients_res.json() if clients_res.status_code == 200 else []
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
                            "-",
                        )
                        st.caption(f"Gateway: `{r_name}`")
                    with rc3:
                        if st.button("Revoke", key=f"del_{c['id']}"):
                            requests.delete(f"{API_BASE}/wg/clients/{c['id']}")
                            st.rerun()
                    st.markdown(
                        "<hr style='margin: 0.4rem 0px; border-color: #1e293b;'>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Belum ada klien VPN.")

# --- TAB 2: MANAJEMEN ROUTER ---
with tab_router:
    col_r1, col_r2 = st.columns([1, 1.3], gap="large")
    with col_r1:
        st.markdown("### ⚙️ Registrasi Router Baru")
        with st.form("router_form"):
            r_name = st.text_input("Nama Router")
            r_host = st.text_input("IP Publik / Host")
            r_port = st.number_input("API Port", value=8728)
            r_user = st.text_input("API Username", value="admin")
            r_pass = st.text_input("API Password", type="password")
            r_iface = st.text_input("Interface WireGuard", value="wg0")
            r_submit = st.form_submit_button("💾 Simpan Router")
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
                st.success("Router disimpan!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Gagal"))

    with col_r2:
        st.markdown("### 🌐 Armada Router Aktif")
        for r in routers:
            with st.container():
                st.markdown(f"**🖧 {r['router_name']}**")
                st.caption(f"IP: `{r['host']}:{r['port']}` | Iface: `{r['wg_interface']}`")
                if st.button(f"Hapus Router {r['router_name']}", key=f"del_r_{r['id']}"):
                    requests.delete(f"{API_BASE}/routers/{r['id']}")
                    st.rerun()
                st.markdown(
                    "<hr style='margin: 0.4rem 0px; border-color: #1e293b;'>",
                    unsafe_allow_html=True,
                )

# --- TAB 3: MANAJEMEN USER (ADMIN PANEL) ---
with tab_user_mgmt:
    st.markdown("### 👥 Manajemen Pengguna & Approval Akun")
    if st.session_state.role != "root":
        st.warning("⚠️ Anda harus masuk sebagai Root Admin untuk mengelola pengguna.")
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
                    status_text = (
                        "🟢 **Disetujui (Approved)**"
                        if u["is_approved"]
                        else "🟡 **Menunggu Approval (Pending)**"
                    )
                    st.markdown(status_text)
                with uc3:
                    if not u["is_approved"]:
                        if st.button("✅ Approve", key=f"app_{u['id']}"):
                            requests.put(f"{API_BASE}/users/{u['id']}/approve")
                            st.rerun()
                    if u["role"] != "root":
                        if st.button("🗑️ Hapus User", key=f"del_u_{u['id']}"):
                            requests.delete(f"{API_BASE}/users/{u['id']}")
                            st.rerun()
                st.markdown(
                    "<hr style='margin: 0.4rem 0px; border-color: #1e293b;'>",
                    unsafe_allow_html=True,
                )

# --- TAB 4: AUDIT LOG ---
with tab_logs:
    st.markdown("### 📜 Sistem Audit Log Aktivitas Pengguna")
    if st.button("🔄 Refresh Log"):
        st.rerun()

    logs_res = requests.get(f"{API_BASE}/audit-logs")
    logs = logs_res.json() if logs_res.status_code == 200 else []

    if logs:
        for log in logs:
            st.markdown(
                f"- `[{log['timestamp']}]` **{log['username']}** melakukan"
                f" **{log['action']}**: _{log['details']}_"
            )
    else:
        st.info("Belum ada aktivitas tercatat.")
