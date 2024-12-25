from fastapi import FastAPI
from resources.test import router
from resources.auth import router as auth_router 

app = FastAPI(title="Root API")

app.include_router(router, prefix="/api", tags=["Test"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"status": 200, "message": "success", "data": [], "error": ""}
