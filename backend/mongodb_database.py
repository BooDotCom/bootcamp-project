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
        #Create unique index on date for transactions...?
        self.transaction_collection.create_index("date")

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
            }
            result = self.transaction_collection.insert_one(trans_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error: {e}")
            return None
                
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
        
    def get_balance_by_year(self, year):
        """Calculate balance for a specific year"""
        
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            # Get debit transactions
            debits = list(self.transaction_collection.find({
                "paid": "Yes",
                "transaction_type": "debit",
                "date": {"$gte": start_date, "$lte": end_date}
            }))
            
            # Get credit transactions
            credits = list(self.transaction_collection.find({
                "paid": "Yes",
                "transaction_type": "credit",
                "date": {"$gte": start_date, "$lte": end_date}
            }))
            
            debit_sum = sum(debit.get('amount', 0) for debit in debits)
            credit_sum = sum(credit.get('amount', 0) for credit in credits)
            balance = debit_sum - credit_sum
            
            return {"debit_sum": debit_sum, "credit_sum": credit_sum, "balance": balance}
        except Exception as e:
            print(f"Error calculating balance: {e}")
            return {"error": str(e)}

    def get_transaction_by_year(self, year, paid):
        """Get transactions for specific year."""
        try:
            start_date = datetime(year,1,1)
            end_date = datetime(year,12,31)

            trans = []
            if paid in ["paid", "yes"]:
                trans = list(self.transaction_collection.find({
                    "paid": "Yes",
                    "date":{
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }))
            elif paid in ["unpaid", "no"]:
                trans = list(self.transaction_collection.find({
                    "paid": "No",
                    "date":{
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }))
            else:
                trans = list(self.transaction_collection.find({
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

    def delete_transaction(self, tran_id):
        """Delete transaction"""
        try:
            #Convert string tran_id to ObjectId if it's a valid ObjectId
            if ObjectId.is_valid(tran_id):
                tran_object_id = ObjectId(tran_id)
            else:
                tran_object_id = tran_id

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
    print("4. View Transactions by Year")
    print("5. Delete Transaction")
    print("6. Exit")
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
        choice = input("Enter your choice (1-6): ").strip()

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

            if amount == 0:
                #skip input for these fields if unpaid
                transaction_type = "debit"
                description = ""
                paid = "No"
            else:
                paid = "Yes"
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
                    date = date.strptime(date_str, "%d-%m-%Y")
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
                    date = date.strptime(date_str, "%d-%m-%Y")
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

        elif choice == '5':
            print("\n--- Delete Transaction ---")

            tran_id = input("Enter transaction ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete transaction {tran_id}? (y/n): ").strip().lower()

            if confirm == 'y':
                if db.delete_transaction(tran_id):
                    print("Transaction deleted successfully")
                else:
                    print("Transaction not found or deletion failed.")
            else:
                print("Deletion cancelled")

        elif choice == '6':
            print("\nClosing database connection...")
            db.close_connection()
            print("\nGoodbye.")
            break

        else:
            print("Invalid choice. Please enter 1-5.")

        input("\nPress Enter to continue.")

if __name__ == "__main__":
    main()