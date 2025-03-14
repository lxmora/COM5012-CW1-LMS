class LibraryManagementSystem:
    function __init__():
        connect to database
        ensure database tables (items, users, loans) exist

class GenericSystem:
    attribute db = database connection
    attribute cur = database connection

    function commit():
        commits changes to database

    function execute(string, args):
        executes sql query on database


class LoanSystem inherits from GenericSystem:
    function request_loan(name, item):
        inserts new loan to loans table

    function request_hold(name, item):
        inserts new hold to loans table

    function return_loan(name, item):
        deletes associate loan from loans table

class UserManagementSystem inherits from GenericSystem:
    function login_user(name, password):
        returns permission level of specifed user from users table

    function search(name):
        returns user entry with name from users table

    function add_user(name, password, permission_level):
        inserts new user entry to users table

    function suspend_user(name):
        updates permission_level for user entry with name to suspended

    function make_librarian(name):
        updates permission_level for user entry with name to librarian

    function make_admin(name):
        updates permission_level for user entry with name to librarian

    function make_member(name):
        updates permission_level for user entry with name to member

class StockSystem inherits from GenericSystem:
    function add_item(title, author):
        inserts new entry into items table

    function remove_item(item):
        updates entry with item to status removed

    function mark_loaned(item):
        updates entry with item to status loaned

    function mark_overdue(item):
        updates entry with item to status overdue

    function mark_available(item):
        updates entry with item to status available

    function search(title, author):
        returns entries with title and author from items table

    function search_title(title):
        returns entries with title from items table

    function search_author(, author):
        returns entries with author from items table

class BaseMenu():
    function __init__():
        attribute protected options = dictionary
        attrubute private user_permissions
        attribute private user_name
        attrubute protected options_list = list

    function update_options():
        calls options() from appropriate BaseOptions subclass based on user_permissions

    function update_login(name, perms):
        user_permission = perms
        user_name = name
        call update_options()

    function update_name(name):
        user_name = name

    function get_name():
        return user_name

    function print_options():
        counter=0
        for option in options_list:
            print counter > option
            counter + 1

    function get_option():
        print("Enter an Option:")
        option=int(input())
        ._options[._options_list[option]]()


class BaseOptions():

    function options():
        returns dictionary of functions in the class

    function exit():
        exits program

    function login():
        name = input "Enter user name:"
        password = input "Enter password:"
        login user
    function logout():
        clears user login

    function search():
        prompts for UserManagementSystem search functions

class MemberOptions(BaseOptions):
    function options():
        retruns dictionary of class and superclass functions 
    function borrow_item():
        prompts for item
        requests loan from LoanSystem
        marks item as loaned from StockSystem
    function reserve_item():
        prompts for item
        reqests hold from LoanSystem
        marks item as reserved from StockSystem
    function return_item():
        prompts for item
        requests return from LoanSystem
        marks item as available from StockSystem

class LibrarianOptions(MemberOptions):
    function options():
        returns dictionary of class and superclass functions
    
    function add_item():
        prompts for title and author
        adds item to StockSystem

    function update_item():
        Prompts for item and status
        Marks status in Stock System

    function item_report():
        Prints all entries in loans and items tables

class AdminOptions(LibrarianOptions):
    function options():
        returns dictionary of class and superclass functions

    function suspend_user():
        prompts for user
        requests user suspension from UserManagementSystem

    function add_user():
        prompts for username, password and permissions
        reqeusts new user from UsermanagementSystem

app = BaseMenu()
while True:
    clear screen
    app.print_options()
    app.get_option()
