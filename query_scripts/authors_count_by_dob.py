import requests
import json

# CouchDB instance URL and credentials
couchdb_url = "http://couchdb.admin:couchdb.admin@localhost:10010"
database_name = "library"
view_name = "authors_by_birth_date_group_level"

# Query view with different group_level values
group_level_queries = [
    (1, [1896]),  # Born in 1896
    (2, [1896, 7]),  # Born in July 1896
    (3, [1896, 7, 4])  # Born on 4th July 1896
]

for group_level, start_key in group_level_queries:
    view_url = f"{couchdb_url}/{database_name}/_design/views/_view/{view_name}"
    query_parameters = {
        "start_key": json.dumps(start_key),
        "end_key": json.dumps(start_key + [{}]),  # Add an empty object {} to match all keys with the same prefix
        "group_level": group_level,
        "reduce": "true"
    }

    response = requests.get(view_url, params=query_parameters)

    if response.status_code == 200:
        print(f"Group level {group_level} results:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error querying view with group_level {group_level}: {response.status_code}, {response.text}")
