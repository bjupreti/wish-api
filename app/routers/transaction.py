from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..oauth2 import get_current_user
from ..models.transaction import Transaction as TransactionModel
from ..models.user import User as UserModel
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
    # Update total income and total expense in user table
    user_query = db.query(UserModel).filter_by(id=str(current_user.id))
    user = user_query.first()
    # updating the updated transaction income or expense
    final_total_income = float(user.total_income) + transaction["amount"] if transaction["is_income"] else user.total_income
    final_total_expense = float(user.total_expense) + transaction["amount"] if transaction["is_expense"] else user.total_expense
    updated_total_income_expense = {
        "total_income": final_total_income,
        "total_expense": final_total_expense
    }
    user_query.update(updated_total_income_expense, synchronize_session=False)

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
    # Update total income and total expense in user table
    user_query = db.query(UserModel).filter_by(id=str(current_user.id))
    user = user_query.first()
    # updating the updated transaction income or expense
    final_total_income = user.total_income - transaction.amount if transaction.is_income else user.total_income
    final_total_expense = user.total_expense - transaction.amount if transaction.is_expense else user.total_expense
    updated_total_income_expense = {
        "total_income": final_total_income,
        "total_expense": final_total_expense
    }
    user_query.update(updated_total_income_expense, synchronize_session=False)

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
    

    # Update total income and total expense in user table
    user_query = db.query(UserModel).filter_by(id=str(current_user.id))
    user = user_query.first()
    # updating the updated transaction income or expense
    final_total_income = float(user.total_income) + updated_transaction["amount"] if updated_transaction["is_income"] else user.total_income
    final_total_expense = float(user.total_expense) + updated_transaction["amount"] if updated_transaction["is_expense"] else user.total_expense
    # removing the current transaction income or expense as we are updating it
    final_total_income = final_total_income - float(transaction.amount) if transaction.is_income else user.total_income
    final_total_expense = final_total_expense - float(transaction.amount) if transaction.is_expense else user.total_expense
    updated_total_income_expense = {
        "total_income": final_total_income,
        "total_expense": final_total_expense
    }
    user_query.update(updated_total_income_expense, synchronize_session=False)
    transaction_query.update(updated_transaction, synchronize_session=False)
    db.commit()

    return transaction_query.first()

