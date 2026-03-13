from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str