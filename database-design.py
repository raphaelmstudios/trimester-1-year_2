from datetime import datetime
import json
import os


class Base:
    # Every object (book or user) has an id, and tracks when it was created/updated
    def __init__(self, id, created_at=None, updated_at=None):
        self.id = id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    # Save the object to a JSON file
    def save(self):
        self.updated_at = datetime.now()
        data = self.__dict__.copy()  # grab all the object's info as a dictionary
        filename = data.get("title") or data.get(
            "name"
        )  # books use title, users use name
        os.makedirs(
            self.folder_type, exist_ok=True
        )  # create the folder if it doesn't exist
        with open(f"{self.folder_type}/{filename}.json", "w") as f:
            json.dump(data, f, default=str)  # write the dictionary to a file

    # Load an object back from its JSON file
    @classmethod
    def load(cls, filename):
        try:
            with open(f"{cls.folder_type}/{filename}.json", "r") as f:
                data = json.load(f)  # read the file back as a dictionary
            obj = cls.__new__(cls)  # create a blank object without calling __init__
            obj.__dict__.update(data)  # fill it with the saved data
            obj.created_at = datetime.fromisoformat(
                data["created_at"]
            )  # convert date strings back to datetime
            obj.updated_at = datetime.fromisoformat(data["updated_at"])
            return obj
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None

    # Return a list of all saved objects in the folder
    @classmethod
    def list_all(cls):
        try:
            return [
                cls.load(f.replace(".json", "")) for f in os.listdir(cls.folder_type)
            ]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


class Book(Base):
    folder_type = "Books"  # all books are saved in the 'Books' folder

    def __init__(self, id, title, author, genre, year_published):
        super().__init__(id)  # pass id up to Base
        self.title = title
        self.author = author
        self.genre = genre
        self.year_published = year_published
        self.is_borrowed = False  # book is available by default
        self.borrowed_by = None  # no one has it yet


class User(Base):
    folder_type = "Users"  # all users are saved in the 'Users' folder

    def __init__(self, id, name):
        super().__init__(id)  # pass id up to Base
        self.name = name
        self.borrowed_books = []  # user starts with no borrowed books

    def borrow_book(self, book):
        # stop if the book is already taken
        if book.is_borrowed:
            print(f"{book.title} is already borrowed.")
            return

        # mark the book as borrowed
        book.is_borrowed = True
        book.borrowed_by = self.name
        self.borrowed_books.append(book.title)  # add to user's borrowed list
        book.save()  # update the book's file
        print(f"{self.name} has borrowed {book.title}.")

    def return_book(self, book):
        # stop if this user didn't borrow this book
        if book.title not in self.borrowed_books:
            print(
                f"{self.name} cannot return {book.title} because it was not borrowed by them."
            )
            return

        # mark the book as returned
        book.is_borrowed = False
        book.borrowed_by = None
        self.borrowed_books.remove(book.title)  # remove from user's borrowed list
        book.save()  # update the book's file
        print(f"{self.name} has returned {book.title}.")
