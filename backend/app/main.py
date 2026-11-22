from fastapi import FastAPI

from backend.app.api.routes.customers import router as customers_router
from backend.app.api.routes.inventory import router as inventory_router
from backend.app.api.routes.orders import router as orders_router


app = FastAPI(title="Urban Aanchol API")

app.include_router(inventory_router)
app.include_router(customers_router)
app.include_router(orders_router)


@app.get("/")
def root():
    return {"message": "Urban Aanchol API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}