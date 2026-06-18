from fastapi import FastAPI

from app.api.detection import router as detection_router

app = FastAPI(
    title="HawkEye Traffic AI"
)

app.include_router(
    detection_router,
    prefix="/api"
)


@app.get("/")
def root():

    return {
        "message": "HawkEye Traffic AI Running"
    }