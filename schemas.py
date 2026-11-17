from pydantic import BaseModel

class RouterCreate(BaseModel):
    router_name: str
    host: str
    port: int = 8728
    username: str
    password: str
    wg_interface: str = "wg0"

class RouterResponse(RouterCreate):
    id: int

    class Config:
        from_attributes = True

class ProvisionRequest(BaseModel):
    client_name: str
    private_key: str
    router_id: int

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
