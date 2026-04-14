from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv

import os

load_dotenv()

mongo_uri = os.getenv('MONGODB_ATLAS_CLUSTER_URI')

class DatabaseManager:
    def __init__(self, db_name = 'example_db', connection_string=mongo_uri):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.users_collection = self.db.users
        self.posts_collection = self.db.posts
        self.init_database()

    def init_database(self):
        """Initialize database with collections and indexes"""
        #Create unique index on email for users
        self.users_collection.create_index("email", unique = True)
        #create index on user_id for posts for better query performance
        self.posts_collection.create_index("user_id")

#Create data (INSERT) function
    def create_user(self, name, email, age):
        """Create a new user"""
        try:
            user_doc = {
                "name": name,
                "email": email,
                "age": age,
                "created_at": datetime.now()
            }
            result = self.users_collection.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def create_post(self, user_id, title, content):
        """Create a new post"""
        try:
            #Convert string user_id to ObjectId if it's a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            post_doc = {
                "user_id": user_object_id,
                "title": title,
                "content": content,
                "created_at": datetime.now()
            }
            result = self.posts_collection.insert_one(post_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
        
    def get_all_users(self):
        """Get all users"""
        try:
            users = list(self.users_collection.find())
            #Convert ObjectId to string for display
            for user in users:
                user['_id'] = str(user['_id'])
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        
    def get_user_posts(self, user_id):
        """Get posts by user"""
        try:
            #Convert string user_id to ObjectId if it's a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            posts = list(self.posts_collection.find(
                {"user_id": user_object_id}
            ).sort("created_at", -1))
            
            #Convert ObjectId to string for display
            for post in posts:
                post['_id'] = str(post['_id'])
            return posts
        
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        
    def update_user(self,user_id, name, email, age):
        """Update existing user Id"""
        try:
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "name": name,
                    "email": email,
                    "age": age,
                    "updated_at": datetime.now()
                }}
            )
            return result.modified_count
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def update_post(self,user_id, title, content):
        """Update existing post based on user ID"""
        try:
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "title": title,
                    "content": content,
                    "updated_at": datetime.now()
                }}
            )
            return result.modified_count
        except Exception as e:
            print(f"Error: {e}")
            return None


    def delete_user(self, user_id):
        """Delete user and their posts"""
        try:
            #Convert string user_id to ObjectId if it's a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            #Delete user's posts first
            self.posts_collection.delete_many({"user_id": user_object_id})

            #Delete the user
            result = self.users_collection.delete_one({"_id": user_object_id})

            return result.deleted_count > 0
        
        except Exception as e:
            print(f"Error deleteing user: {e}")
            return False
    
    def close_connection(self):
        """Close the MongoDB connection"""
        self.client.close()
         
def display_menu():
    """Display the main menu"""
    print("\n" + "="*40)
    print("         DATABASE MANAGER")
    print("="*40)
    print("1. Create User")
    print("2. Update User")
    print("3. View All Users")
    print("4. Create Post")
    print("5. Update Post")
    print("6. View User Posts")
    print("7. Delete User")
    print("8. Exit")
    print("-"*40)

def main():
    """Main interactive CLI function"""
    try:
        db = DatabaseManager()
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failec to connect to MongoDB: {e}")
        print(f"Make sure MongoDB is running on localhost:27017")
        return

    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':

            print("\n--- Create New User ---")
            name = input("Enter name: ").strip()
            email = input("Enter email: ").strip()

            try:
                age = int(input("Enter age: ").strip())
                user_id = db.create_user(name, email, age)
                if user_id:
                    print(f"User created successfully! ID: {user_id}")
                else:
                    print("Failed to create user")
            except ValueError:
                print("Invalid age. Please enter a number.")

        elif choice == '2':
            # print("Not there yet.")
            print("\n--- Update User ---")

            user_id = input("Enter user ID to update: ").strip()
            name = input("Enter new name: ").strip()
            email = input("Enter new email: ").strip()
            try:
                age = int(input("Enter new age: ").strip())

                user_updated = db.update_user(user_id, name, email, age)
                if user_updated:
                    print(f"User {user_id} updated successfully!")
                else:
                    print("No user found with that ID.")
            except ValueError:
                print("Invalid input. Please enter numbers for age.")

        elif choice == '3':
            print("\n--- All Users ---")
            users = db.get_all_users()
            if users:
                for user in users:
                    print(f"ID: {user['_id']} | Name: {user['name']} | Email: {user['email']} | Age: {user['age']}")
            else:
                print("No users found.")

        elif choice == '4':
            print("\n--- Create New Post ---")

            user_id = input("Enter user ID: ").strip()
            title = input("Enter post title: ").strip()
            content = input("Enter post content: ").strip()
            post_id = db.create_post(user_id, title, content)
            if post_id:
                print(f"Post created successfully! ID: {post_id}")
            else:
                print("Failed to create post")

        elif choice == '5':
            # print("Not there yet")
            
            print("\n--- Update post ---")
            user_id = int(input("Enter user ID to update: ").strip())
            title = input("Enter new title: ").strip()
            content = input("Enter new content: ").strip()

            post_updated = db.update_post(user_id, title, content)
            if post_updated:
                print(f"Post for User {user_id} updated successfully!")
            else:
                print("No user found with that ID.")
            
        elif choice == '6':
            print("\n--- View User Posts ---")
            user_id = input("Enter user ID: ").strip()
            posts = db.get_user_posts(user_id)

            if posts:
                for post in posts:
                    print(f"\nPost ID: {post['_id']}")
                    print(f"Title: {post['title']}")
                    print(f"Content: {post['content']}")
                    print(f"Created: {post['created_at']}")
                    print("-"*30)
            else:
                print("No posts found for this user.")

        elif choice == '7':
            print("\n--- Delete User ---")

            user_id = input("Enter user ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete user {user_id}? (y/n): ").strip().lower()

            if confirm == 'y':
                if db.delete_user(user_id):
                    print("User deleted successfully")
                else:
                    print("User not found or deletion failed.")
            else:
                print("Deletion cancelled")

        elif choice == '8':
            print("\nClosing database connection...")
            db.close_connection()
            print("\nGoodbye.")
            break

        else:
            print("Invalid choice. Please enter 1-8.")

        input("\nPress Enter to continue.")

if __name__ == "__main__":
    main()