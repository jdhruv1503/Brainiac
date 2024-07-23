from simulate import WQSession
from fastapi import FastAPI, BackgroundTasks
from schemas import Alpha
from math import ceil
import os

credfiles = []

for file in os.listdir("creds"):
    if file.endswith(".json"):
        credfiles.append(f"creds/{file}")


sessions = [
    WQSession(json_fn=file) for file in credfiles if not file.endswith("example.json")
]


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(map(lambda x: lst[x * size : x * size + size], list(range(n))))


def simulate_all(data: list[Alpha]):
    global sessions

    data_chunks = chunk_into_n(data, len(sessions))

    # Assign each chunk of data to a WQSession
    for i, session in enumerate(sessions):
        print(f"Simulating for session {i}...")
        chunk = [dict(data_chunks[i][k]) for k in range(len(data_chunks[i]))]
        print(chunk)
        session.simulate(chunk)


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/add_alphas")
def add_simulate(alphas: list[Alpha], bgt: BackgroundTasks):
    bgt.add_task(simulate_all, alphas)
    return {"status": "Added to queue!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
