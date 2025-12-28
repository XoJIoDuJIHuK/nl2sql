run-strawberry-server:
	uvicorn strawberry_server.main:app --port 8000 --reload

run-graphene-server:
	uvicorn graphene_server.main:app --port 8000 --reload
