import pytest
from unittest.mock import Mock, patch

from app.vector_db import (
    create_astra_client,
    get_database,
    similarity_search,
    filter_on_similarity,
    get_information_to_query
)  


def test_filter_on_similarity():
    # Test data
    test_results = [
        {"$similarity": 0.8, "$vectorize": "text1"},
        {"$similarity": 0.5, "$vectorize": "text2"},
        {"$similarity": 0.7, "$vectorize": "text3"},
    ]
    
    # Test with default threshold (0.6)
    filtered = filter_on_similarity(test_results)
    assert len(filtered) == 2
    assert filtered[0]["$similarity"] == 0.8
    assert filtered[1]["$similarity"] == 0.7

    # Test with custom threshold
    filtered = filter_on_similarity(test_results, threshold=0.75)
    assert len(filtered) == 1
    assert filtered[0]["$similarity"] == 0.8

@patch('vector_db.DataAPIClient')
def test_create_astra_client(mock_client):
    with patch.dict('os.environ', {'ASTRA_DB_TOKEN': 'test-token'}):
        create_astra_client()
        mock_client.assert_called_once_with('test-token')

@patch('vector_db.get_database')
def test_similarity_search(mock_get_database):
    # Mock setup
    mock_collection = Mock()
    mock_db = Mock()
    mock_db.get_collection.return_value = mock_collection
    mock_get_database.return_value = mock_db
    
    mock_results = [
        {"$similarity": 0.8, "$vectorize": "text1"},
        {"$similarity": 0.7, "$vectorize": "text2"},
    ]
    mock_collection.find.return_value = mock_results
    
    # Test
    client = Mock()
    results = similarity_search(client, "test query")
    
    # Assertions
    mock_collection.find.assert_called_once_with(
        sort={"$vectorize": "test query"},
        limit=10,
        projection={"$vectorize": True},
        include_similarity=True,
    )
    assert len(results) == 2
    assert all(key in results[0] for key in ['$similarity', '$vectorize'])

def test_get_information_to_query():
    # Mock the similarity_search function
    with patch('vector_db.similarity_search') as mock_search:
        mock_search.return_value = [
            {"$similarity": 0.8, "$vectorize": "text1"},
            {"$similarity": 0.5, "$vectorize": "text2"},
        ]
        
        client = Mock()
        results = get_information_to_query(client, "test query")
        
        # Should only return results above threshold (0.6 by default)
        assert len(results) == 1
        assert results[0]["$similarity"] == 0.8
