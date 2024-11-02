# autibot
RAG based chatbot trained on autism specific documents

## How to run the project

1. Clone the repository
2. Create Astra DB instance with an autibot database and a documents collection within it
3. Load the documents into the documents collection
4. Save the token in the .env file
5. Set the database API address in the .env file
6. Create a Discord app on the Discord developer portal
7. Set the token in the .env file
8. Add the App to the server
9. Create a Hugging Face account
10. Set the token in the .env file
11. Compose the docker container
12. Start chatting :)

```.env
DISCORD_TOKEN="<your-discord-app-token>"
HUGGINGFACE_TOKEN="<your-huggingface-token>"
ASTRA_DB_TOKEN="<your-astra-db-token>"
ASTRA_DB_API_ENDPOINT="https://<your-namespace>.apps.astra.datastax.com"
```

```bash
git clone https://github.com/fannijako/autibot.git
cd autibot
docker compose up --build
```

## Components

- **Discord App**: The app that allows the user to chat with the bot
- **Astra DB**: The database that stores the documents and the chat history
- **Hugging Face**: The model that is used to generate the responses

## Costs

- **Astra DB**: currently using a free tier
- **Hugging Face**: currently using a free tier
