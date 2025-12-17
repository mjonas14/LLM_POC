from typing import Optional, Dict, Any
from database.db import db  # uses your Atlas URI from .env

def get_latest_index_snapshot(index_id: str) -> Optional[Dict[str, Any]]:
    """
    Return the latest document for a given index ID from MongoDB.

    Args:
        index_id: The ID field of the index (e.g. "2003RealEstate").

    Returns:
        A dict with the latest snapshot or None if not found.
    """
    doc = db.indexes.find_one(
        {"ID": index_id},
        sort=[("Date", -1)],
        projection={"_id": 0},  # hide Mongo internal id
    )
    return doc
