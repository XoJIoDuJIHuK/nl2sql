run-server:
	uvicorn server:app --port 8000 --reload

run-graphql-server:
	uvicorn graphql_server.main:app --port 8000 --reload
