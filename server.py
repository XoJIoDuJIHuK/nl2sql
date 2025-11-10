from fastapi import FastAPI

app = FastAPI()


@app.post("/process")
async def process(data: dict):
    return {"result": f"Processed {data}"}


