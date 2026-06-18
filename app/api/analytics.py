from fastapi import APIRouter

from app.database.mongodb import (
    violations_collection
)

router = APIRouter()


@router.get("/analytics")

def analytics():

    total = (violations_collection.count_documents({}))

    triple_riding = (
        violations_collection
        .count_documents(
            {
                "violations.type":
                "TRIPLE_RIDING"
            }
        )
    )

    return {

        "total_records":
        total,

        "triple_riding":
        triple_riding
    }