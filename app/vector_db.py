"""
Module for interacting with the Astra Vector Database.
Client creation, database and collection retrieval, similarity search,
filtering on similarity and getting information to query.
"""

import os
import logging
from astrapy import DataAPIClient
from astrapy.database import Database


def create_astra_client() -> DataAPIClient:
    """
    Creates an Astra client.

    Params:
        None
    Returns:
        DataAPIClient: The Astra client.
    """
    astra_client = DataAPIClient(os.environ.get('ASTRA_DB_TOKEN'))
    logging.info('Astra client created.')

    return astra_client


def get_database(client: DataAPIClient) -> Database:
    """
    Gets the database from the Astra client.

    Params:
        client (DataAPIClient): The Astra client.

    Returns:
        Database: The database.
    """
    database = client.get_database_by_api_endpoint(
        os.environ.get('ASTRA_DB_API_ENDPOINT')
    )
    logging.info('Database retrieved.')

    return database


def similarity_search(client: DataAPIClient,
                      query: str,
                      collection_name: str = "documents",
                      limit: int = 10) -> list[dict]:
    """
    Performs a similarity search on the database.

    Params:
        client (DataAPIClient): The Astra client.
        query (str): The query.
        collection_name (str): The collection name.
        limit (int): The limit.

    Returns:
        list[dict]: The results.
    """

    db = get_database(client)
    collection = db.get_collection(collection_name)
    logging.info('Collection retrieved.')

    results = collection.find(
        sort={"$vectorize": query},
        limit=limit,
        projection={"$vectorize": True},
        include_similarity=True,
    )

    logging.info('Results retrieved from collection based on similarity search.')

    return [{"$similarity": result["$similarity"],
             "$vectorize": result["$vectorize"]}
            for result in results]


def filter_on_similarity(results: list[dict], threshold: float = 0.6) -> list[dict]:
    """
    Filters the results on similarity.

    Params:
        results (list[dict]): The results.
        threshold (float): The threshold.

    Returns:
        list[dict]: The filtered results.
    """

    filtered_results = [result for result in results if result['$similarity'] >= threshold]
    logging.info(f'Results filtered on similarity with threshold {threshold}.')

    return filtered_results


def get_information_to_query(client: DataAPIClient,
                             query: str,
                             collection_name: str = "documents",
                             limit: int = 10,
                             threshold: float = 0.6) -> list[dict]:
    """
    Gets the information to query from the database.

    Params:
        client (DataAPIClient): The Astra client.
        query (str): The query.
        collection_name (str): The collection name.
        limit (int): The limit.
        threshold (float): The threshold.

    Returns:
        list[dict]: The filtered results.
    """

    return filter_on_similarity(similarity_search(client,
                                                  query,
                                                  collection_name=collection_name,
                                                  limit=limit),
                                threshold=threshold)
