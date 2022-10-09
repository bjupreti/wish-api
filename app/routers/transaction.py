from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..oauth2 import get_current_user
from ..models.transaction import Transaction as TransactionModel
from ..schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from ..database import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    transaction = transaction.dict()
    transaction["is_expense"] = not transaction["is_income"]
    new_transaction = TransactionModel(**transaction, user_id=current_user.id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), limit: int = 10, page: int = 1, search: str | None = ""):
    offset = (page - 1) * limit
    # TODO: Make search case-insensitive
    # TODO: Add order_by
    transactions = db.query(TransactionModel).filter(TransactionModel.user_id == current_user.id).filter(TransactionModel.title.contains(search)).order_by(TransactionModel.created_at.desc()).limit(limit).offset(offset).all()
    return transactions

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    transaction = db.query(TransactionModel).filter_by(id=str(id)).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"transaction with id: {id} doesn't exist.")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized to perform requested action")

    return transaction

@router.delete("/{id}")
def delete_transaction(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    transaction_query = db.query(TransactionModel).filter_by(id=str(id))
    transaction = transaction_query.first()

    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"transaction with id: {id} doesn't exist.")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not Authorized to perform requested action")

    transaction_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=TransactionResponse)
def update_transaction(id: int, updated_transaction: TransactionUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    transaction_query = db.query(TransactionModel).filter_by(id=str(id))
    transaction = transaction_query.first()

    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"transaction with id: {id} doesn't exist.")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not Authorized to perform requested action")

    updated_transaction = updated_transaction.dict()
    updated_transaction["is_expense"] = not updated_transaction["is_income"]
    transaction_query.update(updated_transaction, synchronize_session=False)
    db.commit()
    return transaction_query.first()

