from fastapi import FastAPI
from app.api.detection import router as detection_router
from app.api.analytics import router as analytics_router
from app.api.upload import router as upload_router

from app.api.violations import router as violations_router

app = FastAPI(title="HawkEye Traffic AI - SEVE Enabled")

app.include_router(upload_router, prefix="/api")
app.include_router(detection_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(violations_router, prefix="/api")

@app.get("/")
def root():
    return {
        "system": "HawkEye Traffic AI",
        "status": "Online",
        "seve_engine": "Active"
    }