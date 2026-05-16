from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, hash_password
from app.database import get_db
from app.models import User
from app.schemas import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """List all users (paginated)."""
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user. Users can only update themselves."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user. Users can only delete themselves."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
