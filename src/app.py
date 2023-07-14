from typing import Optional
from datetime import date
from tabulate import tabulate
from collections import namedtuple
from src.schema import StatusEnum, CreateDataType, FetchByIdDataType
from src.database import (
    insert_data,
    fetch_by_id,
    update_data,
    delete_data,
    truncate_table,
    exit_program,
    count_books_read_completely,
    search_books_by_title,
    count_pending_books
)


class MenuDisplay:
    """
    MENU
    ----------
    1. DATA QUERY
       1. How many books were read completely during a specific period of time
       2. How many books are pending
       3. Search books by title
       77. Go back to Menu
       99. Exit
    2. DATA MANIPULATION
       1. INSERT DATA
       2. UPDATE DATA
       3. DELETE DATA
       4. TRUNCATE
       77. Go back to Menu
       99. Exit

    99. Exit
    """

    @staticmethod
    def display_menu():
        print(
            """
      WELCOME TO MY READ APP
      
      MENU
      ---------
      1. DATA QUERY
      2. DATA MANIPULATION
      99. Quit
      """
        )

    @staticmethod
    def display_DM_menu():
        print(
            """
      MENU > DATA MANIPULATION
      -------
      1. INSERT DATA
      2. UPDATE DATA
      3. DELETE DATA
      4. TRUNCATE
      77. Back To Menu
      99. Quit
      
      """
        )

    @staticmethod
    def display_DQ_menu():
        print(
            """
      MENU > DATA QUERY
      ---------
      1. How many books were read completely during a specific period of time?
      2. How many books do we have pending?
      3. Search books by title?
      77. Back To Menu
      99. Quit
      """
        )


class InputOption:
    @staticmethod
    def input_option_dm_insert() -> CreateDataType:
        username = InputOption.get_username()
        print("Please, provide the following details: ")
        book_title: str = input("Book title: ")
        book_desc: str = input("(Optional) Describe the book: ")
        status: StatusEnum = input(
            "(Optional) What is your current read status(pending, reading, complete): "
        )
        pct_read: str = input("(Optional) What percentage read: ")
        if pct_read:
            pct_read: int = int(pct_read)
        start_read_date: str = input("(Optional) Start reading date(YYYY-MM-DD): ")
        if start_read_date:
            start_read_date: date = date.fromisoformat(start_read_date)

        end_read_date: str = input("(Optional) end reading date(YYYY-MM-DD): ")
        if end_read_date:
            end_read_date: date = date.fromisoformat(end_read_date)

        return {
            "username": username,
            "book_title": book_title,
            "book_desc": book_desc if book_desc else None,
            "status": status if status else StatusEnum.pending,
            "pct_read": pct_read if pct_read else 0,
            "start_read_date": start_read_date if start_read_date else None,
            "end_read_date": end_read_date if end_read_date else None,
        }

    @staticmethod
    def input_option_dm_update():
        while True:
            id_to_update: int = int(input("Input book id to update: "))
            book: Optional[FetchByIdDataType] = fetch_by_id(id_to_update)
            if book is None:
                print("Book by that id doesn't exist. Please,  try again")
                continue
            else:
                print("Book info: ")
                InputOption.generate_table(book)
                print(
                    """
                   Fields to update?
                     1. book title
                     2. status
                     3. description
                     4. pct read
                     5. start date
                     6. end date   
               """
                )
                field_option = int(input("What field do you want to change? "))
                UpdatedInfo = namedtuple("UpdatedInfo", "book_id column value")

                if field_option == 1:
                    book_title = input("Enter the new title: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="title", value=book_title
                    )
                    return updated_info

                elif field_option == 3:
                    book_desc = input("Enter the new description: ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="book_desc", value=book_desc
                    )
                    return updated_info

                elif field_option == 4:
                    pct_read = int(input("Enter the new percentage read: "))
                    updated_info = UpdatedInfo(
                        book_id=id_to_update, column="pct_read", value=pct_read
                    )
                    return updated_info

                elif field_option == 5:
                    start_read_date = input("Enter the new start date (YYYY-MM-DD): ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update,
                        column="start_read_date",
                        value=date.fromisoformat(start_read_date),
                    )
                    return updated_info

                elif field_option == 6:
                    end_read_date = input("Enter the new end date (YYYY-MM-DD): ")
                    updated_info = UpdatedInfo(
                        book_id=id_to_update,
                        column="end_read_date",
                        value=date.fromisoformat(end_read_date),
                    )
                    return updated_info
                else:
                    print("Option not recognized. Please try again.")

    @staticmethod
    def generate_table(data):
        table = [
            ["title", "status", "desc", "pct", "SD", "ED"],
            data,
        ]
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

    @staticmethod
    def get_username() -> str:
        username = input("Enter your username: ")
        return username


def main():
    while True:
        MenuDisplay.display_menu()
        option: int = int(input("Choose an option to continue: "))
        if option == 1:
            while True:
                MenuDisplay.display_DQ_menu()
                query_option: int = int(input("Choose an option to continue: "))

                if query_option == 1:
                    start_date = input("Enter the start date (YYYY-MM-DD): ")
                    end_date = input("Enter the end date (YYYY-MM-DD): ")
                    count_books_read_completely(start_date, end_date)

                elif query_option == 2:
                    count_pending_books()

                elif query_option == 3:
                    title = input("Enter the title to search: ")
                    books: Optional[FetchByNameDataType] = search_books_by_title(title)

                    if books:
                        print("Search results:")
                        for book in books:
                            InputOption.generate_table(book)
                    else:
                        print("No books found with the given title.")

                elif query_option == 77:
                    break

                elif query_option == 99:
                    exit_program()

                else:
                    print("Option not recognized. Please try again.")
            else:
                print("Option not recognized. Please try again.")

        elif option == 2:
            while True:
                MenuDisplay.display_DM_menu()
                option: int = int(input("Choose an option to continue: "))
                if option == 1:
                    data: CreateDataType = InputOption.input_option_dm_insert()
                    id = insert_data(data)
                elif option == 2:
                    updated_data = InputOption.input_option_dm_update()
                    updated_id = update_data(
                        updated_data.book_id, updated_data.column, updated_data.value
                    )
                    if updated_id is not None:
                        print(f"Record with id {updated_id} updated successfully")
                    else:
                        print("Update failed!")

                elif option == 3:
                    book_id = int(input("Enter the book id to delete: "))
                    delete_data(book_id)

                elif option == 4:
                    truncate_table()

                elif option == 77:
                    break

                elif option == 99:
                    exit_program()

                else:
                    print("Option not recognized. Please try again.")
            else:
                print("Option not recognized. Please try again.")

        elif option == 99:
            print("EXIT THE PROGRAM")
            break
        else:
            print("Option not recognized. Please try again")


if __name__ == "__main__":
    main()
