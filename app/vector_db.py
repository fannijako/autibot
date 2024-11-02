from astrapy import DataAPIClient
import os
from utils import load_env

load_env()

client = DataAPIClient(os.environ.get('ASTRA_DB_TOKEN'))
db = client.get_database_by_api_endpoint(
    os.environ.get('ASTRA_DB_API_ENDPOINT')
    )

print(f"Connected to Astra DB: {db.list_collection_names()}")
