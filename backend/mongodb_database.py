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
        
    def get_all_transactions(self):
        """Get all transactions"""
        try:
            trans = list(self.transaction_collection.find())
            #Convert ObjectId to string for display
            for tran in trans:
                tran['_id'] = str(tran['_id'])
            return trans
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
        
    def get_transaction_by_year(self, year, paid):
        """Get transactions for specific year."""
        try:
            start_date = datetime(year,1,1)
            end_date = datetime(year,12,31)

            if paid == "paid":
                trans = list(self.transaction_collection.find({
                    "paid": "Yes",
                    "date":{
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }))
            elif paid == "unpaid":
                trans = list(self.transaction_collection.find({
                    "paid": "No",
                    "date":{
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }))
            for tran in trans:
                tran['_id'] = str(tran['_id'])
            return trans
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []

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
        
    def update_transaction(self,tran_id, name, amount, transaction_type, description, paid, date):
        """Update existing transaction Id"""
        try:
            result = self.transaction_collection.update_one(
                {"_id": ObjectId(tran_id)},
                {"$set": {
                    "name": name,
                    "amount": amount,
                    "transaction_type": transaction_type,
                    "description": description,
                    "paid": paid,
                    "date": date
                }}
            )
            return result.modified_count
        
        except Exception as e:
            print(f"Error: {e}")
            return None

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


    def delete_transaction(self, tran_id):
        """Delete transaction"""
        try:
            #Convert string user_id to ObjectId if it's a valid ObjectId
            if ObjectId.is_valid(tran_id):
                tran_object_id = ObjectId(tran_id)
            else:
                tran_object_id = tran_id

            #Delete user's posts first
            # self.posts_collection.delete_many({"user_id": user_object_id})

            #Delete the user
            result = self.transaction_collection.delete_one({"_id": tran_object_id})

            return result.deleted_count > 0
        
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
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
    print("4. View Paid Transactions by Year")
    print("5. View Unpaid Transactions")
    print("6. Delete Transaction")
    print("7. Exit")
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
        choice = input("Enter your choice (1-7): ").strip()

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
                transaction_type = "debit"
                description = ""
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

        elif choice == '2':
            # print("Not there yet.")
            print("\n--- Update Transaction ---")

            tran_id = input("Enter transaction ID to update: ").strip()
            name = input("Enter new name: ").strip()

            while True:
                try:
                    amount = int(input("Enter new amount: ").strip())
                    if amount <0:
                        raise ValueError("Amount must not be negative.")
                    break
                except ValueError as e:
                    print(f"Invalid amount: {e}. Please enter a number.")

            paid = "Yes" if amount > 0 else "No"

            if amount == 0:
                #skip input for these fields if unpaid
                transaction_type = "debit"
                description = ""
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

            tran_updated = db.update_transaction(tran_id, name, amount, transaction_type, description, paid, date)
            if tran_updated:
                print(f"Transaction {tran_id} updated successfully!")
            else:
                print("No transaction found with that ID.")

        elif choice == '3':
            # print("Not there yet.")
            print("\n--- All Transactions ---")
            trans = db.get_all_transactions()
            if trans:
                for tran in trans:
                    print(f"ID: {tran['_id']} | Name: {tran['name']} | Amount: {tran['amount']} | Transaction Type: {tran['transaction_type']} | Description: {tran['description']} | Paid: {tran['paid']} | Date: {tran['date']}")
            else:
                print("No transactions found.")

        elif choice == '4':
            # print("Not there yet.")
            print("\n--- Transactions by Year ---")

            try:
                year = int(input("Enter year: ").strip())
            except ValueError:
                print("Invalid year. Please enter a valid number.")
            
            while True:
                paid = input("Do you want to check for paid or unpaid: ").strip().lower()
                if paid in ["paid", "unpaid"]:
                    if paid == "paid":
                        trans = db.get_transaction_by_year(year, paid)
                        if trans:
                            for tran in trans:
                                print(f"ID: {tran['_id']} | Name: {tran['name']} | Amount: {tran['amount']} | Date: {tran['date']}")
                            break
                        else:
                            print(f"No paid transactions found for year {year}.")
                            break
                    elif paid == "unpaid":
                        trans = db.get_transaction_by_year(year, paid)
                        if trans:
                            for tran in trans:
                                print(f"ID: {tran['_id']} | Name: {tran['name']} | Date: {tran['date']}")
                            break
                        else:
                            print(f"No paid transactions found for year {year}.")
                            break
                else:
                    print("Please type 'paid' or 'unpaid'")

        # elif choice == '5':
        #     # print("Not there yet")
            
        #     print("\n--- Unpaid Transactions ---")
        #     trans = db.get_unpaid_by_year()
        #     if trans:
        #         for tran in trans:
        #             print(f"ID: {tran['_id']} | Name: {tran['name']} | Date: {tran['date']}")
        #     else:
        #         print("No unpaid transactions found.")

            
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

        elif choice == '6':
            print("\n--- Delete Transaction ---")

            tran_id = input("Enter user ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete user {tran_id}? (y/n): ").strip().lower()

            if confirm == 'y':
                if db.delete_transaction(tran_id):
                    print("Transaction deleted successfully")
                else:
                    print("Transaction not found or deletion failed.")
            else:
                print("Deletion cancelled")

        elif choice == '7':
            print("\nClosing database connection...")
            db.close_connection()
            print("\nGoodbye.")
            break

        else:
            print("Invalid choice. Please enter 1-5.")

        input("\nPress Enter to continue.")

if __name__ == "__main__":
    main()