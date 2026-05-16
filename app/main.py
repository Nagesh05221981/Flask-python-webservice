from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth_router, users_router, products_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Service API",
    description=(
        "A simple REST API with:\n"
        "- **User & Product CRUD**\n"
        "- **Username/password login** (JWT)\n"
        "- **Dummy OAuth provider**\n"
        "- **API key authentication** (X-API-Key header)\n\n"
        "Authenticate via the **Authorize** button using either:\n"
        "1. Username/password (OAuth2 form) to get a Bearer token\n"
        "2. An API key in the `X-API-Key` header"
    ),
    version="1.0.0",
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(products_router.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "my-service"}
