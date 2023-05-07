import sys
import json
import random

from datetime import datetime, timedelta
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX schema: <http://schema.org/>

SELECT ?bookLabel ?genreLabel ?genreDescription ?freebase ?dop ?authorLabel ?dob ?dod (SAMPLE(?residenceName) AS ?singleResidenceName) WHERE {
  ?book wdt:P31 wd:Q571.
  ?book wdt:P50 ?author.
  ?author wdt:P31 wd:Q5.
  ?book rdfs:label ?bookLabel.
  ?author rdfs:label ?authorLabel.
  
  ?author wdt:P569 ?dob.
  
  OPTIONAL {
    ?author wdt:P570 ?dod.
  }
  
  OPTIONAL {
    ?book wdt:P577 ?dop.
  }
  
  OPTIONAL {
    ?book wdt:P646 ?freebase.
  }
  
  OPTIONAL {
    ?author wdt:P551 ?residence.
    ?residence rdfs:label ?residenceName.
    FILTER(LANG(?residenceName) = "en").
  }

  ?book wdt:P136 ?genre.
  ?genre rdfs:label ?genreLabel.
  ?genre schema:description ?genreDescription.
  
  FILTER(LANG(?genreLabel) = "en").
  FILTER(LANG(?genreDescription) = "en").
  FILTER(LANG(?bookLabel) = "en").
  FILTER(LANG(?authorLabel) = "en").
  FILTER(DATATYPE(?dob) = xsd:dateTime).
  FILTER(!BOUND(?dod) || DATATYPE(?dod) = xsd:dateTime).
}
GROUP BY ?bookLabel ?genreLabel ?genreDescription ?freebase ?dop ?authorLabel ?dob ?dod
LIMIT 10000"""

libraries_query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?libraryLabel ?countryLabel ?webpage ?isil
WHERE {
  ?library wdt:P31 wd:Q7075 . # ?library is an instance of (P31) Library (Q7075)
  ?library wdt:P17 ?country.
  ?country rdfs:label ?countryLabel.
  ?library wdt:P856 ?webpage.
  ?library wdt:P791 ?isil.
  
  FILTER(LANG(?countryLabel) = "en").
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
GROUP BY ?libraryLabel ?countryLabel ?webpage ?isil
LIMIT 100
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)
libraries_results = get_results(endpoint_url, libraries_query)

genres = {}
books = {}
authors = {}

genre_id = 1
book_id = 1
author_id = 1

for result in results["results"]["bindings"]:
    # Process genre
    genre_label = result["genreLabel"]["value"]
    genre_description = result["genreDescription"]["value"]
    
    if genre_label not in genres:
        genre_key = f"genre_{genre_id}"
        genre_id += 1
        genres[genre_label] = {
            "_id": genre_key,
            "type": "genre",
            "genreLabel": genre_label,
            "genreDescription": genre_description
        }
        
    # Process author
    author_label = result["authorLabel"]["value"]
    dob = result["dob"]["value"]
    dod = result.get("dod", {}).get("value", None)
    
    if author_label not in authors:
        author_key = f"author_{author_id}"
        author_id += 1
        authors[author_label] = {
            "_id": author_key,
            "type": "author",
            "authorLabel": author_label,
            "dob": dob,
            "dod": dod
        }
        
    # Process book
    book_label = result["bookLabel"]["value"]
    dop = result.get("dop", {}).get("value", None)
    freebase = result.get("freebase", {}).get("value", None)
    
    if book_label not in books:
        book_key = f"book_{book_id}"
        book_id += 1
        books[book_label] = {
            "_id": book_key,
            "type": "book",
            "bookLabel": book_label,
            "dop": dop,
            "freebase": freebase,
            "genres": [genres[genre_label]["_id"]],
            "authors": [authors[author_label]["_id"]]
        }
    else:
        books[book_label]["genres"].append(genres[genre_label]["_id"])
        if authors[author_label]["_id"] not in books[book_label]["authors"]:
            books[book_label]["authors"].append(authors[author_label]["_id"])

libraries = []
lease_offers = []
item_availabilities = ["Available", "NotAvailable", "Discontinued"]

# Generate 100 libraries
idx = 1
for result in libraries_results["results"]["bindings"]:
    library_label = result["libraryLabel"]["value"]
    isil = result["isil"]["value"]
    webpage = result["webpage"]["value"]
    country = result["countryLabel"]["value"]

    libraries.append({
        "_id": f"library_{idx + 1}",
        "type": "library",
        "name": library_label,
        "country": country,
        "webpage": webpage,
        "isil": isil
    })
    idx += 1

# Generate 10,000 lease offers
for i in range(1, 10001):
    # Randomly select a book
    book = random.choice(list(books.values()))

    # Randomly select a library
    library = random.choice(libraries)

    # Randomly select an item availability
    availability = random.choice(item_availabilities)

    # Generate random lease start and end dates
    lease_start = datetime.now() + timedelta(days=random.randint(-365, 365))
    lease_end = lease_start + timedelta(days=random.randint(1, 365))

    lease_offers.append({
        "_id": f"lease_offer_{i}",
        "type": "lease_offer",
        "bookId": book["_id"],
        "libraryId": library["_id"],
        "availability": availability,
        "leaseStart": lease_start.isoformat(),
        "leaseEnd": lease_end.isoformat()
    })

# Save libraries to libraries.json
with open("libraries.json", "w") as f:
    json.dump(libraries, f, indent=2)

# Save lease_offers to lease_offers.json
with open("lease_offers.json", "w") as f:
    json.dump(lease_offers, f, indent=2)

# Save genres to genres.json
with open("genres.json", "w") as f:
    json.dump(list(genres.values()), f, indent=2)

# Save authors to authors.json
with open("authors.json", "w") as f:
    json.dump(list(authors.values()), f, indent=2)

# Save books to books.json
with open("books.json", "w") as f:
    json.dump(list(books.values()), f, indent=2)