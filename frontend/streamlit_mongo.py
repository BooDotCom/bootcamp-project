# #runtime order:
# #1: uvicorn fastapi_mongo:app
# #2: streamlit run streamlit_mongo.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, time
import json

#Configure the page
st.set_page_config(
    page_title="Raya Fund Tracker",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# #API base URL (make sure your fastapi server is running on this port)
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False
    
def create_transaction(name, amount, transaction_type, description, date):
    """Create a new transaction via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/transactions/",
            json={"name": name, "amount": amount, "transaction_type": transaction_type, "description": description, "date": date.isoformat()}
        )
        return response.json(), response.status_code == 201
    except Exception as e:
        return{"error": str(e)}, False
    
def get_all_transactions():
    """Get all transactions via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/")
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], False
    
# def update_user(user_id, name, email, age):
#     """Update a user via API"""
#     try:
#         response = requests.put(
#             f"{API_BASE_URL}/users/{user_id}",
#             json={"name": name, "email": email, "age": age}
#         )
#         return response.json(), response.status_code == 200
#     except Exception as e:
#         return {"error": str(e)}, False
    
# def delete_user(user_id):
#     """Delete a user via API"""
#     try:
#         response = requests.delete(f"{API_BASE_URL}/users/{user_id}")
#         return response.json(), response.status_code == 200
#     except Exception as e:
#         return{"error": str(e)}, False
    
# def create_post(user_id, title, content):
#     """Create a new user via API"""
#     try:
#         response = requests.post(
#             f"{API_BASE_URL}/posts/",
#             json={"user_id": user_id, "title": title, "content": content}
#         )
#         return response.json(), response.status_code == 201
#     except Exception as e:
#         return{"error": str(e)}, False

# def get_all_posts():
#     """Get all posts via API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/posts/")
#         if response.status_code == 200:
#             return response.json(), True
#         return [], False
#     except Exception as e:
#         return [], False

# def get_user_posts(user_id):
#     """Get all posts for specific user"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/users/{user_id}/posts")
#         if response.status_code == 200:
#             return response.json(), True
#         return [], False
#     except Exception as e:
#         return [], False

# def delete_post(post_id):
#     """Delete a post via API"""
#     try:
#         response = requests.delete(f"{API_BASE_URL}/posts/{post_id}")
#         return response.json(), response.status_code == 200
#     except Exception as e:
#         return{"error": str(e)}, False

def main():
    st.title("🔎 Raya Fund Tracker")
    st.markdown("---")

    #check API connection
    if not check_api_connection():
        st.error("Cannot connect to FastAPI server. Please make sure it's running on http://localhost:8000")
        st.info("Run 'python fastapi_mongo.py' to start the server")
        return
    
    #Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["👥 Transactions", "☰ Dashboard"]
    )

    if page == "👥 Transactions":
        transactions_page()
#     elif page == "☰ Dashboard":
#         dashboard_page()

def transactions_page():
    st.header("👥 Transaction Management")

    #Create tabs for different transaction operations
    tab1, tab2, tab3 = st.tabs(["Create Transaction", "View Transactions", "Manage Transactions"])

    with tab1:
        st.subheader("Create New Transaction")
        with st.form("create_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", placeholder="Enter your name")
                amount = st.number_input("Amount", min_value=0, value=0)
                date = st.date_input("Select date")
            with col2:
                transaction_type = st.selectbox("Transaction Type", ["Debit", "Credit"], placeholder="Select transaction type")
                description = st.text_input("Description", placeholder="Enter description")
            
            submitted = st.form_submit_button("Create Transaction", type="primary")

            if submitted:
                if name:
                    # paid = "Yes" if amount > 0 else "No"
                    date_obj = datetime.combine(date,time.min)
                    result, success = create_transaction(name, amount, transaction_type, description, date_obj)
                    # st.json(result)
                    if success:
                        st.success(f"Transaction created successfully! ID: {result.get('tran_id')}")
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('detail', 'Unknown error')}")
                else:
                    st.error("Please fill in name.")

#     with tab2:
#         st.subheader("All Users")
#         users, success = get_all_users()

#         if success and users:
#             #Convert to DataFrame for better display
#             df = pd.DataFrame(users)
#             df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

#             #Display users in a table
#             st.dataframe(
#                 df[['id', 'name', 'email', 'age', 'created_at']],
#                 use_container_width=True,
#                 hide_index=True
#             )

#             #Show user count
#             st.info(f"Total users: {len(users)}")
#         else:
#             st.info("No users found")

#     with tab3:
#         st.subheader("Manage Users")
#         users, success = get_all_users()

#         if success and users:
#             #Select user to merge
#             user_options = {f"{user['name']} ({user['email']})": user['id'] for user in users}
#             selected_user_display = st.selectbox("Select a user to manage", list(user_options.keys()))

#             if selected_user_display:
#                 selected_user_id = user_options[selected_user_display]
#                 selected_user = next(user for user in users if user['id'] == selected_user_id)

#                 col1, col2 = st.columns(2)

#                 with col1:
#                     st.write("**Update User**")
#                     with st.form("update_user_form"):
#                         new_name = st.text_input("Name", value=selected_user['name'])
#                         new_email = st.text_input("Email", value=selected_user['email'])
#                         new_age = st.number_input("Age", min_value=1, max_value=120, value=selected_user['age'])

#                         if st.form_submit_button("Update User", type = "primary"):
#                             result, success = update_user(selected_user_id, new_name, new_email, new_age)
#                             if success:
#                                 st.success("User updated successfully")
#                                 st.rerun()
#                             else:
#                                 st.error(f"Error: {result.get('detail', 'Unknown error')}")

#                 with col2:
#                     st.write("**Delete User**")
#                     st.warning("⚠️ WARNING This will delete the user and all their posts!")
                    
#                     if st.button("Delete User", type = "secondary"):
#                         result, success = delete_user(selected_user_id)
#                         if success:
#                             st.success("User deleted successfully")
#                             st.rerun()
#                         else:
#                             st.error(f"Error: {result.get('detail', 'Unknown error')}")

# def dashboard_page():
#     st.header("☰ Dashboard")

#     #Get data for dashboard
#     users, users_success = get_all_users()
#     posts, posts_success = get_all_posts()

#     if users_success and posts_success:
#         #Metrics
#         col1, col2, col3, col4 = st.columns(4)

#         with col1:
#             st.metric("Total Users", len(users))

#         with col2:
#             st.metric("Total Posts", len(posts))
        
#         with col3:
#             avg_age = sum(user['age'] for user in users) / len(users) if users else 0
#             st.metric("Average Age", f"{avg_age:.1f}")

#         with col4:
#             posts_per_user = len(posts) / len(users) if users else 0
#             st.metric("Posts per User", f"{posts_per_user:.1f}")

#         st.markdown("---")

#         #Charts
#         if users:
#             col1, col2 = st.columns(2)

#             with col1:
#                 st.subheader("Age Distribution")
#                 age_data = [user['age'] for user in users]
#                 st.bar_chart(pd.Series(age_data).value_counts().sort_index())

#             with col2:
#                 st.subheader("Recent Activity")
#                 if posts:
#                     #Posts by date
#                     posts_df = pd.DataFrame(posts)
#                     posts_df['date'] = pd.to_datetime(posts_df['created_at']).dt.date
#                     daily_posts = posts_df.groupby('date').size()
#                     st.line_chart(daily_posts)

#         #Recent posts
#         st.subheader("Recent Posts")
#         if posts:
#             recent_posts = sorted(posts, key=lambda x: x['created_at'], reverse=True)[:5]
#             for post in recent_posts:
#                 st.write(f"- **{post['title']}** - {pd.to_datetime(post['created_at']).strftime('%Y-%m-%d %H:%M')}")
#     else:
#         st.error("Failed to load dashboard data")

if __name__ == "__main__":
    main()