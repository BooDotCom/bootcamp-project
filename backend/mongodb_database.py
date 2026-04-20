from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv

import os

load_dotenv()

mongo_uri = os.getenv('MONGODB_ATLAS_CLUSTER_URI')

class DatabaseManager:
    def __init__(self, db_name = 'fundtracker_db', connection_string=mongo_uri):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.transaction_collection = self.db.transactions
        self.init_database()

    def init_database(self):
        """Initialize database with collections and indexes"""
        #Create unique index on email for users
        self.transaction_collection.create_index("date")
        #create index on user_id for posts for better query performance
        # self.posts_collection.create_index("user_id")

#Create data (INSERT) function
    def create_transaction(self, name, amount, transaction_type, description, paid, date):
        """Create a new user"""
        try:
            trans_doc = {
                "name": name,
                "amount": amount,
                "transaction_type": transaction_type,
                "description": description,
                "paid": paid,
                "date": date
                # "created_at": datetime.now()
            }
            result = self.transaction_collection.insert_one(trans_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    # def create_post(self, user_id, title, content):
    #     """Create a new post"""
    #     try:
    #         #Convert string user_id to ObjectId if it's a valid ObjectId
    #         if ObjectId.is_valid(user_id):
    #             user_object_id = ObjectId(user_id)
    #         else:
    #             user_object_id = user_id

    #         post_doc = {
    #             "user_id": user_object_id,
    #             "title": title,
    #             "content": content,
    #             "created_at": datetime.now()
    #         }
    #         result = self.posts_collection.insert_one(post_doc)
    #         return str(result.inserted_id)
    #     except Exception as e:
    #         print(f"Error creating post: {e}")
    #         return None
        
    # def get_all_transactions(self):
    #     """Get all transactions"""
    #     try:
    #         trans = list(self.transaction_collection.find())
    #         #Convert ObjectId to string for display
    #         for tran in trans:
    #             tran['_id'] = str(tran['_id'])
    #         return trans
    #     except Exception as e:
    #         print(f"Error fetching transactions: {e}")
    #         return []
        
    # def get_user_posts(self, user_id):
    #     """Get posts by user"""
    #     try:
    #         #Convert string user_id to ObjectId if it's a valid ObjectId
    #         if ObjectId.is_valid(user_id):
    #             user_object_id = ObjectId(user_id)
    #         else:
    #             user_object_id = user_id

    #         posts = list(self.posts_collection.find(
    #             {"user_id": user_object_id}
    #         ).sort("created_at", -1))
            
    #         #Convert ObjectId to string for display
    #         for post in posts:
    #             post['_id'] = str(post['_id'])
    #         return posts
        
    #     except Exception as e:
    #         print(f"Error fetching users: {e}")
    #         return []
        
    # def update_transaction(self,tran_id, name, transaction_type, description, paid, date):
    #     """Update existing transaction Id"""
    #     try:
    #         result = self.transaction_collection.update_one(
    #             {"_id": ObjectId(tran_id)},
    #             {"$set": {
    #                 "name": name,
    #                 "transaction_type": transaction_type,
    #                 "description": description,
    #                 "paid": paid,
    #                 "date": date
    #             }}
    #         )
    #         return result.modified_count
        
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return None

    # def update_post(self,user_id, title, content):
    #     """Update existing post based on user ID"""
    #     try:
    #         result = self.users_collection.update_one(
    #             {"_id": ObjectId(user_id)},
    #             {"$set": {
    #                 "title": title,
    #                 "content": content,
    #                 "updated_at": datetime.now()
    #             }}
    #         )
    #         return result.modified_count
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return None


    # def delete_user(self, tran_id):
    #     """Delete transaction"""
    #     try:
    #         #Convert string user_id to ObjectId if it's a valid ObjectId
    #         if ObjectId.is_valid(tran_id):
    #             tran_object_id = ObjectId(tran_id)
    #         else:
    #             tran_object_id = tran_id

    #         #Delete user's posts first
    #         # self.posts_collection.delete_many({"user_id": user_object_id})

    #         #Delete the user
    #         result = self.transaction_collection.delete_one({"_id": tran_object_id})

    #         return result.deleted_count > 0
        
    #     except Exception as e:
    #         print(f"Error deleting transaction: {e}")
    #         return False
    
    def close_connection(self):
        """Close the MongoDB connection"""
        self.client.close()
         
def display_menu():
    """Display the main menu"""
    print("\n" + "="*40)
    print("         DATABASE MANAGER")
    print("="*40)
    print("1. Create Transaction")
    print("2. Update Transaction")
    print("3. View All Transactions")
    print("4. Delete Transaction")
    print("5. Exit")
    print("-"*40)

def main():
    """Main interactive CLI function"""
    try:
        db = DatabaseManager()
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print(f"Make sure MongoDB is running on localhost:27017")
        return

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':

            print("\n--- Create New Transaction ---")
            name = input("Enter name: ").strip()
            while True:
                try:
                    amount = int(input("Enter amount: ").strip())
                    if amount <0:
                        raise ValueError("Amount must not be negative.")
                    break
                except ValueError as e:
                    print(f"Invalid amount: {e}. Please enter a number.")

            paid = "Yes" if amount > 0 else "No"

            if amount == 0:
                #skip input for these fields if unpaid
                transaction_type = ""
                description = ""
                date = None
            else:
                while True:
                    transaction_type = input("Enter transaction type(Debit or Credit): ").strip().lower()
                    if transaction_type in ["debit", "credit"]:
                        break
                    print("Transaction type can only be Debit or Credit.")
                
                description = input("Enter description: ").strip()
                
                while True:
                    date_str = input("Enter date of transaction: ").strip()
                    date_str = date_str.replace("/", "-")
                    try:
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                        break
                    except ValueError:
                        print("Please enter a valid date.")

            tran_id = db.create_transaction(name, amount, transaction_type, description, paid, date)
            if tran_id:
                print(f"Transaction created successfully! ID: {tran_id}")
            else:
                print("Failed to create transaction.")

            # try:
            #     age = int(input("Enter age: ").strip())
            #     tran_id = db.create_transaction(name, amount, transaction_type, description, paid, date)
            #     if tran_id:
            #         print(f"Transaction created successfully! ID: {tran_id}")
            #     else:
            #         print("Failed to create transaction.")
            # except ValueError:
            #     print("Invalid age. Please enter a number.")

        elif choice == '2':
            print("Not there yet.")
            # print("\n--- Update User ---")

            # user_id = input("Enter user ID to update: ").strip()
            # name = input("Enter new name: ").strip()
            # email = input("Enter new email: ").strip()
            # try:
            #     age = int(input("Enter new age: ").strip())

            #     user_updated = db.update_user(user_id, name, email, age)
            #     if user_updated:
            #         print(f"User {user_id} updated successfully!")
            #     else:
            #         print("No user found with that ID.")
            # except ValueError:
            #     print("Invalid input. Please enter numbers for age.")

        elif choice == '3':
            print("Not there yet.")
            # print("\n--- All Users ---")
            # users = db.get_all_users()
            # if users:
            #     for user in users:
            #         print(f"ID: {user['_id']} | Name: {user['name']} | Email: {user['email']} | Age: {user['age']}")
            # else:
            #     print("No users found.")

        elif choice == '4':
            print("Not there yet.")
            # print("\n--- Create New Post ---")

            # user_id = input("Enter user ID: ").strip()
            # title = input("Enter post title: ").strip()
            # content = input("Enter post content: ").strip()
            # post_id = db.create_post(user_id, title, content)
            # if post_id:
            #     print(f"Post created successfully! ID: {post_id}")
            # else:
            #     print("Failed to create post")

        # elif choice == '5':
        #     print("Not there yet")
            
            # print("\n--- Update post ---")
            # user_id = int(input("Enter user ID to update: ").strip())
            # title = input("Enter new title: ").strip()
            # content = input("Enter new content: ").strip()

            # post_updated = db.update_post(user_id, title, content)
            # if post_updated:
            #     print(f"Post for User {user_id} updated successfully!")
            # else:
            #     print("No user found with that ID.")
            
        # elif choice == '6':
            # print("\n--- View User Posts ---")
            # user_id = input("Enter user ID: ").strip()
            # posts = db.get_user_posts(user_id)

            # if posts:
            #     for post in posts:
            #         print(f"\nPost ID: {post['_id']}")
            #         print(f"Title: {post['title']}")
            #         print(f"Content: {post['content']}")
            #         print(f"Created: {post['created_at']}")
            #         print("-"*30)
            # else:
            #     print("No posts found for this user.")

        # elif choice == '7':
        #     print("\n--- Delete User ---")

        #     user_id = input("Enter user ID to delete: ").strip()
        #     confirm = input(f"Are you sure you want to delete user {user_id}? (y/n): ").strip().lower()

        #     if confirm == 'y':
        #         if db.delete_user(user_id):
        #             print("User deleted successfully")
        #         else:
        #             print("User not found or deletion failed.")
        #     else:
        #         print("Deletion cancelled")

        elif choice == '5':
            print("\nClosing database connection...")
            db.close_connection()
            print("\nGoodbye.")
            break

        else:
            print("Invalid choice. Please enter 1-5.")

        input("\nPress Enter to continue.")

if __name__ == "__main__":
    main()