from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello Sanuja! Your first FastAPI app works 🎉"}
