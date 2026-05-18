from unittest.mock import MagicMock, patch

from app.vector_db import (
    filter_on_similarity,
    similarity_search,
    get_information_to_query,
)


def test_filter_on_similarity_keeps_items_at_or_above_threshold():
    results = [
        {"$similarity": 0.9, "$vectorize": "a"},
        {"$similarity": 0.6, "$vectorize": "b"},
        {"$similarity": 0.59, "$vectorize": "c"},
        {"$similarity": 0.1, "$vectorize": "d"},
    ]

    filtered = filter_on_similarity(results, threshold=0.6)

    assert filtered == [
        {"$similarity": 0.9, "$vectorize": "a"},
        {"$similarity": 0.6, "$vectorize": "b"},
    ]


def test_filter_on_similarity_custom_threshold():
    results = [
        {"$similarity": 0.95, "$vectorize": "a"},
        {"$similarity": 0.8, "$vectorize": "b"},
    ]

    assert filter_on_similarity(results, threshold=0.9) == [
        {"$similarity": 0.95, "$vectorize": "a"},
    ]


def test_filter_on_similarity_empty_input():
    assert filter_on_similarity([], threshold=0.6) == []


def test_similarity_search_projects_and_passes_query(fake_astra_client):
    fake_collection = MagicMock()
    fake_collection.find.return_value = iter([
        {"$similarity": 0.8, "$vectorize": "doc-1", "other": "ignored"},
        {"$similarity": 0.7, "$vectorize": "doc-2", "other": "ignored"},
    ])
    fake_db = MagicMock()
    fake_db.get_collection.return_value = fake_collection
    fake_astra_client.get_database_by_api_endpoint.return_value = fake_db

    out = similarity_search(fake_astra_client, "kérdés", collection_name="docs", limit=5)

    fake_db.get_collection.assert_called_once_with("docs")
    fake_collection.find.assert_called_once_with(
        sort={"$vectorize": "kérdés"},
        limit=5,
        projection={"$vectorize": True},
        include_similarity=True,
    )
    assert out == [
        {"$similarity": 0.8, "$vectorize": "doc-1"},
        {"$similarity": 0.7, "$vectorize": "doc-2"},
    ]


def test_get_information_to_query_combines_search_and_filter(fake_astra_client):
    raw = [
        {"$similarity": 0.9, "$vectorize": "good"},
        {"$similarity": 0.3, "$vectorize": "noise"},
    ]
    with patch("app.vector_db.similarity_search", return_value=raw) as mock_search:
        out = get_information_to_query(
            fake_astra_client, "q", collection_name="documents", limit=10, threshold=0.6
        )

    mock_search.assert_called_once_with(
        fake_astra_client, "q", collection_name="documents", limit=10
    )
    assert out == [{"$similarity": 0.9, "$vectorize": "good"}]
