from fastapi import FastAPI

app=FastAPI(title="Urban Aanchol API")

@app.get("/")
def root():
    return {"message": "Urban Aanchol API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}