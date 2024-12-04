import tkinter as tk
import customtkinter as ck
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from finalsproj import run
# Define the scope for Google Sheets and Google Drive API
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from your JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name('ATTENDANCECHECKER/attendancesystem-443309-b7a6d64cef33.json', scope)
client = gspread.authorize(creds)

def update_clock(label):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS
    label.configure(text=current_time)
    label.after(1000, update_clock, label)

# Function to validate login credentials from Google Sheets
def validate_login(user_type, email, password):
    try:
        spreadsheet = client.open("Attendance System")  # Replace with the actual name of your sheet
        worksheet = spreadsheet.worksheet(user_type)  # Use either 'faculty' or 'students'
        data = worksheet.get_all_values()
        users = pd.DataFrame(data[1:], columns=data[0])  # Assumes first row is the header
        
        if ((users['email'] == email) & (users['password'] == password)).any():
            return "success"
        else:
            return "Invalid email or password!"
    except Exception as e:
        return f"Error: {e}"

# Function to register a student from the faculty home page
def register_student(email, password):
    try:
        spreadsheet = client.open("Attendance System")  # Replace with the actual name of your sheet
        worksheet = spreadsheet.worksheet("students")
        data = worksheet.get_all_values()
        existing_emails = [row[0] for row in data[1:]]
        
        if email in existing_emails:
            return "Email already exists!"
        
        worksheet.append_row([email, password])
        return "Student registered successfully!"
    except Exception as e:
        return f"Error: {e}"

# Faculty Home Page
def open_faculty_home():
    faculty_window.withdraw()
    ck.set_appearance_mode("dark")
    ck.set_default_color_theme("blue")
    home = ck.CTk()
    home.geometry('1280x720')
    home.title("Faculty Home Page")

    clock_label = ck.CTkLabel(master=home, font=('Century Gothic', 20))
    clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    update_clock(clock_label)
    
    l1 = ck.CTkLabel(master=home, text="Faculty Home Page", font=('Century Gothic', 20))
    l1.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    
    # Registration Section
    frame = ck.CTkFrame(master=home, width=400, height=200, corner_radius=15)
    frame.place(relx=0.3, rely=0.4, anchor=tk.E)
    
    reg_label = ck.CTkLabel(master=frame, text="Register a Student", font=('Century Gothic', 15))
    reg_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    
    student_email_entry = ck.CTkEntry(master=frame, placeholder_text="Student ID")
    student_email_entry.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    
    student_pass_entry = ck.CTkEntry(master=frame, placeholder_text="Password", show="*")
    student_pass_entry.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
    
    def register_action():
        email = student_email_entry.get()
        password = student_pass_entry.get()
        result = register_student(email, password)
        reg_label.configure(text=result)
        update_student_list()  # Update the student list after registering a new student
    
    register_button = ck.CTkButton(master=frame, text="Register", command=register_action)
    register_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
    
    # Student Email Display
    email_frame = ck.CTkFrame(master=home, width=400, height=400, corner_radius=15, fg_color="orange")
    email_frame.place(relx=0.7, rely=0.5, anchor=tk.W)
    
    email_label = ck.CTkLabel(master=email_frame, text="Student Emails", font=('Century Gothic', 20))
    email_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    
    email_textbox = ck.CTkTextbox(master=email_frame, width=350, height=300, wrap="none")
    email_textbox.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def update_student_list():
        try:
            spreadsheet = client.open("Attendance System")  # Replace with the actual name of your sheet
            worksheet = spreadsheet.worksheet("students")
            data = worksheet.get_all_values()
            student_emails = [row[0] for row in data[1:]]  # Extract the email column, skip header
            
            email_textbox.delete("1.0", tk.END)  # Clear the textbox
            for email in student_emails:
                email_textbox.insert(tk.END, f"{email}\n")  # Add each email to the textbox
        except Exception as e:
            email_textbox.insert(tk.END, f"Error: {e}")
    
    update_student_list()  # Initial population of student email list
    
    home.mainloop()


# Student Home Page
def open_student_home():
    student_window.withdraw()
    ck.set_appearance_mode("dark")
    ck.set_default_color_theme("blue")
    home = ck.CTk()
    home.geometry('1280x720')
    home.title("Student Home Page")

    clock_label = ck.CTkLabel(master=home, font=('Century Gothic', 20))
    clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    update_clock(clock_label)
    
    l1 = ck.CTkLabel(master=home, text="Student Home Page", font=('Century Gothic', 20))
    l1.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

    frame2 = ck.CTkFrame(master=home, width=400, height=560, corner_radius=15, fg_color='orange')
    frame2.place(relx=0.7, rely=0.5, anchor=tk.W)

    recordB = ck.CTkButton(master=frame2, width=100, height=50, text="Record", command=run)
    recordB.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    home.mainloop()


# Faculty Login
def faculty_login():
    email = faculty_entry1.get()
    password = faculty_entry2.get()
    result = validate_login("faculty", email, password)
    if result == "success":
        open_faculty_home()
    else:
        faculty_error_label.configure(text=result)

# Student Login
def student_login():
    email = student_entry1.get()
    password = student_entry2.get()
    result = validate_login("students", email, password)
    if result == "success":
        open_student_home()
    else:
        student_error_label.configure(text=result)

# Open Student Login Window
def open_student_window():
    global student_window, student_entry1, student_entry2, student_error_label
    app.withdraw()
    student_window = ck.CTk()
    student_window.geometry("720x480")
    student_window.title("Student Login")
    
    frame = ck.CTkFrame(student_window, width=320, height=360, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    l1 = ck.CTkLabel(master=frame, text="Student Login", font=('Century Gothic', 20))
    l1.place(x=50, y=25)
    
    student_entry1 = ck.CTkEntry(master=frame, width=220, placeholder_text="Student ID")
    student_entry1.place(x=50, y=80)
    student_entry2 = ck.CTkEntry(master=frame, width=220, placeholder_text="Password", show="*")
    student_entry2.place(x=50, y=135)
    
    student_error_label = ck.CTkLabel(master=frame, text="", font=('Century Gothic', 12), text_color="red")
    student_error_label.place(x=50, y=180)
    
    login_button = ck.CTkButton(master=frame, width=100, text='Login', corner_radius=6, command=student_login)
    login_button.place(x=50, y=220)
    
    back_button = ck.CTkButton(master=frame, width=100, text="Back", corner_radius=6, command=lambda: (student_window.withdraw(), app.deiconify()))
    back_button.place(x=170, y=220)
    
    student_window.mainloop()

# Open Faculty Login Window
def open_faculty_window():
    global faculty_window, faculty_entry1, faculty_entry2, faculty_error_label
    app.withdraw()
    faculty_window = ck.CTk()
    faculty_window.geometry("720x480")
    faculty_window.title("Faculty Login")
    
    frame = ck.CTkFrame(faculty_window, width=320, height=360, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    l1 = ck.CTkLabel(master=frame, text="Faculty Login", font=('Century Gothic', 20))
    l1.place(x=50, y=25)
    
    faculty_entry1 = ck.CTkEntry(master=frame, width=220, placeholder_text="Faculty ID")
    faculty_entry1.place(x=50, y=80)
    faculty_entry2 = ck.CTkEntry(master=frame, width=220, placeholder_text="Password", show="*")
    faculty_entry2.place(x=50, y=135)
    
    faculty_error_label = ck.CTkLabel(master=frame, text="", font=('Century Gothic', 12), text_color="red")
    faculty_error_label.place(x=50, y=180)
    
    login_button = ck.CTkButton(master=frame, width=100, text='Login', corner_radius=6, command=faculty_login)
    login_button.place(x=50, y=220)
    
    back_button = ck.CTkButton(master=frame, width=100, text="Back", corner_radius=6, command=lambda: (faculty_window.withdraw(), app.deiconify()))
    back_button.place(x=170, y=220)
    
    faculty_window.mainloop()

# Main Application
def open_main_window():
    global app
    ck.set_appearance_mode("dark")
    ck.set_default_color_theme("blue")
    app = ck.CTk()
    app.geometry("720x480")
    app.title("Attendance Checker")

    clock_label = ck.CTkLabel(master=app, font=('Century Gothic', 20))
    clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    update_clock(clock_label)

    frame = ck.CTkFrame(app, width=320, height=360, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    l1 = ck.CTkLabel(master=frame, text="Choose Login Type", font=('Century Gothic', 20))
    l1.place(x=50, y=45)

    student_button = ck.CTkButton(master=frame, width=220, text="Student", corner_radius=6, command=open_student_window)
    student_button.place(x=50, y=110)

    faculty_button = ck.CTkButton(master=frame, width=220, text="Faculty", corner_radius=6, command=open_faculty_window)
    faculty_button.place(x=50, y=165)

    app.mainloop()

# Initialize app window and start the application
app = None
student_window = None
faculty_window = None
open_main_window()
