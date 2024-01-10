from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"message": "I am Douglas, you aren't Douglas."}
