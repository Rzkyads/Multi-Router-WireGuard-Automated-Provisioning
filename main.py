from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import database, models, schemas, wg_service
from crypto_helper import encrypt
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Cyaneum WireGuard Multi-Router NCM", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTER MANAGEMENT ENDPOINTS ---

@app.post("/api/v1/routers", response_model=schemas.RouterResponse)
def register_router(router_in: schemas.RouterCreate, db: Session = Depends(get_db)):
    try:
        # Test connection before saving
        wg_service.test_router_connection(router_in.host, router_in.port, router_in.username, router_in.password)
        
        db_router = models.MikrotikRouter(
            router_name=router_in.router_name,
            host=router_in.host,
            port=router_in.port,
            username=router_in.username,
            password=encrypt(router_in.password),
            wg_interface=router_in.wg_interface
        )
        db.add(db_router)
        db.commit()
        db.refresh(db_router)
        return db_router
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Router name already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to connect or save router: {str(e)}")

@app.get("/api/v1/routers", response_model=list[schemas.RouterResponse])
def list_routers(db: Session = Depends(get_db)):
    return db.query(models.MikrotikRouter).all()

@app.delete("/api/v1/routers/{router_id}")
def delete_router(router_id: int, db: Session = Depends(get_db)):
    router = db.query(models.MikrotikRouter).filter(models.MikrotikRouter.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found.")

    clients_count = db.query(models.Client).filter(models.Client.router_id == router_id).count()
    if clients_count > 0:
        raise HTTPException(status_code=400, detail="Tidak dapat menghapus router karena masih ada klien VPN yang terikat padanya.")

    db.delete(router)
    db.commit()
    return {"message": "Router berhasil dihapus."}

@app.post("/api/v1/routers/{router_id}/test-connection")
def test_router_connection(router_id: int, db: Session = Depends(get_db)):
    router = db.query(models.MikrotikRouter).filter(models.MikrotikRouter.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found.")

    if wg_service.settings.SIMULATION_MODE:
        return {"status": "online", "message": "Simulasi Mode: Router Online"}

    try:
        import librouteros
        from crypto_helper import decrypt
        connection = librouteros.connect(
            username=router.username,
            password=decrypt(router.password),
            host=router.host,
            port=router.port,
            timeout=3,
        )
        connection.close()
        return {"status": "online", "message": "Koneksi API Mikrotik Berhasil"}
    except Exception as e:
        return {"status": "offline", "message": str(e)}

# --- WIREGUARD CLIENT PROVISIONING ENDPOINTS ---

@app.post("/api/v1/wg/generate")
def generate_client(data: schemas.ProvisionRequest, db: Session = Depends(get_db)):
    if not wg_service.validate_private_key(data.private_key):
        raise HTTPException(status_code=400, detail="Invalid key format or length (must be 44 chars).")

    router = db.query(models.MikrotikRouter).filter(models.MikrotikRouter.id == data.router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Target MikroTik router not found.")

    if wg_service.settings.SIMULATION_MODE:
        public_key = f"MOCK_PUBKEY_{data.client_name.upper().replace(' ', '_')}_123="
    else:
        public_key = wg_service.derive_public_key(data.private_key)
    allocated_ip = wg_service.get_next_available_ip(db)
    
    db_client = models.Client(
        client_name=data.client_name,
        public_key=public_key,
        allocated_ip=allocated_ip,
        router_id=router.id,
        is_active=True
    )
    db.add(db_client)
    db.commit()

    try:
        wg_service.add_peer_to_mikrotik(router, public_key, allocated_ip, data.client_name)
    except Exception as e:
        db.delete(db_client)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    
    config_text = wg_service.generate_config_text(data.private_key, allocated_ip, router)
    
    return {
        "client_name": db_client.client_name,
        "client_ip": allocated_ip,
        "router_name": router.router_name,
        "config_text": config_text,
    }

@app.get("/api/v1/wg/clients")
def list_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).all()

@app.delete("/api/v1/wg/clients/{client_id}")
def revoke_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")

    router = db.query(models.MikrotikRouter).filter(models.MikrotikRouter.id == client.router_id).first()
    if router:
        wg_service.remove_peer_from_mikrotik(router, client.public_key)

    db.delete(client)
    db.commit()
    return {"message": "Client revoked successfully and IP recycled."}
