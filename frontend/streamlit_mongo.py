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
    
def get_transactions_by_year(year, paid):
    """Get transactions by year via API"""
    try:
        
        if paid == "Paid":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/paid/",
                json={"year": year, "paid": paid}
                )
        elif paid == "Unpaid":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/unpaid/",
                json={"year": year, "paid": paid}
                )
        elif paid == "All":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/",
                json={"year": year}
                )
        
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], False

def update_transaction(tran_id, name, amount, transaction_type, description, date):
    """Update a transaction via API"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/transactions/{tran_id}",
            json={"name": name, "amount": amount, "transaction_type": transaction_type, "description": description, "date": date.isoformat()}
        )
        return response.json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False
    
def delete_transaction(tran_id):
    """Delete a transaction via API"""
    try:
        response = requests.delete(f"{API_BASE_URL}/transactions/{tran_id}")
        return response.json(), response.status_code == 200
    except Exception as e:
        return{"error": str(e)}, False
    
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
    elif page == "📅 Annual":
        annual_page()

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

    with tab2:
        st.subheader("All Transactions")
        trans, success = get_all_transactions()

        if success and trans:
            #Convert to DataFrame for better display
            df = pd.DataFrame(trans)
            try:
                df['date'] = pd.to_datetime(df['date'], format='ISO8601').dt.strftime('%d-%m-%Y %H:%M:%S')
            except Exception as e:
                st.warning(f"Date formatting issue: {e}")

            #Display users in a table
            st.dataframe(
                df[['id', 'name', 'amount', 'transaction_type', 'description', 'paid', 'date']],
                use_container_width=True,
                hide_index=True
            )

            #Show user count
            # st.info(f"Total users: {len(users)}")
        else:
            st.info("No transactions found")

    with tab3:
        st.subheader("Manage Transactions")
        trans, success = get_all_transactions()

        if success and trans:
            #Select user to merge
            tran_options = {f"{tran['name']} ({tran['date']})": tran['id'] for tran in trans}
            selected_tran_display = st.selectbox("Select a transaction to manage", list(tran_options.keys()))

            if selected_tran_display:
                selected_tran_id = tran_options[selected_tran_display]
                selected_tran = next(tran for tran in trans if tran['id'] == selected_tran_id)

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Update Transaction**")
                    with st.form("update_transaction_form"):
                        new_name = st.text_input("Name", value=selected_tran['name'])
                        new_amount = st.number_input("Amount", min_value=0, value=selected_tran['amount'])
                        new_tran_type = st.text_input("Transaction Type", value=selected_tran['transaction_type'])
                        new_desc = st.text_input("Description", value=selected_tran['description'])
                        new_date = st.date_input("Date", value=selected_tran['date'])

                        if st.form_submit_button("Update Transaction", type = "primary"):
                            result, success = update_transaction(selected_tran_id, new_name, new_amount, new_tran_type, new_desc, new_date)
                            if success:
                                st.success("Transaction updated successfully")
                                st.rerun()
                            else:
                                st.error(f"Error: {result.get('detail', 'Unknown error')}")

                with col2:
                    st.write("**Delete Transaction**")
                    st.warning("⚠️ WARNING This will delete the transaction!")
                    
                    if st.button("Delete Transaction", type = "secondary"):
                        result, success = delete_transaction(selected_tran_id)
                        if success:
                            st.success("Transaction deleted successfully")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('detail', 'Unknown error')}")

def annual_page():
    st.header("📅 Annual Transactions")

    with st.form("get_annual_form"):
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Year", min_value=2000, max_value=2050, value=2026)
        with col2:
            paid = st.selectbox("Pay Status", ["All", "Paid", "Unpaid"], placeholder="Select pay status")

        submit = st.form_submit_button("View Transactions", type="primary")

    st.markdown('---')

    if submit:
        if year:
            trans, success = get_transactions_by_year(year, paid)

            if success and trans:
                #Convert to DataFrame for better display
                df = pd.DataFrame(trans)
                try:
                    df['date'] = pd.to_datetime(df['date'], format='ISO8601').dt.strftime('%d-%m')
                except Exception as e:
                    st.warning(f"Date formatting issue: {e}")

                #Display users in a table
                if paid == "Paid":
                    st.dataframe(
                        df[['id', 'name', 'amount', 'transaction_type', 'description', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )
                if paid == "Unpaid":
                    st.dataframe(
                        df[['id', 'name', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )
                if paid == "All":
                    st.dataframe(
                        df[['id', 'name', 'amount', 'transaction_type', 'description', 'paid', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )

                #Show user count
                # st.info(f"Total users: {len(users)}")
            else:
                st.info("No transactions found")
        else:
            st.error("Please fill in year.")
            
            

#     #Get data for dashboard
#     # users, users_success = get_all_users()
#     # posts, posts_success = get_all_posts()

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