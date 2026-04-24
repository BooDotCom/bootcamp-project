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

def get_balance_by_year(year):
    """Get balance for year via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/balance/{year}")
        if response.status_code == 200:
            return response.json(), True
        return response.json(), False
    except Exception as e:
        return {"error": str(e)}, False

def get_transactions_by_year(year, paid):
    """Get transactions by year via API"""
    try:
        
        if paid == "Paid":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/paid/?year={year}&paid=yes",
                )
        elif paid == "Unpaid":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/unpaid/?year={year}&paid=no",
                )
        elif paid == "All":
            response = requests.get(
                f"{API_BASE_URL}/transactions/by-year/?year={year}",
                )
        
        if response.status_code == 200:
            return response.json(), True
        # return [], False
        return response.json(), False
    except Exception as e:
        # return [], False
        return {"error": str(e)}, False

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
        ["💰 Transactions", "📅 Annual"]
    )

    if page == "💰 Transactions":
        transactions_page()
    elif page == "📅 Annual":
        annual_page()

def transactions_page():
    st.header("💰 Transaction Management")

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
                    transaction_type = transaction_type.lower()
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
                df[['name', 'amount', 'transaction_type', 'description', 'paid', 'date']],
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No transactions found")

    with tab3:
        st.subheader("Manage Transactions")
        trans, success = get_all_transactions()

        if success and trans:
            #Select user to merge
            tran_options = {f"{tran['name']} ({datetime.fromisoformat(tran['date']).date()})": tran['id'] for tran in trans}
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
                        new_tran_type = st.selectbox("Transaction Type", ["Debit", "Credit"], placeholder="Select transaction type")
                        new_desc = st.text_input("Description", value=selected_tran['description'])
                        new_date = st.date_input("Date", value=selected_tran['date'])

                        if st.form_submit_button("Update Transaction", type = "primary"):
                            new_tran_type = new_tran_type.lower()
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
            balance, balance_success = get_balance_by_year(year)

            if balance_success and "error" not in balance:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Debit: ", f"RM{balance['debit_sum']}")
                col1.metric("Total Credit: ", f"RM{balance['credit_sum']}")
                col1.metric("Balance: ", f"RM{balance['balance']}")

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
                        df[['name', 'amount', 'transaction_type', 'description', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )
                if paid == "Unpaid":
                    st.dataframe(
                        df[['name', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )
                if paid == "All":
                    st.dataframe(
                        df[['name', 'amount', 'transaction_type', 'description', 'paid', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )

            else:
                st.info("No transactions found")
        else:
            st.error("Please fill in year.")
            
if __name__ == "__main__":
    main()