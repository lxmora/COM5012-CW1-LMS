import sqlite3
import os
import sys

class LibraryManagementSystem:
    def __init__(self):
        self.db = sqlite3.connect("lms.db")
        self.cur = self.db.cursor()

        try:
            self.cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, name, password, permissions);")
        except sqlite3.OperationalError:
            pass
        try:
            self.cur.execute("CREATE TABLE items(id INTEGER PRIMARY KEY AUTOINCREMENT, status, title, author);")
        except sqlite3.OperationalError:
            pass
        try:
            self.cur.execute("CREATE TABLE loans(id INTEGER PRIMARY KEY AUTOINCREMENT, user, item, type, expires, FOREIGN KEY(item) REFERENCES items(id), FOREIGN KEY(user) REFERENCES users(id));")
        except sqlite3.OperationalError:
            pass

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

    def add_user(self, name, password, permission_level="guest"):
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
        self.execute("UPDATE items SET status='removed' WHERE id=?",[item])
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
        self.__user_name = ""
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

    def update_login(self, name, perms):
        self.__user_permissions = perms
        self.update_name(name)
        self.update_options()

    def update_name(self, name):
        self.__user_name = name

    def get_name(self):
        return self.__user_name

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
        return {"exit":self.exit,"login":self.login, "logout":self.logout, "search":self.search}
    def exit(self):
        sys.exit()
    def login(self):
        name=input("Enter user name: ")
        password=input("Enter password: ")
        perms=self.lms.ums.login_user(name, password)[0]
        self.menu.update_login(name,perms)
    def logout(self):
        self.menu.update_login("","guest")
    def search(self):
        print("0> Search by Title\n1> Search by Author")
        if input() == "0":
            out=self.lms.ss.search_title(input("Enter Title:"))
        elif input() == "1":
            out=self.lms.ss.search_author(input("Author"))
        else:
            print("Invalid Input")
            out = ""
        if str(out) == "[]":
            print("No Results Found")
        else:
            print(out)
        input("'Enter' to Continue")

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
        title=input("Enter Title: ")
        author=input("Enter Author: ")
        self.lms.ss.add_item(title, author)

    def update_item(self):
        option=input("0> Back\n1> Mark Overdue\n2> Mark Loaned\n3> Mark Available\n4> Mark Removed")
        prompt="Enter Item ID: "
        if option == "0":
            prompt="'Enter' to Continue"
        item_id=input(prompt)
        if option == "1":
            self.lms.ss.mark_overdue(item_id)
        if option == "2":
            self.lms.ss.mark_loaned(item_id)
        if option == "3":
            self.lms.ss.mark_available(item_id)
        if option == "4":
            self.lms.ss.remove_item(item_id)
        else:
            input("Invalid Option: 'Enter to Continue'")

    def item_report(self):
        pass

class AdminOptions(LibrarianOptions):
    def options(self):
        return super().options() | {"suspend user":self.suspend_user,"add user":self.add_user}
    def suspend_user(self):
        name=input("Enter user name: ")
        self.lms.ums.suspend_user(name)

    def add_user(self):
        name=input("Enter user name:")
        password=input("Enter password:")
        perms=input("Enter Permission Level:")
        self.lms.ums.add_user(name,password,perms)

app = BaseMenu()
app.update_options()
if os.name == "nt":
    CLEAR="cls"
else:
    CLEAR="clear"
while True:
    os.system(CLEAR)
    app.print_options()
    app.get_option()
