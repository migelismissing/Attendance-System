# sheets_helper.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Authenticate with Google Sheets
def connect_to_sheet():
    # Define the scope of the application
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    
    # Use the ServiceAccountCredentials to authenticate
    creds = ServiceAccountCredentials.from_json_keyfile_name("ATTENDANCECHECKER/attendancesystem-443309-b7a6d64cef33.json", scope)
    
    # Authorize the client and open the Google Sheets document
    client = gspread.authorize(creds)
    
    # Open the Google Sheets document by name
    return client.open("Attendance System")  # Replace with your sheet name

def validate_login(user_type, email, password):
    sheet = connect_to_sheet().worksheet(user_type)  # Access the sheet for 'students' or 'faculty'
    users = pd.DataFrame(sheet.get_all_records())    # Get all records (user data) as a DataFrame
    
    if not users.empty:
        # Check if email and password match any record
        valid_user = users[(users['email'] == email) & (users['password'] == password)]
        if not valid_user.empty:
            return "success"
        else:
            return "Invalid email or password!"
    else:
        return "No users found!"

def register_user(user_type, email, password):
    sheet = connect_to_sheet().worksheet(user_type)  # Access the sheet for 'students' or 'faculty'
    users = pd.DataFrame(sheet.get_all_records())    # Get all records (user data) as a DataFrame
    
    if email in users['email'].values:
        return "Email already exists!"
    
    # Append new user data to the sheet
    new_user = {"email": email, "password": password}
    sheet.append_row([email, password])
    
    return "Account created successfully!"
