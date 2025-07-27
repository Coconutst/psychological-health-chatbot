from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
from sqlalchemy.orm import Session
from . import schemas, services

router = APIRouter()


@router.post("/reset-password")
async def reset_password(
        token: str,
        new_password: str,
        db: Session = Depends(services.get_db)
):
    user = services.verify_reset_token(token)
    if not user:
        raise HTTPException(status_code=400, detail="无效的重置令牌")

    hashed_password = services.hash_password(new_password)
    services.update_user_password(db, user.id, hashed_password)
    return {"status": "success"}