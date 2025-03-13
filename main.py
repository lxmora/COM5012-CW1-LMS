import sqlite3

class LibraryManagementSystem:
    def __init__(self):
        self.db = sqlite3.connect("lms.db")
        self.cur = self.db.cursor()
        
        try:
            self.cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, name, hash);")
        except sqlite3.OperationalError as e:
            print(e)
        try:
            self.cur.execute("CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, ris);")
        except sqlite3.OperationalError as e:
            print(e)    
        try:
            self.cur.execute("CREATE TABLE loans(id INTEGER PRIMARY KEY AUTOINCREMENT, user, item, type, expires, FOREIGN KEY(item) REFERENCES items(id), FOREIGN KEY(user) REFERENCES users(id));")
        except sqlite3.OperationalError as e:
            print(e)

        self.ls = LoanSystem(self.db)
        self.ums = UserManagementSystem(self.db)
        self.ss = StockSystem(self.db)

class GenericSystem:
    def __init__(self, db):
        self.db = db
        self.cur = self.db.cursor()
    
    def commit(self):
        self.db.commit()

class LoanSystem(GenericSystem):
    def __init__(self, db):
        super().__init__(db)

       
class UserManagementSystem(GenericSystem):
    def __init__(self, db):
        super().__init__(db)

class StockSystem(GenericSystem):
    def __init__(self, db):
        super().__init__(db)


lms = LibraryManagementSystem()