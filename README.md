# Cyaneum Multi-Router WireGuard Automated Provisioning System

Enterprise-grade automated network client management and provisioning system built with FastAPI, SQLite, SQLAlchemy, Streamlit, and MikroTik RouterOS v7 API integration.

## 🚀 Features
- **Dynamic Multi-Router Management**: Control multiple MikroTik routers from a single master dashboard.
- **Automated IPAM**: Subnet allocation management (`10.10.0.0/24`).
- **Real-time MikroTik API Sync**: Automatically provisions WireGuard peers and maps client names directly to Winbox (`comment`).
- **AES-Fernet Security**: Encrypts MikroTik API passwords at rest in the database.
- **Ocean-Dusk UI**: Minimalist, professional NOC dashboard built with Streamlit.
- **Simulation Mode**: Run and test the entire backend locally on Windows without physical WireGuard tools.

---

## 📦 Installation & Deployment Guide

### 1. Docker Deployment (Recommended for Production)
1. Ensure **Docker** and **Docker Compose** are installed on your server.
2. Clone the repository and configure your environment:
   ```bash
   git clone https://github.com/Rzkyads/Multi-Router-WireGuard-Automated-Provisioning.git
   cd Multi-Router-WireGuard-Automated-Provisioning
   cp .env.example .env
   ```
3. Edit `.env` and set `SIMULATION_MODE=false` alongside your production parameters.
4. Build and launch containers:
   ```bash
   docker-compose up -d --build
   ```
5. Access the services:
   - FastAPI Backend / Swagger Docs: `http://<your-server-ip>:8000/docs`
   - Streamlit Dashboard: `http://<your-server-ip>:8501` (or add frontend service to compose if needed)

---

### 2. Linux Native Setup (Debian / Ubuntu / CentOS)
1. Install system dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv wireguard-tools iproute2
   ```
2. Clone repository & setup virtual environment:
   ```bash
   git clone https://github.com/Rzkyads/Multi-Router-WireGuard-Automated-Provisioning.git
   cd Multi-Router-WireGuard-Automated-Provisioning
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Setup configuration:
   ```bash
   cp .env.example .env
   # Edit .env as required
   ```
4. Run the services:
   - Start FastAPI:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - Start Streamlit (in a separate terminal):
     ```bash
     streamlit run app.py
     ```

---

### 3. Windows Setup (Local Development & Simulation)
If you want to test or develop the system locally on Windows without physical MikroTik/WireGuard kernel utilities:
1. Ensure Python 3.11+ is installed.
2. Open PowerShell in the project directory:
   ```powershell
   python -m venv venv
   venv\Scripts\Activate
   pip install -r requirements.txt
   ```
3. Ensure `.env` has `SIMULATION_MODE=true`.
4. Run Backend:
   ```powershell
   uvicorn main:app --reload
   ```
5. Run Frontend (in a separate PowerShell window):
   ```powershell
   streamlit run app.py
   ```
