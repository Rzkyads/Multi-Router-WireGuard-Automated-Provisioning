import base64
import ipaddress
import librouteros
from config import settings
from models import Client, MikrotikRouter
from sqlalchemy.orm import Session
from crypto_helper import decrypt
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

SUBNET = "10.10.0.0/24"

def validate_private_key(key: str) -> bool:
    if len(key) != 44:
        return False
    try:
        base64.b64decode(key)
        return True
    except:
        return False

def derive_public_key(private_key_base64: str) -> str:
    """Menghasilkan Public Key Curve25519 WireGuard yang valid dari Private Key."""
    try:
        priv_bytes = base64.b64decode(private_key_base64)
        priv_key = x25519.X25519PrivateKey.from_private_bytes(priv_bytes)
        pub_key = priv_key.public_key()
        pub_bytes = pub_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(pub_bytes).decode("utf-8")
    except Exception:
        # Fallback jika gagal decode
        return "MOCK_DERIVED_PUBKEY_BASE64_ABC123="

def get_next_available_ip(db: Session) -> str:
    network = ipaddress.ip_network(SUBNET)
    used_ips = {c.allocated_ip for c in db.query(Client.allocated_ip).all()}
    for ip in list(network.hosts())[1:]:
        if str(ip) not in used_ips:
            return str(ip)
    raise Exception("IP pool exhausted")

def get_mikrotik_server_config(router: MikrotikRouter):
    """Mengambil Public Key dan Listen Port asli dari interface WireGuard di MikroTik via API."""
    if settings.SIMULATION_MODE:
        return {
            "public_key": "fNqJmtIGBAucwH1edpb/YulSocMIZigJwTKAD2ACvHY=",
            "port": 13231,  # Menyesuaikan dengan port aktual di router Anda
        }

    try:
        connection = librouteros.connect(
            username=router.username,
            password=decrypt(router.password),
            host=router.host,
            port=router.port,
        )

        # Menggunakan path dengan pemanggilan iterasi kueri yang benar di librouteros
        wg_interface_api = connection.path("interface/wireguard")
        server_pub_key = None
        server_port = 51820  # Fallback default

        for iface in wg_interface_api:
            if iface.get("name") == router.wg_interface:
                server_pub_key = iface.get("public-key")

                # Cek berbagai kemungkinan nama key port dari API RouterOS
                port_val = (
                    iface.get("listen-port")
                    or iface.get("listen_port")
                    or iface.get("port")
                )
                if port_val:
                    server_port = int(port_val)
                break

        connection.close()

        if server_pub_key:
            return {"public_key": server_pub_key, "port": server_port}

        raise Exception(f"Interface WireGuard '{router.wg_interface}' tidak ditemukan di router {router.router_name}")
    except Exception as e:
        raise RuntimeError(f"Gagal mengambil konfigurasi server dari MikroTik: {str(e)}")


def add_peer_to_mikrotik(router: MikrotikRouter, public_key: str, allowed_ip: str, client_name: str):
    if settings.SIMULATION_MODE:
        print(f"[SIMULATION MODE] Menambahkan peer ke Router [{router.router_name}] -> Nama: {client_name}, PubKey: {public_key}, IP: {allowed_ip}")
        return

    try:
        connection = librouteros.connect(
            username=router.username,
            password=decrypt(router.password),
            host=router.host,
            port=router.port,
        )

        # Menggunakan connection.path untuk mengakses API path MikroTik secara benar di librouteros
        peers_api = connection.path("interface/wireguard/peers")
        peers_api.add(
            **{
                "interface": router.wg_interface,
                "public-key": public_key,
                "allowed-address": f"{allowed_ip}/32",
                "comment": client_name,
            }
        )
        connection.close()
    except Exception as e:
        print(f"DETAIL ERROR MIKROTIK API: {str(e)}")
        raise RuntimeError(f"Gagal menambahkan peer ke MikroTik via API: {str(e)}")


def remove_peer_from_mikrotik(router: MikrotikRouter, public_key: str):
    if settings.SIMULATION_MODE:
        print(f"[SIMULATION MODE] Menghapus peer dari Router [{router.router_name}] -> PubKey: {public_key}")
        return

    try:
        connection = librouteros.connect(
            username=router.username,
            password=decrypt(router.password),
            host=router.host,
            port=router.port,
        )
        peers_api = connection(path="interface/wireguard/peers")
        for peer in peers_api:
            if peer.get("public-key") == public_key:
                peers_api.remove(id=peer[".id"])
                break
        connection.close()
    except Exception as e:
        print(f"Peringatan gagal hapus peer di router: {str(e)}")

def generate_config_text(private_key: str, client_ip: str, router: MikrotikRouter) -> str:
    server_config = get_mikrotik_server_config(router)
    endpoint = f"{router.host}:{server_config['port']}"
    return f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}/32
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server_config['public_key']}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

def test_router_connection(host, port, username, password):
    connection = librouteros.connect(
        username=username,
        password=password,
        host=host,
        port=port,
    )
    connection.close()
    return True
