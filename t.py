from app.database.mongodb import (
    violations_collection
)

print(
    violations_collection.count_documents({})
)