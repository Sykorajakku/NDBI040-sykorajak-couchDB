import requests
import timeit

COUCHDB_URL = "http://couchdb.admin:couchdb.admin@localhost:10010"
DATABASE_NAME = "library"
AUTHOR_ID = "author_2"

def get_author_and_books(couchdb_url, db_name, author_id):
    author_view_url = f"{couchdb_url}/{db_name}/_design/views/_view/authors"
    books_view_url = f"{couchdb_url}/{db_name}/_design/views/_view/books"
    
    author_resp = requests.get(author_view_url, params={"key": f'"{author_id}"'})
    books_resp = requests.get(books_view_url, params={"key": f'"{author_id}"'})
    
    if author_resp.status_code != 200:
        raise Exception(f"Error querying author view: {author_resp.text}")

    if books_resp.status_code != 200:
        raise Exception(f"Error querying books view: {books_resp.text}")

    author = author_resp.json()["rows"][0]["value"]
    books = [book["value"] for book in books_resp.json()["rows"]]

    return author, books

def join_with_include_docs():
    view_url = f"{COUCHDB_URL}/{DATABASE_NAME}/_design/views/_view/authors_books_include_docs"
    resp = requests.get(view_url, params={"key": f'"{AUTHOR_ID}"', "include_docs": "true"})
    return [(row["doc"]["bookLabel"], row["doc"]["authors"]) for row in resp.json()["rows"]]

def join_with_view_collation():
    view_url = f"{COUCHDB_URL}/{DATABASE_NAME}/_design/views/_view/authors_books_view_collation"
    resp = requests.get(view_url, params={"startkey": f'["{AUTHOR_ID}"]', "endkey": f'["{AUTHOR_ID}", {{}}]'})
    return [(row["value"]["bookLabel"], row["value"]["authors"]) for row in resp.json()["rows"] if len(row["key"]) > 1]

def join_with_python_code():
    author, books = get_author_and_books(COUCHDB_URL, DATABASE_NAME, AUTHOR_ID)
    return [(book, [AUTHOR_ID]) for book in books]

if __name__ == "__main__":
    include_docs_time = timeit.timeit(join_with_include_docs, number=1)
    view_collation_time = timeit.timeit(join_with_view_collation, number=1)
    python_code_time = timeit.timeit(join_with_python_code, number=1)

    print("Query times:")
    print(f"Include_docs: {include_docs_time:.6f} seconds")
    print(f"View collation: {view_collation_time:.6f} seconds")
    print(f"Python code: {python_code_time:.6f} seconds")
