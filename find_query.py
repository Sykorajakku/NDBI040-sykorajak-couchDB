import subprocess
import timeit
import requests

COUCHDB_URL = "http://couchdb.admin:couchdb.admin@localhost:10010"
DATABASE_NAME = "library"
LIBRARY_ID = "library_2"
MANGO_QUERY_FILE = "mango_lease_offers.json"

def mango_query(use_index):
    query = {
        "selector": {
            "type": "lease_offer",
            "libraryId": LIBRARY_ID
        },
        "fields": ["_id", "_rev", "bookId", "libraryId", "availability", "leaseStart", "leaseEnd"]
    }
    if use_index:
        query["use_index"] = "lease_offer_libraryId_index"

    resp = requests.post(f"{COUCHDB_URL}/{DATABASE_NAME}/_find", json=query)
    return resp.json()

def map_views_query():
    cmd = f'curl -X GET "{COUCHDB_URL}/{DATABASE_NAME}/_design/views/_view/lease_offers_by_libraryId?key=\\"{LIBRARY_ID}\\""'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout

if __name__ == "__main__":
    # Unindexed Mango query
    unindexed_mango_time = timeit.timeit(lambda: mango_query(False), number=1)

    # Indexed Mango query
    indexed_mango_time = timeit.timeit(lambda: mango_query(True), number=1)

    map_views_time = timeit.timeit(map_views_query, number=1)

    print("Query times:")
    print(f"Unindexed Mango query: {unindexed_mango_time:.6f} seconds")
    print(f"Indexed Mango query: {indexed_mango_time:.6f} seconds")
    print(f"Map views query: {map_views_time:.6f} seconds")