import sys
import random
import string
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QCheckBox, QPushButton, QVBoxLayout, QWidget, QMessageBox, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

# Password generator function
def generate_password(length, include_uppercase, include_numbers, include_symbols):
    characters = string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    if length < 1 or not characters:
        return None
    return ''.join(random.choice(characters) for _ in range(length))

# Database setup function
def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="***",
        database="internship_project"
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(45) NOT NULL,
            password_for VARCHAR(45) NOT NULL, 
            password VARCHAR(45) NOT NULL
        )
    ''')
    conn.commit()
    return conn


# Main Window Class
class PasswordGeneratorApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Random Password Generator")
        self.setGeometry(300, 300, 400, 400)

        # Create widgets
        self.purpose_label = QLabel("Password For:")
        self.purpose_input = QLineEdit()
        self.purpose_input.setPlaceholderText("Enter purpose (e.g., Github)")
        self.length_label = QLabel("Password Length:")
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("Enter length (e.g., 12)")
        self.uppercase_checkbox = QCheckBox("Include Uppercase Letters")
        self.numbers_checkbox = QCheckBox("Include Numbers")
        self.symbols_checkbox = QCheckBox("Include Symbols")
        self.generate_button = QPushButton("Generate Password")
        self.copy_button = QPushButton("Copy to Clipboard")
        self.save_button = QPushButton("Save to Database")
        self.display_button = QPushButton("Display all Passwords")
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px; color: green;")

        # Connect buttons to actions
        self.generate_button.clicked.connect(self.on_generate)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.save_button.clicked.connect(self.save_to_database)
        self.display_button.clicked.connect(self.open_display_passwords)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.purpose_label)
        layout.addWidget(self.purpose_input)
        layout.addWidget(self.length_label)
        layout.addWidget(self.length_input)
        layout.addWidget(self.uppercase_checkbox)
        layout.addWidget(self.numbers_checkbox)
        layout.addWidget(self.symbols_checkbox)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.save_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Setup database
        self.conn = setup_database()
        
        self.view_passwords_button = QPushButton("View Stored Passwords")
        self.view_passwords_button.clicked.connect(self.open_display_passwords)
        layout.addWidget(self.view_passwords_button)

    def on_generate(self):
        # Get user inputs
        try:
            length = int(self.length_input.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Password length must be a number.")
            return

        include_uppercase = self.uppercase_checkbox.isChecked()
        include_numbers = self.numbers_checkbox.isChecked()
        include_symbols = self.symbols_checkbox.isChecked()
        
        # Generate password
        password = generate_password(length, include_uppercase, include_numbers, include_symbols)
        if password:
            self.result_label.setText(f"Generated Password:\n{password}")
            self.generated_password = password
        else:
            QMessageBox.warning(self, "Error", "Invalid inputs. Check your options.")
            self.generated_password = ""

    def copy_to_clipboard(self):
        if hasattr(self, 'generated_password') and self.generated_password:
            QGuiApplication.clipboard().setText(self.generated_password)
            QMessageBox.information(self, "Copied", "Password copied to clipboard!")
        else:
            QMessageBox.warning(self, "Error", "No password to copy. Please generate one first.")

    def save_to_database(self):
        if hasattr(self, 'generated_password') and self.generated_password:
            try:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO password (username, password_for, password) VALUES (%s, %s, %s)", (self.username, self.purpose_input.text(), self.generated_password))
                self.conn.commit()
                QMessageBox.information(self, "Saved", "Password saved to database!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save to database: {e}")
        else:
            QMessageBox.warning(self, "Error", "No password to save. Please generate one first.")
            
    # To open the DisplayPasswordsApp from the PasswordGeneratorApp
    def open_display_passwords(self):
        self.display_passwords_app = DisplayPasswordsApp(self.username)
        self.display_passwords_app.show()


class DisplayPasswordsApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Stored Passwords")
        self.setGeometry(300, 300, 400, 400)

        # Create a list widget to display passwords
        self.password_list = QListWidget()

        # Load passwords from the database
        self.load_passwords()

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.password_list)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_passwords(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='internship_project', 
                user='root',
                password='***'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM password WHERE username=%s",(self.username,))
                records = cursor.fetchall()

                # Populate the list widget with passwords
                for row in records:
                    display_text = f"Password For:  {row[2]}, \nPassword:  {row[3]}\n"
                    self.password_list.addItem(display_text)
        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error while connecting to MySQL: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 300, 200)

        # Create widgets
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")

        # Connect button to action
        self.login_button.clicked.connect(self.on_login)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Validate credentials against the database
        if self.validate_credentials(username, password):
            QMessageBox.information(self, "Login Successful", "Welcome!")
            self.open_password_generator()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def validate_credentials(self, username, password):
        try:
            connection = mysql.connector.connect(
                host='localhost',              
                database='internship_project', 
                user='root',          
                password='***'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
                result = cursor.fetchone()
                return result is not None

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error while connecting to MySQL: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return False
    
    def open_password_generator(self):
        self.password_generator_app = PasswordGeneratorApp(self.username_input.text())
        self.password_generator_app.show()
        self.close()

# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())