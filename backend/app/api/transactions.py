import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories.transaction import TransactionRepository
from app.db.session import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)) -> TransactionRead:
    return TransactionRepository(db).create(data)


@router.get("", response_model=list[TransactionRead])
def list_transactions(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> list[TransactionRead]:
    return TransactionRepository(db).list(limit=limit, offset=offset)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)) -> TransactionRead:
    transaction = TransactionRepository(db).get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID, data: TransactionUpdate, db: Session = Depends(get_db)
) -> TransactionRead:
    transaction = TransactionRepository(db).update(transaction_id, data)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    if not TransactionRepository(db).delete(transaction_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")