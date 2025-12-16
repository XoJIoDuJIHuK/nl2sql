run-server:
	uvicorn server:app --port 8000 --reload

run-graphene-server:
	uvicorn graphene_server.main:app --port 8000 --reload
