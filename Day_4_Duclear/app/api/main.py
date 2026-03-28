from fastapi import FastAPI

from app.api.routes.receipts import router as receipts_router


app = FastAPI(
    title="Receipt Processing API",
    version="1.0.0"
)

app.include_router(receipts_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}