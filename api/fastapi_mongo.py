# #checklist:
# #post new user: /
# #get all users: /
# #post new post: /
# #get all posts from specific user: / 
# #delete user and its posts: /
# #delete specific post: /
# #get specific user: 
# #get specific post:
# #get all posts: /
# #put user: /
# #put post:

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

# class TransactionType(str, Enum):
#     debit = "Debit"
#     credit = "Credit"

# class Paid(str, Enum):
#     paid = "Paid"
#     not_paid = "Not Paid"

class TransactionCreate(BaseModel):
    name: str
    amount: int
    transaction_type: Optional[str]
    description: Optional[str]
    # paid: Optional[str]
    date: datetime

# class UserUpdate(BaseModel):
#     name: Optional[str]
#     email: Optional[EmailStr]
#     age: Optional[int]

class TransactionResponse(BaseModel):
    id: str
    name: str
    amount: int
    transaction_type: str
    description: str
    paid: str
    date: datetime

# class PostCreate(BaseModel):
#     user_id: str
#     title: str
#     content: str

# class PostUpdate(BaseModel):
#     # user_id: Optional[int] = None
#     title: Optional[str] = None
#     content: Optional[str] = None

# class PostResponse(BaseModel):
#     id: str
#     user_id: str
#     title: str
#     content: str
#     created_at: datetime

# class PostResponseForUser(BaseModel):
#     id: str
#     title: str
#     content: str
#     created_at: datetime

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
            tran.transaction_type = "debit"
            tran.description = ""
            paid = "No"
            tran.date = datetime.now()
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
    
# # @app.get("/users/{user_id}", response_model=UserResponse)
# # async def get_user(user_id: str):
# #     """Get specific user by ID"""
# #     try:
        
# #         if not ObjectId.is_valid(user_id):
# #             raise HTTPException(
# #                 status_code=status.HTTP_400_BAD_REQUEST,
# #                 detail="Invalid user ID format"
# #             )

# #         user = db.users_collection.find_one({"_id": ObjectId(user_id)})
# #         if not user:
# #             raise HTTPException(
# #                 status_code=status.HTTP_404_NOT_FOUND,
# #                 detail="User not found"
# #             )
            
# #         return UserResponse(
# #                 id=user['_id'],
# #                 name=user['name'],
# #                 email=user['email'],
# #                 age=user['age'],
# #                 created_at=user['created_at'],
# #             )
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         raise HTTPException(
# #                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #                 detail=f"Internal server error: {str(e)}"
# #         )
    
# @app.post("/posts/", response_model=dict, status_code=status.HTTP_201_CREATED)
# async def create_post(post: PostCreate):
#     """Create a new post"""
#     try:
        
#         if not ObjectId.is_valid(post.user_id):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid user ID format"
#             )
        
#         #check if user exists
#         user = db.users_collection.find_one({"_id": ObjectId(post.user_id)})
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )

#         post_id = db.create_post(post.user_id, post.title, post.content)
#         if post_id:
#             return {"message": "Post created successfully", "post_id": post_id}
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Failed to create post"
#             )
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )
    
# @app.get("/posts/", response_model=List[PostResponse])
# async def get_all_posts():
#     """Get all posts"""
#     try:

#         posts = list(db.posts_collection.find().sort("created_at", -1))

#         #convert objectid to string for response
#         for post in posts:
#             post['_id'] = str(post['_id'])
#             post['user_id'] = str(post['user_id'])

#         return [
#             PostResponse(
#                 id=post['_id'],
#                 user_id=post['user_id'],
#                 title=post['title'],
#                 content=post['content'],
#                 created_at=post['created_at']
#             )
#             for post in posts
#         ]
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )

# @app.get("/users/{user_id}/posts", response_model=List[PostResponseForUser])
# async def get_user_posts(user_id: str):
#     """Get all posts by specific user"""
#     try:

#         if not ObjectId.is_valid(user_id):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid user ID format"
#             )

#         #check if user exists
#         user = db.users_collection.find_one({"_id": ObjectId(user_id)})
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )

#         posts = db.get_user_posts(user_id)
#         return [
#             PostResponseForUser(
#                 id=post['_id'],
#                 title=post['title'],
#                 content=post['content'],
#                 created_at=post['created_at'],
#             )
#             for post in posts
#         ]
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )

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

# @app.delete("/posts/{post_id}", response_model=dict)
# async def delete_post(post_id: str):
#     """Delete specific post"""
#     try:
#         if not ObjectId.is_valid(post_id):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid user ID format"
#             )
            
#         result = db.posts_collection.delete_one({"_id": ObjectId(post_id)})

#         if result.deleted_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Post not found"
#             )
            
#         return {"message": "Post deleted successfully"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )
    
# @app.put("/users/{user_id}", response_model=dict)
# async def update_user(user_id: str, user_update: UserUpdate):
#     """Update user by ID"""
#     try:

#         if not ObjectId.is_valid(user_id):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid user ID format"
#             )

#         #check if user exists
#         user = db.users_collection.find_one({"_id": ObjectId(user_id)})
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
            
#         #update user
#         result = db.users_collection.update_one(
#             {"_id": ObjectId(user_id)},
#             {"$set": {
#                 "name": user_update.name,
#                 "email": user_update.email,
#                 "age": user_update.age
#             }}
#         )

#         if result.modified_count > 0:
#             return {"message": "User updated successfully"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )
    
# @app.put("/posts/{post_id}", response_model=dict)
# async def update_post(post_id: str, title: str, content:str):#post: PostUpdate):
#     """Update post by post ID"""
#     try:

#         if not ObjectId.is_valid(post_id):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid post ID format"
#             )

#         #check if post exists
#         post = db.posts_collection.find_one({"_id": ObjectId(post_id)})
#         if not post:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="post not found"
#             )

#         #Update post    
#         result = db.posts_collection.update_one(
#             {"_id": ObjectId(post_id)},
#             {"$set": {
#                 "title": title,
#                 "content": content
#             }}
#         )
#         if result.modified_count > 0 :
#             return {"message": "Post updated successfully"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: {str(e)}"
#         )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)