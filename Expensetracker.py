import streamlit as st
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

#basic categories
categories = ["Food", "Grocery", "Bills", "Miscellaneous"]
st.set_page_config(page_title="Expense Tracker", layout="centered")

#Email handling
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if st.session_state.user_email == "":
    st.title("Hey! Let's track your expenses")
    email_input = st.text_input("What's your email?")
    
    if email_input:
        if "@" in email_input and "." in email_input:
            st.session_state.user_email = email_input
            st.rerun()
        else:
            st.warning("Enter valid email")
else:
    filename = f"expenses_{st.session_state.user_email}.json"
    
    #load or create data
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {"expenses": [], "budgets": {}}
    else:
        data = {"expenses": [], "budgets": {}}

    #save function
    #saving as json file for each user, adding the email to filename to track.
    #json stored locally

    def save():
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    st.sidebar.title("Menu")
    choice = st.sidebar.radio("Pick an option", ["Add Expense", "Set Monthly Budget", "View Report"])

    st.title("Your Expense Tracker")

    if choice == "Add Expense":
        st.header("Add a New Expense")

        expense_date = st.date_input("When did you spend?", datetime.today()).strftime("%Y-%m-%d")
        selected_category = st.selectbox("What was it for?", categories)
        amount_spent = st.number_input("How much did it cost?", min_value=0.0, step=1.0)

        if st.button("Log It"):
            if amount_spent > 0:
                data["expenses"].append({
                    "date": expense_date,
                    "category": selected_category,
                    "amount": amount_spent
                })
                save()
                st.success(f"Added ₹{amount_spent} to {selected_category}")
            else:
                st.error("Enter a positive amount, please.")

    elif choice == "Set Monthly Budget":
        st.header("Set Your Budgets")

        cat_to_budget = st.selectbox("Category", categories)
        budget_amount = st.number_input("Monthly limit (₹)", min_value=0.0, step=1.0)

        if st.button("Save Budget"):
            if budget_amount > 0:
                data["budgets"][cat_to_budget] = budget_amount
                save()
                st.success(f"Budget for {cat_to_budget} set to ₹{budget_amount}")
            else:
                st.warning("Enter something more than zero")

    elif choice == "View Report":
        st.header("Monthly Report")

        # Group expenses
        monthly_summary = {}
        for entry in data["expenses"]:
            month_key = entry["date"][:7]
            if month_key not in monthly_summary:
                monthly_summary[month_key] = {}
            if entry["category"] not in monthly_summary[month_key]:
                monthly_summary[month_key][entry["category"]] = 0
            monthly_summary[month_key][entry["category"]] += entry["amount"]

        if monthly_summary:
            months_available = sorted(monthly_summary.keys(), reverse=True)
            selected_month = st.selectbox("Pick a month", months_available)
            month_data = monthly_summary[selected_month]
            st.write(f"### You spent ₹{sum(month_data.values()):.2f} in {selected_month}")

            for cat in categories:
                spent = month_data.get(cat, 0.0)
                budget = data["budgets"].get(cat)
                if budget:
                    st.write(f"{cat}: ₹{spent:.2f} / ₹{budget}")
                    if spent > budget:
                        st.error(f"Warning: Over budget for {cat}!")
                else:
                    st.write(f"{cat}: ₹{spent:.2f} (No budget set)")

            if any(month_data.values()):
                st.subheader("Pie Chart of Spending")
                fig, ax = plt.subplots()
                ax.pie(month_data.values(), labels=month_data.keys(), autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
        else:
            st.info("No expenses logged yet.")

    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.user_email = ""
        st.rerun()