import sqlite3

class LibraryManagementSystem:
    def __init__(self):
        self.db = sqlite3.connect("lms.db")
        self.ls = LoanSystem(self.db)
        self.ums = UserManagementSystem(self.db)
        self.ss = StockSystem(self.db)

class LoanSystem:
    def __init__(self, db):
        self.db = db
        self.cur = self.db.cursor()

class UserManagementSystem:
    def __init__(self, db):
        self.db = db
        self.cur = self.db.cursor()

class StockSystem:
    def __init__(self, db):
        self.db = db
        self.cur = self.db.cursor()