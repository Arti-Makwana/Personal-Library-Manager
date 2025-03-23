import streamlit as st
import sqlite3
import pandas as pd

# Database Helper Functions
def execute_query(query, params=()):
    """Executes a SQL query and commits changes."""
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_data(query, params=()):
    """Fetches data from the database."""
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize App
st.title("📚 Personal Library Manager")

# Sidebar Menu
menu = ["Add Book", "View Books", "Search Books", "Update Book", "Delete Book"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Add a Book ---
if choice == "Add Book":
    st.subheader("Add a New Book")
    
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    genre = st.text_input("Genre")
    year = st.number_input("Publication Year", min_value=0, max_value=2100, step=1)
    status = st.selectbox("Status", ["Read", "Unread"])

    if st.button("Add Book"):
        if title and author:
            execute_query("INSERT INTO books (title, author, genre, year, status) VALUES (?, ?, ?, ?, ?)",
                          (title, author, genre, year, status))
            st.success(f"📖 '{title}' by {author} added successfully!")
        else:
            st.warning("⚠️ Title and Author are required!")

# --- View Books ---
elif choice == "View Books":
    st.subheader("📖 Book Collection")
    books = fetch_data("SELECT * FROM books")

    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Year", "Status"])
        st.dataframe(df)
    else:
        st.info("📚 No books found! Add some books first.")

# --- Search Books ---
elif choice == "Search Books":
    st.subheader("🔍 Search Books")
    
    search_term = st.text_input("Enter book title or author name")
    if st.button("Search"):
        results = fetch_data("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                             ('%' + search_term + '%', '%' + search_term + '%'))
        if results:
            df = pd.DataFrame(results, columns=["ID", "Title", "Author", "Genre", "Year", "Status"])
            st.dataframe(df)
        else:
            st.warning("⚠️ No matching books found.")

# --- Update Book ---
elif choice == "Update Book":
    st.subheader("✏️ Update Book Details")

    book_list = fetch_data("SELECT id, title FROM books")
    book_dict = {f"{b[0]} - {b[1]}": b[0] for b in book_list}
    selected_book = st.selectbox("Select a Book to Update", list(book_dict.keys()))

    if selected_book:
        book_id = book_dict[selected_book]
        book_details = fetch_data("SELECT * FROM books WHERE id=?", (book_id,))
        
        if book_details:
            book = book_details[0]
            title = st.text_input("Book Title", value=book[1])
            author = st.text_input("Author", value=book[2])
            genre = st.text_input("Genre", value=book[3])
            year = st.number_input("Publication Year", min_value=0, max_value=2100, value=book[4], step=1)
            status = st.selectbox("Status", ["Read", "Unread"], index=0 if book[5] == "Read" else 1)

            if st.button("Update Book"):
                execute_query("UPDATE books SET title=?, author=?, genre=?, year=?, status=? WHERE id=?",
                              (title, author, genre, year, status, book_id))
                st.success(f"📖 '{title}' updated successfully!")

# --- Delete Book ---
elif choice == "Delete Book":
    st.subheader("🗑️ Delete a Book")

    book_list = fetch_data("SELECT id, title FROM books")
    book_dict = {f"{b[0]} - {b[1]}": b[0] for b in book_list}
    selected_book = st.selectbox("Select a Book to Delete", list(book_dict.keys()))

    if st.button("Delete Book"):
        book_id = book_dict[selected_book]
        execute_query("DELETE FROM books WHERE id=?", (book_id,))
        st.success(f"📕 Book deleted successfully!")



