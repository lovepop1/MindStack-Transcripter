# MindStack Transcript Service

This repository contains a simple Python microservice built with FastAPI. It provides an HTTP API to fetch and return transcripts from YouTube videos using the `youtube-transcript-api` package. The service is designed to be consumed by a frontend (e.g. a Next.js application), but it can also be used standalone.

## Features

- FastAPI-based HTTP server
- CORS enabled for all origins (configurable)
- Endpoint to retrieve raw transcript text for a given YouTube video ID
- Error handling for missing video IDs and API failures

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`:
  ```txt
  fastapi==0.110.0
  uvicorn==0.28.0
  youtube-transcript-api==0.6.2
  ```

## Setup

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
   ```

   The service will be available at `http://localhost:8000`.

## API Endpoints

### `GET /`
Returns a simple health check message.

**Response**:
```json
{
  "status": "ok",
  "message": "MindStack Python Microservice is running"
}
```

### `GET /api/transcript?v=<VIDEO_ID>`
Fetches an English or Hindi transcript for the provided YouTube video ID.

- **Query parameter**: `v` (required) – the YouTube video ID (e.g., `dQw4w9WgXcQ`).

**Success Response** (200):
```json
{
  "transcript": "...full transcript text..."
}
```

**Error Responses**:
- 400 – Missing `v` parameter.
- 500 – Error fetching transcript (e.g., video unavailable, no transcript found, etc.).

## Deployment

This service can be deployed on any platform that supports Python applications. For simple deployments:

- Dockerize the app or
- Use a Python hosting service (e.g. Heroku, Vercel serverless functions, etc.)

The `vercel.json` file is included for deployment on Vercel.

## Notes

- CORS is currently open to all origins; restrict this in production if needed.
- The transcript API supports multiple languages; this service prioritizes English (`en`, `en-US`, `en-GB`) and Hindi (`hi`).

## License

Specify license information here if applicable.

## Author

MindStack Team
