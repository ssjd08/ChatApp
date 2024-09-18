from models import *
from Qt_application import App

class ChatApp:
    def __init__(self):
        self.user = User()

        #app interface initialization
        self.user_interface = App(self.user)

    def run(self):
            self.user_interface.run()
            

