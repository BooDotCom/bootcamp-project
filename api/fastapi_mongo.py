from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from bson.objectid import ObjectId
from backend.mongodb_database import DatabaseManager
from dotenv import load_dotenv
from enum import Enum
from typing import Optional
import os

load_dotenv()

app = FastAPI(title="MongoDB Database API", version ="1.0.0")

#pydantic models for request/response

class TransactionCreate(BaseModel):
    name: str
    amount: int
    transaction_type: Optional[str]
    description: Optional[str]
    # paid: Optional[str]
    date: datetime

class TransactionUpdate(BaseModel):
    name: str
    amount: int
    transaction_type: Optional[str]
    description: Optional[str]
    # paid: Optional[str]
    date: datetime

class TransactionResponse(BaseModel):
    id: str
    name: str
    amount: int
    transaction_type: str
    description: str
    paid: str
    date: datetime

class TransactionResponsePaid(BaseModel):
    id: str
    name: str
    amount: int
    transaction_type: str
    description: str
    date: datetime

class TransactionResponseUnpaid(BaseModel):
    id: str
    name: str
    date: datetime

#Initialize database
try:
    db = DatabaseManager()
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    db = None

#event handler
@app.on_event("startup")
async def startup_event():
    if db is None:
        raise Exception("Failed to connect to MongoDB")
    
@app.on_event("shutdown")
async def shutdown_event():
    if db:
        db.close_connection()


@app.get("/")
async def root():
    return {"message": "MongoDB Database API", "version": "1.0.0"}

@app.post("/transactions/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction(tran: TransactionCreate):
    """Create a new transaction"""
    try:

        #Check if amount = 0(not paid) or not(paid)
        if tran.amount == 0:
            tran.transaction_type = ""
            tran.description = ""
            paid = "No"
            # tran.date = datetime.now()
        else:
            paid = "Yes"

        tran_id = db.create_transaction(tran.name, tran.amount, tran.transaction_type, tran.description, paid, tran.date)
        
        if tran_id:
            return {"message": "Transaction created successfully", "tran_id": tran_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create transaction"
            )
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )

@app.get("/transactions/", response_model=List[TransactionResponse])
async def get_all_transactions():
    """Get all transactions"""
    try:
        trans = db.get_all_transactions()
        return [
            TransactionResponse(
                id=tran['_id'],
                name=tran['name'],
                amount=tran['amount'],
                transaction_type=tran['transaction_type'],
                description=tran['description'],
                paid=tran['paid'],
                date=tran['date']
            )
            for tran in trans
        ]
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )
    
    
@app.get("/transactions/by-year/", response_model=List[TransactionResponse])
async def get_transactions_by_year(year: int):
    """Get paid transactions by year"""
    try:

        paid = ""

        trans = db.get_transaction_by_year(year, paid)
        return [
            TransactionResponse(
                id=tran['_id'],
                name=tran['name'],
                amount=tran['amount'],
                transaction_type = tran['transaction_type'],
                description=tran['description'],
                paid=tran['paid'],
                date=tran['date']
            )
            for tran in trans
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )
    
@app.get("/transactions/by-year/paid/", response_model=List[TransactionResponsePaid])
async def get_transactions_by_year(year: int,paid: str):
    """Get paid transactions by year"""
    try:

        paid = paid.lower()

        if paid in ["yes", "paid"]:
            trans = db.get_transaction_by_year(year, paid)
            return [
                TransactionResponsePaid(
                    id=tran['_id'],
                    name=tran['name'],
                    amount=tran['amount'],
                    transaction_type = tran['transaction_type'],
                    description=tran['description'],
                    date=tran['date']
                )
                for tran in trans
            ]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="paid must be Yes or Paid."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )

@app.get("/transactions/by-year/unpaid/", response_model=List[TransactionResponseUnpaid])
async def get_transactions_by_year(year: int,paid: str):
    """Get unpaid transactions by year"""
    try:

        paid = paid.lower()

        if paid in ["no", "unpaid"]:
            trans = db.get_transaction_by_year(year, paid)
            return [
                TransactionResponseUnpaid(
                    id=tran['_id'],
                    name=tran['name'],
                    date=tran['date']
                )
                for tran in trans
            ]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="paid must be No or Unpaid."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )

@app.delete("/transactions/{tran_id}", response_model=dict)
async def delete_transaction(tran_id: str):
    """Delete transaction"""
    try:

        if not ObjectId.is_valid(tran_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Transaction ID format"
            )

        #check if user exists
        tran = db.transaction_collection.find_one({"_id": ObjectId(tran_id)})
        if not tran:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        success = db.delete_transaction(tran_id)
        if success:
            return {"message": "Transaction deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete transaction"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )
    
@app.put("/transactions/{tran_id}", response_model=dict)
async def update_transaction(tran_id: str, tran_update: TransactionUpdate):
    """Update transaction by ID"""
    try:

        if not ObjectId.is_valid(tran_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction ID format"
            )

        #check if transaction exists
        tran = db.transaction_collection.find_one({"_id": ObjectId(tran_id)})
        if not tran:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
            
        #update transaction
        if tran_update.amount == 0:
            tran_update.transaction_type = ""
            tran_update.description = ""
            paid = "No"
            # tran_update.date = datetime.now()
        else:
            paid = "Yes"

        result = db.update_transaction(tran_id, tran_update.name, tran_update.amount, tran_update.transaction_type, tran_update.description, paid, tran_update.date)

        if result:
            return {"message": "Transaction updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update transaction"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)