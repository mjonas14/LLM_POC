import json
from db import db  # uses your Atlas URI from .env

COLLECTION_NAME = "indexes"  # change as needed

def import_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    collection = db[COLLECTION_NAME]

    if isinstance(data, list):
        if not data:
            print("No documents to insert.")
            return
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into {COLLECTION_NAME}.")
    else:
        result = collection.insert_one(data)
        print(f"Inserted document with _id={result.inserted_id} into {COLLECTION_NAME}.")

if __name__ == "__main__":
    import_json(".json/raw_index_data.json")   # update this to be location of file
