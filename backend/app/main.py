from fastapi import FastAPI

app = FastAPI(
    title="Appna Bank AI",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Appna Bank AI"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
