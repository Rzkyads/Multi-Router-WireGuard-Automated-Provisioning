from database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, func

class MikrotikRouter(Base):
    __tablename__ = "mikrotik_routers"

    id = Column(Integer, primary_key=True, index=True)
    router_name = Column(String, unique=True, index=True, nullable=False)
    host = Column(String, nullable=False)  # IP / Domain Router
    port = Column(Integer, default=8728)  # API Port (default 8728)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    wg_interface = Column(String, default="wg0")  # Nama interface wg di router
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, unique=True, index=True, nullable=False)
    public_key = Column(String, unique=True, nullable=False)
    allocated_ip = Column(String, unique=True, nullable=False)
    router_id = Column(Integer, ForeignKey("mikrotik_routers.id"), nullable=False)  # Menyimpan router tempat klien terhubung
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
