import requests
import json

# CouchDB instance URL and credentials
couchdb_url = "http://couchdb.admin:couchdb.admin@localhost:10010"
database_name = "demo_library"

# Create the demo_library database
create_db_url = f"{couchdb_url}/{database_name}"
create_db_response = requests.put(create_db_url)

if create_db_response.status_code in (201, 202):
    print(f"Database '{database_name}' created successfully")
else:
    print(f"Error creating database: {create_db_response.status_code}, {create_db_response.text}")
    exit(1)

# Insert the JSON document
document = {
    "_id": "author_3",
    "type": "author",
    "authorLabel": "Emil Cioran",
    "dob": "1911-04-08T00:00:00Z",
    "dod": "1995-06-20T00:00:00Z"
}

insert_doc_url = f"{couchdb_url}/{database_name}/{document['_id']}"
insert_doc_response = requests.put(insert_doc_url, data=json.dumps(document), headers={"Content-Type": "application/json"})

if insert_doc_response.status_code in (201, 202):
    print(f"Document inserted successfully: {insert_doc_response.text}")
else:
    print(f"Error inserting document: {insert_doc_response.status_code}, {insert_doc_response.text}")
    exit(1)

# Delete the demo_library database
delete_db_url = f"{couchdb_url}/{database_name}"
delete_db_response = requests.delete(delete_db_url)

if delete_db_response.status_code == 200:
    print(f"Database '{database_name}' deleted successfully")
else:
    print(f"Error deleting database: {delete_db_response.status_code}, {delete_db_response.text}")
    exit(1)
