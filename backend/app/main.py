from fastapi import FastAPI

from backend.app.api.routes.inventory import router as inventory_router

app = FastAPI(title="Urban Aanchol API")

app.include_router(inventory_router)


@app.get("/")
def root():
    return {"message": "Urban Aanchol API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
