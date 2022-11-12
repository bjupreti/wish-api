from fastapi import Response, status, HTTPException, Depends, APIRouter, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from ..oauth2 import get_current_user
from ..models.transaction import Transaction as TransactionModel
from ..models.user import User as UserModel
from ..schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate, UploadPhotoResponse
from ..database import get_db
from ..common.s3 import upload_file_in_s3, create_presigned_url


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

@router.get("/", response_model=Page[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), search: str | None = "", params: Params = Depends()):
    transactions = paginate(db.query(TransactionModel).filter(func.lower(TransactionModel.title).contains(search.lower())).order_by(TransactionModel.created_at.desc()), params)

    # creating preassigned url and sending it as profile_pic_url
    for item in transactions.items:
        print(item)
        if item.transaction_pic_url:
            item.transaction_pic_url = create_presigned_url(item.transaction_pic_url)
    return transactions

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    transaction = db.query(TransactionModel).filter_by(id=str(id)).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"transaction with id: {id} doesn't exist.")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized to perform requested action")

    # creating preassigned url and sending it as profile_pic_url
    if transaction.transaction_pic_url:
        transaction.transaction_pic_url = create_presigned_url(transaction.transaction_pic_url)

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


@router.post("/upload-file", response_model=UploadPhotoResponse)
async def upload_file(file: UploadFile, transaction_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # TODO: Check the file size - HTTP_413 = 'Request Entity Too Large'
    # Upload Files
    type = file.content_type
    transaction_id = str(transaction_id)
    key = f"transaction_pic_url/{str(current_user.id)}/{transaction_id}.{file.filename}"
    if (type != "image/jpeg" and type != "image/png" and type != "image/svg+xml"):
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Please upload jpeg/png images!")
    try:
        await upload_file_in_s3(key, file)
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File upload unsuccessful! Please try again later.")

    # Update file URL
    transaction_query = db.query(TransactionModel).filter_by(id=str(transaction_id))
    transaction = transaction_query.first()

    setattr(transaction, "transaction_pic_url", key)

    db.commit()
    
    return {"detail": f"{file.filename} Upload Successful"}