run-strawberry-server:
	uv run uvicorn strawberry_server.main:app --port 8000 --reload

run-graphene-server:
	uv run uvicorn graphene_server.main:app --port 8000 --reload
