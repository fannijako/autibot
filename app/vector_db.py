import os

from astrapy import DataAPIClient


def create_astra_client():
    return DataAPIClient(os.environ.get('ASTRA_DB_TOKEN'))


def get_database(client):
    return client.get_database_by_api_endpoint(
        os.environ.get('ASTRA_DB_API_ENDPOINT')
        )


def similarity_search(client, query, collection_name = "documents", limit = 10):
    db = get_database(client)
    collection = db.get_collection(collection_name)
    results = collection.find(
        sort={"$vectorize": query},
        limit=limit,
        projection={"$vectorize": True},
        include_similarity=True,
    )
    return [{"$similarity": result["$similarity"], "$vectorize": result["$vectorize"]} for result in results]


def filter_on_similarity(results, threshold = 0.6):
    return [result for result in results if result['$similarity'] >= threshold]


def get_information_to_query(client, query, collection_name="documents", limit=10, threshold=0.6):
    return filter_on_similarity(similarity_search(client, query, collection_name=collection_name, limit=limit), threshold=threshold)
