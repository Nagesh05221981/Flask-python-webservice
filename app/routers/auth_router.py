from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, hash_password, get_current_user
from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserOut, OAuthCallbackRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with username and password."""
    if db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password. Returns a JWT access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# --- Dummy OAuth Provider ---

# In a real app this would redirect to Google/GitHub. Here we simulate it.
DUMMY_OAUTH_USERS = {
    "dummy-auth-code-123": {
        "username": "oauth_user",
        "email": "oauth@example.com",
    }
}


@router.get("/oauth/login")
def oauth_login():
    """Dummy OAuth: returns a fake authorization URL.
    In production this would redirect to Google/GitHub."""
    return {
        "authorization_url": "http://localhost:8000/auth/oauth/callback?code=dummy-auth-code-123",
        "message": "Visit the URL above (or POST the code to /auth/oauth/callback) to complete login.",
    }


@router.post("/oauth/callback", response_model=Token)
def oauth_callback(body: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """Exchange a dummy OAuth code for an access token.
    If the user doesn't exist yet, they are auto-registered."""
    oauth_user = DUMMY_OAUTH_USERS.get(body.code)
    if not oauth_user:
        raise HTTPException(status_code=400, detail="Invalid OAuth code")

    user = db.query(User).filter(User.username == oauth_user["username"]).first()
    if not user:
        user = User(
            username=oauth_user["username"],
            email=oauth_user["email"],
            hashed_password=hash_password("oauth-managed"),  # placeholder
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user
