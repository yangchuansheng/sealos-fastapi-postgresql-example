from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.db import get_connection
from app.models import ItemCreate, ItemRead


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "framework": "FastAPI"}


@router.post("/items", response_model=ItemRead, status_code=201)
def create_item(
    item: ItemCreate,
    connection: Connection[Any] = Depends(get_connection),
) -> ItemRead:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO items (name, description)
                VALUES (%s, %s)
                RETURNING id, name, description
                """,
                (item.name, item.description),
            )
            row = cursor.fetchone()
        connection.commit()
    except Exception:
        connection.rollback()
        raise

    if row is None:
        raise RuntimeError("item insert returned no row")
    return ItemRead.model_validate(row)


@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(
    item_id: int,
    connection: Connection[Any] = Depends(get_connection),
) -> ItemRead:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, description FROM items WHERE id = %s",
                (item_id,),
            )
            row = cursor.fetchone()
        connection.commit()
    except Exception:
        connection.rollback()
        raise

    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead.model_validate(row)
