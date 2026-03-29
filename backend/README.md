# PauseCut Backend v0.6

This version adds a working FFmpeg preview renderer.

## What it does

- builds keep/speedup intervals from analyzed segments
- drops `cut` intervals
- renders `keep` intervals as normal clips
- renders `speedup` intervals at 2x
- concatenates all clips into a single preview MP4

## New endpoints

- `POST /job/{job_id}/preview`
- `GET /job/{job_id}/preview/download`

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notes

- ffmpeg must be installed on the host machine
- preview rendering uses the resolved direct stream URL when available
- full render and persistent preview metadata can be added next
