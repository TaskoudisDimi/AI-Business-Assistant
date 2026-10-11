from pydantic import BaseModel

class ProfileCreate(BaseModel):
    full_name: str