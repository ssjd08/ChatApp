import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QWidget, QLabel, QCheckBox, QTableWidgetItem
from PyQt5.uic import loadUi
import requests
from requests.auth import HTTPBasicAuth
from models import *
import time

class Login(QDialog):
    def __init__(self, widget, user):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.widget = widget
        self.user = user
        
        self.login_button.clicked.connect(self.enter)
        self.register_button.clicked.connect(self.go_to_register_page)
        
    def enter(self):
        if self.username_text.text() != "" or self.password_text.text() != "":
            login_data = {
                "username": self.username_text.text(),
                "password": self.password_text.text()
                }
            login_res = requests.post("http://127.0.0.1:8000/api-token-auth/", json = login_data)
            if login_res.status_code == 200:
                token = login_res.json()["token"]
                self.user.change_info(username = self.username_text.text(), password = self.password_text.text(), token=token)
                # print(self.user)
                self.widget.setCurrentIndex(1)
            else :
                self.alert_lable.setText(login_res.content.decode("utf-8"))

    def go_to_register_page(self):
        self.widget.setCurrentIndex(4)

class Register(QDialog):
    def __init__(self, widget, user):
        super(Register, self).__init__()
        loadUi("register.ui", self)
        self.widget = widget
        self.user = user
        
        self.register_button.clicked.connect(self.register)
        
    def register(self):
        try:
            register_data = {
                "username": self.username_text.text(),
                "email": self.email_text.text(),
                "password": self.password_text.text()
            }
            self.user.username = self.username_text.text()
            self.user.email = self.email_text.text()
            self.user.password = self.password_text.text()
            
            register_res = requests.post("http://127.0.0.1:8000/user/", json=register_data)
            if register_res.status_code == 201:
                self.alert_lable.setText("register was successful.")
                time.sleep(3)
                self.widget.setCurrentIndex(1)
                login_data = {
                "username": self.username_text.text(),
                "password": self.password_text.text()
                }
                login_res = requests.post("http://127.0.0.1:8000/api-token-auth/", json = login_data)
                if login_res.status_code == 200:
                    token = login_res.json()["token"]
                    self.user.token = token
                    self.widget.setCurrentIndex(1)
            else:
                self.alert_lable.setText(register_res.content.decode("utf-8"))
                
        except Exception as e:
            print("error: " , str(e))
              
class Main(QDialog):
    def __init__(self, widget, user, chat_page, create_group_page):
        super(Main, self).__init__()
        loadUi("main.ui", self)
        self.widget = widget
        self.user = user
        self.username_lable.setText(f"Welcome")
        self.chat_page = chat_page
        self.create_group = create_group_page
        
        self.scroll_layout = QVBoxLayout()
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.scroll_layout)
        self.groups_scroll_area.setWidget(self.scroll_content)
        self.groups_scroll_area.setWidgetResizable(True)
        
        self.reset_button.clicked.connect(self.load_user_groups)
        self.create_chat_button_2.clicked.connect(self.go_to_create_group_page)
        
    def go_to_create_group_page(self):
        self.create_group.load_online_users()
        self.widget.setCurrentIndex(self.widget.currentIndex() + 2)
        
    def load_user_groups(self):
        if self.user.token:
            auth = HTTPBasicAuth(self.user.username, self.user.password)
            
            response = requests.get("http://127.0.0.1:8000/user/groups/", auth=auth)
            if response.status_code == 200:
                groups = response.json()['groups']
                self.update_groups_ui(groups)
            else:
                self.alert_lable.setText(f"Error: {response.content.decode('utf-8')}")
                
        else:
            self.alert_lable.setText(f"Error: authentication failed!")
            
    def update_groups_ui(self, groups):
        # Clear the layout
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            self.scroll_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        # Create a button for each group and add it to the layout
        for group in groups:
            group_name = group['name']  # Display group name
            group_id = group['id']  # Get group ID
            group_button = QPushButton(group_name)

            # Connect the button click to a method that opens the chat
            group_button.clicked.connect(lambda checked, gid=group_id: self.open_group_chat(gid))
            
            self.scroll_layout.addWidget(group_button)
            
    
    def open_group_chat(self, group_id):
        print(f"Opening chat for group ID: {group_id}")
        self.chat_page.load_group(group_id)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
    
class ChatPage(QDialog):
    def __init__(self, widget, user):
        super(ChatPage, self).__init__()
        loadUi("chat_page.ui", self)
        self.widget = widget
        self.user = user
        self.group_id = None
        
        # Initialize layout for messages
        self.messages_layout = QVBoxLayout()
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.messages_layout)
        self.messages_scroll_area.setWidget(self.scroll_content)
        self.messages_scroll_area.setWidgetResizable(True)
        
        self.back_to_chats_button_2.clicked.connect(self.back)
        self.send_button.clicked.connect(self.send_message)
        self.reset_button.clicked.connect(self.load_messages)
        self.clear_page()
        
    def clear_page(self):
        for i in reversed(range(self.messages_layout.count())):
            widget_to_remove = self.messages_layout.itemAt(i).widget()
            self.messages_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def back(self):
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)
        
    def load_group(self, group_id):
        """Load the chat for the given group ID."""
        self.group_id = group_id
        self.load_messages()
        
    def load_messages(self):
        if self.group_id:
            auth = HTTPBasicAuth(self.user.username, self.user.password)
            response = requests.get(f"http://127.0.0.1:8000/group/{self.group_id}/messages/", auth=auth)
            
            if response.status_code == 200:
                messages = response.json()
                self.update_ui(messages)
            else:
                print(f"Error loading messages: {response.content.decode('utf-8')}")

    def update_ui(self, messages):
        for i in reversed(range(self.messages_layout.count())):
            widget_to_remove = self.messages_layout.itemAt(i).widget()
            self.messages_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
        
        # Add new messages
        for message in messages:
            message_widget = QLabel(f"{message['author']['username']}: {message['content']}")
            self.messages_layout.addWidget(message_widget)
        
    def send_message(self):
        message = self.message_text.text()
        if message and self.group_id:
            auth = HTTPBasicAuth(self.user.username, self.user.password)
            data = {
                "content": message
                }
            response = requests.post(f"http://127.0.0.1:8000/group/{self.group_id}/messages/", json=data, auth=auth)
            if response.status_code == 201:
                self.load_messages()  # Reload messages after sending
                self.message_text.clear()  # Clear the input box
            else:
                print(f"Error sending message: {response.content.decode('utf-8')}")

class CreateGroup(QDialog):
    def __init__(self, widget, user):
        super(CreateGroup, self).__init__()
        loadUi("create_group.ui", self)
        self.tableWidget.setColumnWidth(0,170)
        self.tableWidget.setColumnWidth(1,100)
        self.tableWidget.setColumnWidth(2,60)
        self.widget = widget
        self.user = user
        self.new_group_users = []
        
        self.reload_button.clicked.connect(self.load_online_users)
        self.create_button.clicked.connect(self.crete_group)
        self.back_to_chats_button.clicked.connect(self.return_to_last_page)
        
    def return_to_last_page(self):
        self.widget.setCurrentIndex(self.widget.currentIndex() - 2)
        
    def load_online_users(self):
        try:
            response = requests.get("http://127.0.0.1:8000/user/")
            print(f"Status code: {response.status_code}")
            print(f"response: {response.json()}")
            if response.status_code == 200:
                users = response.json()
                self.update_ui(users)
            else:
                print(f"Error: {response.content.decode('utf-8')}")
        except Exception as e:
            print(f"Exception during API call: {e}")
    
    def update_ui(self, users):
        self.tableWidget.setRowCount(0)  
    
        for user in users:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            
            username_item = QTableWidgetItem(str(user['id']))
            email_item = QTableWidgetItem(user['username'])
            select_checkbox = QCheckBox()  
            
            self.tableWidget.setItem(row_position, 0, username_item)
            self.tableWidget.setItem(row_position, 1, email_item)
            self.tableWidget.setCellWidget(row_position, 2, select_checkbox)  # Use a checkbox for selection

        self.tableWidget.resizeColumnsToContents()
        
    def get_selected_users(self):
        for row in range(self.tableWidget.rowCount()):
            checkbox = self.tableWidget.cellWidget(row, 2)  # Assuming the checkbox is in the third column
            if checkbox.isChecked():
                user_id = self.tableWidget.item(row, 0).text() 
                self.new_group_users.append(user_id)


    def crete_group(self):
        group_name = self.group_name.text()
        selected_users = self.get_selected_users()
        print(self.get_selected_users)
        
        auth = HTTPBasicAuth(self.user.username, self.user.password)
        if group_name != "" and selected_users != []:
            group_data = {
                'name': group_name,
                'users': self.new_group_users
            }
            
            response = requests.post("http://127.0.0.1:8000/group/", json=group_data, auth=auth)
            
            if response.status_code == 201:
                print("Group created successfully!")
                self.return_to_last_page()  
            else:
                print(f"Error creating group: {response.content.decode('utf-8')}")
                
                
class App(QDialog):
    def __init__(self, user):
        self.user = user
        self.app = QApplication(sys.argv)
        super(App, self).__init__()
        self.initail_widget()  
        
        # Initialize the pages after the widget is created
        self.chat_page = ChatPage(self.widget, self.user)
        self.create_group = CreateGroup(self.widget, self.user)
        self.main_page = Main(self.widget, self.user, self.chat_page, self.create_group) 
        self.login_page = Login(self.widget, self.user)
        self.create_group = CreateGroup(self.widget, self.user)
        self.register_page = Register(self.widget, self.user)
        
        # Add pages to the widget
        self.widget.addWidget(self.login_page)
        self.widget.addWidget(self.main_page)
        self.widget.addWidget(self.chat_page)
        self.widget.addWidget(self.create_group)
        self.widget.addWidget(self.register_page)
        
    def initail_widget(self):
        self.widget = QtWidgets.QStackedWidget()  
        self.widget.setFixedWidth(400)
        self.widget.setFixedHeight(650)

    def run(self):
        self.widget.show()
        self.app.exec_()
        
        