from pydantic import BaseModel, Field, field_validator


class LoginSchema(BaseModel):
    username: str = Field(
        ..., min_length=5, max_length=50, description="Username of the user"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="Password of the user"
    )

    class Config:
        json_schema_extra = {
            "example": {"username": "exampleusername", "password": "password123"}
        }

    @field_validator("username")
    def normalize_username(cls, v):
        return v.lower().strip()


class RegisterSchema(BaseModel):
    username: str = Field(
        ..., min_length=5, max_length=50, description="Username of the user"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="Password of the user"
    )
    name: str = Field(..., min_length=3, max_length=50, description="Name of the user")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "exampleusername",
                "password": "newpassword123",
                "name": "New User",
            }
        }

    @field_validator("username")
    def normalize_username(cls, v):
        return v.lower().strip()


class ChangePasswordSchema(BaseModel):
    new_password: str = Field(
        ..., min_length=6, max_length=100, description="New password"
    )
