import sqlite3
import os

class LibraryManagementSystem:
    def __init__(self):
        self.db = sqlite3.connect("lms.db")
        self.cur = self.db.cursor()

        try:
            self.cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, name, password, permissions);")
        except sqlite3.OperationalError as e:
            print(e)
        try:
            self.cur.execute("CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, status, title, author);")
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

    def execute(self, string, args):
        try:
            self.cur.execute(string, args)
        except sqlite3.OperationalError as e:
            print(e)


class LoanSystem(GenericSystem):
    def request_loan(self, name, item):
        self.execute("INSERT INTO loans (user, item, type) VALUES (?,?,'loan')", [name, item])
        self.commit()

    def request_hold(self, name, item):
        self.execute("INSERT INTO loans (user, item, type) VALUES (?,?,'hold')", [name, item])
        self.commit()

    def return_loan(self, name, item):
        self.execute("DELETE FROM loans WHERE name=? AND item=?",[name, item])
        self.commit()

class UserManagementSystem(GenericSystem):
    def login_user(self, name, password):
        self.execute("SELECT permissions FROM users WHERE name=? AND password=?",[name, password])
        return self.cur.fetchone()

    def search(self, name):
        self.execute("SELECT id FROM users WHERE name=?",[name])
        return self.cur.fetchone()

    def add_user(self, name, password, permission_level):
        self.execute("INSERT INTO users (name, password, permissions) VALUES (?,?,?);",[name, password, permission_level])
        self.commit()

    def suspend_user(self, name):
        self.execute("UPDATE users SET permissions='suspended' WHERE name=?;",[name])
        self.commit()

    def make_librarian(self, name):
        self.execute("UPDATE users SET permissions='librarian' WHERE name=?", [name])
        self.commit()

    def make_admin(self, name):
        self.execute("UPDATE users SET permissions='admin' WHERE name=?", [name])
        self.commit()

    def make_member(self, name):
        self.execute("UPDATE users SET permissions='member' WHERE name=?", [name])
        self.commit()

class StockSystem(GenericSystem):
    def add_item(self, title, author):
        self.execute("INSERT INTO items (status, author, title) VALUES ('unavailable',?,?)", [title,author])
        self.commit()

    def remove_item(self, item):
        self.execute("DELETE FROM items WHERE id=?",[item])
        self.commit()

    def mark_loaned(self, item):
        self.execute("UPDATE items SET status='loaned' WHERE id=?", [item])
        self.commit()

    def mark_overdue(self, item):
        self.execute("UPDATE items SET status='overdue' WHERE id=?", [item])
        self.commit()

    def mark_available(self, item):
        self.execute("UPDATE items SET status='available' WHERE id=?", [item])

    def search(self, title, author):
        self.execute("SELECT id FROM items WHERE title='title' AND author='author'",[title, author])
        self.commit()

    def search_title(self, title):
        self.execute("SELECT * FROM items WHERE title like ?",['%'+title+'%'])
        return self.cur.fetchall()

    def search_author(self, author):
        self.execute("SELECT * FROM items WHERE author=?", [author])
        return self.cur.fetchall()

class BaseMenu():
    def __init__(self):
        self.options={}
        self.lms = LibraryManagementSystem()
        self.__user_permissions = "guest"
        self.options_list=[]

    def update_options(self):
        if self.__user_permissions == "member":
            self.options=MemberOptions(self).options()
        if self.__user_permissions == "librarian":
            self.options=LibrarianOptions(self).options()
        if self.__user_permissions == "admin":
            self.options=AdminOptions(self).options()
        else:
            self.options=BaseOptions(self).options()
        self.options_list=list(self.options.keys())

    def update_login(self, perms):
        self.__user_permissions = perms
        self.update_options()

    def print_options(self):
        counter=0
        for option in self.options_list:
            print(str(counter)+"> "+str(option))
            counter+=1

    def get_option(self):
        print("Enter an Option:")
        option=int(input())
        self.options[self.options_list[option]]()


class BaseOptions():
    def __init__(self,menu):
        self.menu=menu
        self.lms=menu.lms
    def options(self):
        return {"login":self.login, "logout":self.logout, "search":self.search}
    def login(self):
        self.menu.update_login("admin")
    def logout(self):
        self.menu.update_login("guest")
    def search(self):
        pass

class MemberOptions(BaseOptions):
    def options(self):
        return super().options() | {"borrow item":self.borrow_item,"reserve item":self.reserve_item,"return item":self.return_item}
    def borrow_item(self):
        pass
    def reserve_item(self):
        pass
    def return_item(self):
        pass

class LibrarianOptions(MemberOptions):
    def options(self):
        return super().options() | {"add item":self.add_item,"update item":self.update_item}
    def add_item(self):
        pass
    def update_item(self):
        pass

class AdminOptions(LibrarianOptions):
    def options(self):
        return super().options() | {"suspend user":self.suspend_user,"add user":self.add_user}
    def suspend_user(self):
        print("suspended user")
        return self
    def add_user(self):
        pass

menu = BaseMenu()
menu.update_options()
if os.name == "nt":
    CLEAR="cls"
else:
    CLEAR="clear"
while True:
    os.system(CLEAR)
    menu.print_options()
    menu.get_option()
