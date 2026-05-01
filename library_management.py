"""
Smart Library Management System
================================
OOP-based console application implementing:
- Abstraction (Abstract base classes)
- Encapsulation (Private attributes + getters/setters)
- Inheritance (Person -> Student / Librarian)

Advanced Features:
- Book borrow limit per student (3 books)
- Fine calculation for late returns
- Book search by name
- Multiple users handling
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
#  ABSTRACT BASE CLASS
# ─────────────────────────────────────────────

class Person(ABC):
    """Abstract base class for all users in the system."""

    def __init__(self, name: str, user_id: str):
        self._name = name
        self._user_id = user_id

    @property
    def name(self):
        return self._name

    @property
    def user_id(self):
        return self._user_id

    @abstractmethod
    def display_role(self):
        pass

    @abstractmethod
    def perform_action(self, library):
        pass

    def __str__(self):
        return f"{self._name} (ID: {self._user_id})"


# ─────────────────────────────────────────────
#  BOOK CLASS
# ─────────────────────────────────────────────

class Book:
    """Represents a book in the library with encapsulated availability."""

    FINE_PER_DAY = 5  # Rs. 5 per day after due date

    def __init__(self, book_id: str, title: str, author: str):
        self._book_id = book_id
        self._title = title
        self._author = author
        self.__availability = True  # Private attribute

    # ── Getters & Setters ──

    @property
    def book_id(self):
        return self._book_id

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    def get_availability(self):
        return self.__availability

    def set_availability(self, status: bool):
        if isinstance(status, bool):
            self.__availability = status
        else:
            raise ValueError("Availability must be True or False.")

    def __str__(self):
        status = "✅ Available" if self.__availability else "❌ Borrowed"
        return f"[{self._book_id}] '{self._title}' by {self._author} — {status}"


# ─────────────────────────────────────────────
#  LIBRARY CLASS
# ─────────────────────────────────────────────

class Library:
    """Manages the collection of books and borrow/return records."""

    BORROW_LIMIT = 3           # Max books a student can borrow
    BORROW_DAYS = 7            # Days before fine starts

    def __init__(self, name: str):
        self._name = name
        self._books: dict[str, Book] = {}          # book_id -> Book
        # issued_records: user_id -> [(book_id, borrow_date)]
        self._issued_records: dict[str, list] = {}

    # ── Book Management ──

    def add_book(self, book: Book):
        if book.book_id in self._books:
            print(f"  ⚠  Book ID '{book.book_id}' already exists.")
        else:
            self._books[book.book_id] = book
            print(f"  ✔  Book added: {book.title}")

    def remove_book(self, book_id: str):
        if book_id not in self._books:
            print(f"  ⚠  No book found with ID '{book_id}'.")
            return
        book = self._books[book_id]
        if not book.get_availability():
            print(f"  ⚠  Cannot remove '{book.title}' — it is currently borrowed.")
            return
        del self._books[book_id]
        print(f"  ✔  Book '{book.title}' removed from library.")

    def show_available_books(self):
        available = [b for b in self._books.values() if b.get_availability()]
        if not available:
            print("  No books are currently available.")
        else:
            print(f"\n  {'ID':<8} {'Title':<30} {'Author':<25}")
            print("  " + "─" * 65)
            for b in available:
                print(f"  {b.book_id:<8} {b.title:<30} {b.author:<25}")

    def show_all_books(self):
        if not self._books:
            print("  Library is empty.")
        else:
            print(f"\n  {'ID':<8} {'Title':<30} {'Author':<25} {'Status':<15}")
            print("  " + "─" * 80)
            for b in self._books.values():
                status = "Available" if b.get_availability() else "Borrowed"
                print(f"  {b.book_id:<8} {b.title:<30} {b.author:<25} {status:<15}")

    def search_book(self, keyword: str):
        keyword = keyword.lower()
        results = [b for b in self._books.values()
                   if keyword in b.title.lower() or keyword in b.author.lower()]
        if not results:
            print(f"  No books found matching '{keyword}'.")
        else:
            print(f"\n  Search results for '{keyword}':")
            for b in results:
                print(f"    {b}")

    # ── Borrow & Return ──

    def borrow_book(self, user_id: str, book_id: str) -> bool:
        # Check book exists
        if book_id not in self._books:
            print(f"  ⚠  Book ID '{book_id}' not found.")
            return False

        book = self._books[book_id]

        # Check availability
        if not book.get_availability():
            print(f"  ⚠  '{book.title}' is currently not available.")
            return False

        # Check borrow limit
        user_records = self._issued_records.get(user_id, [])
        if len(user_records) >= self.BORROW_LIMIT:
            print(f"  ⚠  Borrow limit reached ({self.BORROW_LIMIT} books max).")
            return False

        # Already borrowed same book?
        if any(r[0] == book_id for r in user_records):
            print(f"  ⚠  You already have '{book.title}' borrowed.")
            return False

        # Issue book
        book.set_availability(False)
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=self.BORROW_DAYS)

        if user_id not in self._issued_records:
            self._issued_records[user_id] = []
        self._issued_records[user_id].append((book_id, borrow_date))

        print(f"  ✔  '{book.title}' borrowed successfully!")
        print(f"     Due date: {due_date.strftime('%d %b %Y')} (within {self.BORROW_DAYS} days)")
        return True

    def return_book(self, user_id: str, book_id: str):
        user_records = self._issued_records.get(user_id, [])
        record = next((r for r in user_records if r[0] == book_id), None)

        if record is None:
            print(f"  ⚠  No borrow record found for book ID '{book_id}' under your account.")
            return

        book = self._books.get(book_id)
        if not book:
            print(f"  ⚠  Book ID '{book_id}' not found in system.")
            return

        borrow_date = record[1]
        return_date = datetime.now()
        days_held = (return_date - borrow_date).days
        fine = 0

        if days_held > self.BORROW_DAYS:
            overdue_days = days_held - self.BORROW_DAYS
            fine = overdue_days * Book.FINE_PER_DAY
            print(f"  ⚠  Book returned {overdue_days} day(s) late.")
            print(f"     Fine: Rs. {fine} ({overdue_days} days × Rs. {Book.FINE_PER_DAY}/day)")
        else:
            print(f"  ✔  Book returned on time. No fine.")

        book.set_availability(True)
        self._issued_records[user_id].remove(record)
        print(f"  ✔  '{book.title}' returned successfully!")

    def get_user_borrowed_books(self, user_id: str):
        records = self._issued_records.get(user_id, [])
        if not records:
            print("  You have no borrowed books.")
        else:
            print(f"\n  {'Book ID':<10} {'Title':<30} {'Borrowed On':<20} {'Due Date':<20}")
            print("  " + "─" * 80)
            for book_id, borrow_date in records:
                book = self._books.get(book_id)
                title = book.title if book else "Unknown"
                due = borrow_date + timedelta(days=self.BORROW_DAYS)
                print(f"  {book_id:<10} {title:<30} "
                      f"{borrow_date.strftime('%d %b %Y'):<20} "
                      f"{due.strftime('%d %b %Y'):<20}")

    def show_all_issued(self):
        if not self._issued_records:
            print("  No books are currently issued.")
            return
        print(f"\n  {'User ID':<12} {'Book ID':<10} {'Title':<30} {'Borrowed On':<20}")
        print("  " + "─" * 75)
        for uid, records in self._issued_records.items():
            for book_id, borrow_date in records:
                book = self._books.get(book_id)
                title = book.title if book else "Unknown"
                print(f"  {uid:<12} {book_id:<10} {title:<30} "
                      f"{borrow_date.strftime('%d %b %Y'):<20}")


# ─────────────────────────────────────────────
#  STUDENT CLASS
# ─────────────────────────────────────────────

class Student(Person):
    """A student who can borrow and return books."""

    def display_role(self):
        print(f"\n  Role: Student | Name: {self._name} | ID: {self._user_id}")

    def perform_action(self, library: Library):
        while True:
            print(f"""
  ╔══════════════════════════════╗
  ║    STUDENT MENU              ║
  ╠══════════════════════════════╣
  ║  1. View Available Books     ║
  ║  2. Borrow a Book            ║
  ║  3. Return a Book            ║
  ║  4. My Borrowed Books        ║
  ║  5. Search Book              ║
  ║  6. Logout                   ║
  ╚══════════════════════════════╝""")
            choice = input("  Enter choice: ").strip()

            if choice == "1":
                print("\n  ── Available Books ──")
                library.show_available_books()

            elif choice == "2":
                book_id = input("  Enter Book ID to borrow: ").strip()
                library.borrow_book(self._user_id, book_id)

            elif choice == "3":
                book_id = input("  Enter Book ID to return: ").strip()
                library.return_book(self._user_id, book_id)

            elif choice == "4":
                print("\n  ── Your Borrowed Books ──")
                library.get_user_borrowed_books(self._user_id)

            elif choice == "5":
                keyword = input("  Enter title or author to search: ").strip()
                library.search_book(keyword)

            elif choice == "6":
                print(f"  Goodbye, {self._name}!")
                break
            else:
                print("  ⚠  Invalid choice. Try again.")


# ─────────────────────────────────────────────
#  LIBRARIAN CLASS
# ─────────────────────────────────────────────

class Librarian(Person):
    """A librarian who manages the library system."""

    def display_role(self):
        print(f"\n  Role: Librarian | Name: {self._name} | ID: {self._user_id}")

    def perform_action(self, library: Library):
        while True:
            print(f"""
  ╔══════════════════════════════╗
  ║    ADMIN / LIBRARIAN MENU    ║
  ╠══════════════════════════════╣
  ║  1. View All Books           ║
  ║  2. Add a Book               ║
  ║  3. Remove a Book            ║
  ║  4. View All Issued Books    ║
  ║  5. Search Book              ║
  ║  6. Logout                   ║
  ╚══════════════════════════════╝""")
            choice = input("  Enter choice: ").strip()

            if choice == "1":
                print("\n  ── All Books ──")
                library.show_all_books()

            elif choice == "2":
                book_id = input("  Enter Book ID     : ").strip()
                title   = input("  Enter Book Title  : ").strip()
                author  = input("  Enter Author Name : ").strip()
                if book_id and title and author:
                    library.add_book(Book(book_id, title, author))
                else:
                    print("  ⚠  All fields are required.")

            elif choice == "3":
                book_id = input("  Enter Book ID to remove: ").strip()
                library.remove_book(book_id)

            elif choice == "4":
                print("\n  ── Currently Issued Books ──")
                library.show_all_issued()

            elif choice == "5":
                keyword = input("  Enter title or author to search: ").strip()
                library.search_book(keyword)

            elif choice == "6":
                print(f"  Goodbye, {self._name}!")
                break
            else:
                print("  ⚠  Invalid choice. Try again.")


# ─────────────────────────────────────────────
#  USER REGISTRY  (Multiple users handling)
# ─────────────────────────────────────────────

class UserRegistry:
    """Stores and authenticates registered users."""

    def __init__(self):
        self._users: dict[str, Person] = {}

    def register(self, user: Person):
        if user.user_id in self._users:
            print(f"  ⚠  User ID '{user.user_id}' is already registered.")
        else:
            self._users[user.user_id] = user
            print(f"  ✔  {user.name} registered successfully.")

    def login(self, user_id: str) -> Person | None:
        user = self._users.get(user_id)
        if user:
            print(f"  ✔  Welcome back, {user.name}!")
            user.display_role()
            return user
        else:
            print(f"  ⚠  No user found with ID '{user_id}'.")
            return None

    def list_users(self):
        if not self._users:
            print("  No users registered.")
        else:
            print(f"\n  {'ID':<12} {'Name':<25} {'Role':<12}")
            print("  " + "─" * 50)
            for u in self._users.values():
                role = "Librarian" if isinstance(u, Librarian) else "Student"
                print(f"  {u.user_id:<12} {u.name:<25} {role:<12}")


# ─────────────────────────────────────────────
#  SEED DATA  (pre-load for demonstration)
# ─────────────────────────────────────────────

def seed_data(library: Library, registry: UserRegistry):
    # Books
    books = [
        Book("B001", "Python Crash Course",       "Eric Matthes"),
        Book("B002", "Clean Code",                "Robert C. Martin"),
        Book("B003", "The Pragmatic Programmer",  "Andrew Hunt"),
        Book("B004", "Design Patterns",           "Gang of Four"),
        Book("B005", "Introduction to Algorithms","Thomas H. Cormen"),
        Book("B006", "You Don't Know JS",         "Kyle Simpson"),
        Book("B007", "Fluent Python",             "Luciano Ramalho"),
    ]
    for b in books:
        library.add_book(b)

    # Users
    registry.register(Librarian("Admin Ali",    "L001"))
    registry.register(Student("Sara Khan",      "S001"))
    registry.register(Student("Ahmed Raza",     "S002"))
    registry.register(Student("Fatima Noor",    "S003"))


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print("""
  ╔═══════════════════════════════════════════╗
  ║   SMART LIBRARY MANAGEMENT SYSTEM        ║
  ║   Powered by OOP  |  Console Edition     ║
  ╚═══════════════════════════════════════════╝
  Initializing library...
    """)

    library  = Library("City Public Library")
    registry = UserRegistry()
    seed_data(library, registry)

    print("\n  ── System ready! ──")

    while True:
        print("""
  ════════════════════════════════
       MAIN MENU
  ════════════════════════════════
   1. Login
   2. Register New Student
   3. Register New Librarian
   4. List All Users
   5. Exit
  ════════════════════════════════""")
        choice = input("  Enter choice: ").strip()

        if choice == "1":
            uid = input("  Enter your User ID: ").strip()
            user = registry.login(uid)
            if user:
                user.perform_action(library)

        elif choice == "2":
            name = input("  Enter student name  : ").strip()
            uid  = input("  Enter student ID    : ").strip()
            if name and uid:
                registry.register(Student(name, uid))
            else:
                print("  ⚠  Name and ID are required.")

        elif choice == "3":
            name = input("  Enter librarian name: ").strip()
            uid  = input("  Enter librarian ID  : ").strip()
            if name and uid:
                registry.register(Librarian(name, uid))
            else:
                print("  ⚠  Name and ID are required.")

        elif choice == "4":
            print("\n  ── Registered Users ──")
            registry.list_users()

        elif choice == "5":
            print("\n  Thank you for using the Smart Library System. Goodbye! 📚\n")
            break

        else:
            print("  ⚠  Invalid choice. Please try again.")


if __name__ == "__main__":
    main()