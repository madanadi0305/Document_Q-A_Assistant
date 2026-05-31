# Document Summarizer - Command Instructions

This guide provides commands to run the app with and without Docker.

## Prerequisites

- Install Docker Desktop
- Open terminal in project root:
  - `c:\Users\madan\Downloads\AI Projects`
- Ensure `.env` exists with:
  - `OPENAI_SECRET_KEY=your_openai_key`

## Run With Docker Compose

### 1) Build and start the app

```bash
docker compose up --build
```

The app is interactive. Keep the terminal open and enter inputs when prompted.

### 2) Stop the app

- Press `Ctrl + C` in the same terminal

### 3) Remove container resources after stopping

```bash
docker compose down
```

## Run In Background (Detached Mode)

### 1) Start in detached mode

```bash
docker compose up -d --build
```

### 2) View logs

```bash
docker compose logs -f
```

### 3) Stop detached containers

```bash
docker compose down
```

## Optional: Rebuild Only

```bash
docker compose build --no-cache
```

## Optional: Start Without Rebuilding

```bash
docker compose up
```

## Useful Docker Commands

### List running containers

```bash
docker ps
```

### Open shell inside the running container

```bash
docker exec -it document-summarizer sh
```

## Notes

- The compose setup mounts your local project into the container (`./:/app`), so:
  - document files are available directly
  - log files (`user_logs.txt`, `output_logs.txt`, `error_logs.txt`) persist locally
  - prompt files (`prompt_template.md`, `prompt_versions.json`) update live
- If you update dependencies in `requirements.txt`, rebuild:
  - `docker compose up --build`

## Run Without Docker (Local Python)

### 1) Open terminal in project root

```powershell
cd "c:\Users\madan\Downloads\AI Projects"
```

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install -r requirements.txt
```

### 4) Create `.env` file

Add this key:

```env
OPENAI_SECRET_KEY=your_openai_key
```

### 5) Run the app

```powershell
python .\DocumentSummarizer.py
```

### 6) Stop the app

- Press `Ctrl + C`

## Optional Local Troubleshooting

### Deactivate virtual environment

```powershell
deactivate
```

### Reinstall dependencies cleanly

```powershell
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```
