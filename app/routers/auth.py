from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse

from app.core.deps import CurrentUserDep
from app.models.models import User
from app.schemas.auth_schema import ChangePasswordSchema, LoginSchema, RegisterSchema
from app.core.security import create_access_token, hash_password, verify_password


router = APIRouter()


@router.post("/login")
async def login(credentials: LoginSchema):
    user = await User.filter(username=credentials.username).first()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "User not found"}
        )
    if not verify_password(credentials.password, user.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid username or password"},
        )
    return {
        "message": "Login successful",
        "token": create_access_token(data={"sub": user.username}),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(credentials: RegisterSchema):
    user = await User.filter(username=credentials.username).first()
    if user:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={"message": "User already exists"},
        )
    await User.create(
        username=credentials.username,
        password=hash_password(credentials.password),
        name=credentials.name,
    )

    return {
        "message": "User created successfully",
        "token": create_access_token(
            data={"sub": credentials.username},
        ),
    }


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user: CurrentUserDep):
    return {
        "username": user.username,
        "name": user.name,
        "completed_unit": user.completed_unit
    }


@router.post('/change-password', status_code=status.HTTP_200_OK)
async def change_password(
    user: CurrentUserDep,
    credentials: ChangePasswordSchema
):
    user.password = hash_password(credentials.new_password)
    await user.save()
    return {
        "message": "Succesfully changed",
    }
