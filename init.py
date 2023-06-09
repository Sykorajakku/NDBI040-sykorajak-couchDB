import os
import requests
import json

from dotenv import load_dotenv
from couchdb import Server

load_dotenv()

deployment_name = os.environ["COMPOSE_PROJECT_NAME"]
coordinator_node = "0"
additional_nodes = "1,2"
all_nodes = f"{coordinator_node},{additional_nodes}"

couchdb_user = os.environ["COUCHDB_USER"]
couchdb_password = os.environ["COUCHDB_PASSWORD"]
port_base = os.environ["PORT_BASE"]

def make_request(url, data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return response

for node_id in coordinator_node:
    url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}{node_id}/_cluster_setup"
    data = {
        "action": "enable_cluster",
        "bind_address": "0.0.0.0",
        "username": couchdb_user,
        "password": couchdb_user,
        "node_count": "3"
    }
    make_request(url, data)
    print("You may safely ignore the warning above.")

for node_id in additional_nodes.split(","):
    url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/_cluster_setup"
    
    data1 = {
        "action": "enable_cluster",
        "bind_address": "0.0.0.0",
        "username": couchdb_user,
        "password": couchdb_password,
        "port": 5984,
        "node_count": "3",
        "remote_node": f"couchdb-{node_id}.{deployment_name}",
        "remote_current_user": couchdb_user,
        "remote_current_password": couchdb_password
    }
    make_request(url, data1)
    
    data2 = {
        "action": "add_node",
        "host": f"couchdb-{node_id}.{deployment_name}",
        "port": 5984,
        "username": couchdb_user,
        "password": couchdb_password
    }
    make_request(url, data2)

url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/"
requests.get(url)

url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/_cluster_setup"
data = {"action": "finish_cluster"}
make_request(url, data)

url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/_cluster_setup"
requests.get(url)

url = f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/_membership"
requests.get(url)

print("Your cluster nodes are available at:")
for node_id in all_nodes.split(","):
    print(f"   http://{couchdb_user}:{couchdb_password}@localhost:{port_base}{node_id}")

# Connect to CouchDB
server = Server(f"http://{couchdb_user}:{couchdb_password}@127.0.0.1:{port_base}0/")
server.create("library")

with open("json/books.json", "r") as f:
    books = json.load(f)
    for book in books:
        server["library"].save(book)

with open("json/authors.json", "r") as f:
    authors = json.load(f)
    for author in authors:
        server["library"].save(author)

with open("json/genres.json", "r") as f:
    genres = json.load(f)
    for genre in genres:
        server["library"].save(genre)

with open("json/lease_offers.json", "r") as f:
    lease_offers = json.load(f)
    for lease_offer in lease_offers:
        server["library"].save(lease_offer)

with open("json/libraries.json", "r") as f:
    libraries = json.load(f)
    for library in libraries:
        server["library"].save(library)

couchdb_url = "http://couchdb.admin:couchdb.admin@localhost:10010"
database_name = "library"

def create_index():
    with open("query_scripts/find_index.json", "r") as f:
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