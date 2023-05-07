import requests
import json

couchdb_url = "http://couchdb.admin:couchdb.admin@localhost:10010"
database_name = "library"

def create_index():
    with open("find_index.json", "r") as f:
        index_definition = json.load(f)

    response = requests.post(
        f"{couchdb_url}/{database_name}/_index",
        json=index_definition,
        headers={"Content-Type": "application/json"},
    )

    print("Index creation response:", response.json())

design_document = {
    "_id": "_design/views",
    "views": {
        "libraries": {
            "map": "function(doc) { if (doc.type === 'library') { emit(doc.country, doc); } }"
        },
        "authors_by_birth_year": {
            "map": "function(doc) { if (doc.type === 'author' && doc.dob) { var birthYear = new Date(doc.dob).getFullYear(); emit(birthYear, 1); } }",
            "reduce": "function(keys, values, rereduce) { return sum(values); }"
        },
        "authors_by_birth_date_group_level": {
            "map": "function(doc) { if (doc.type === 'author' && doc.dob) { var date = new Date(doc.dob); var year = date.getFullYear(); var month = date.getMonth() + 1; var day = date.getDate(); emit([year, month, day], 1); } }",
            "reduce": "function(keys, values, rereduce) { return sum(values); }"
        },
        "authors_books_include_docs": {
            "map": "function(doc) { if (doc.type && doc.type === \"book\" && doc.authors) { for (var i = 0; i < doc.authors.length; i++) { emit(doc.authors[i], { _id: doc._id }); } } }"
        },
        "authors_books_view_collation": {
            "map": "function(doc) { if (doc.type && doc.type === \"book\" && doc.authors) { for (var i = 0; i < doc.authors.length; i++) { emit([doc.authors[i], doc._id], doc); } } else if (doc.type && doc.type === \"author\") { emit([doc._id], doc); } }"
        },
        "books": {
            "map": "function(doc) { if (doc.type && doc.type === \"book\") { for (var i = 0; i < doc.authors.length; i++) { emit(doc.authors[i], doc.bookLabel); } } }"
        },
        "authors": {
            "map": "function(doc) { if (doc.type && doc.type === \"author\") { emit(doc._id, doc.authorLabel); } }"
        },
        "lease_offers_by_libraryId": {
            "map": "function(doc) { if (doc.type && doc.type === \"lease_offer\" && doc.libraryId) { emit(doc.libraryId, doc); } }"
        }
    }
}

response = requests.put(
    f"{couchdb_url}/{database_name}/_design/views",
    data=json.dumps(design_document),
    headers={"Content-Type": "application/json"},
)

print(response.json())
create_index()