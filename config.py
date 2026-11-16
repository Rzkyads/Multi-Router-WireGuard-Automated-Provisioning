from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    WG_INTERFACE: str = "wg0"
    WG_SUBNET_PREFIX: str = "10.10.0"
    DNS_SERVERS: str = "1.1.1.1, 8.8.8.8"
    SERVER_PUBLIC_KEY: str = "SERVER_PUBKEY_MOCK_DUMMY_KEY_BASE64="
    SERVER_ENDPOINT: str = "127.0.0.1:51820"
    DATABASE_URL: str = "sqlite:///./wireguard.db"
    MIKROTIK_HOST: str = "192.168.88.1"
    MIKROTIK_PORT: int = 8728
    MIKROTIK_USER: str = "admin"
    MIKROTIK_PASS: str = ""
    SIMULATION_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
