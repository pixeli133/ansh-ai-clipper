# ANSH AI CLIPPER

Starter project for creating vertical clips from videos you own or have permission to use.

## Important limits
- This starter supports **video file upload**. A YouTube URL alone cannot be used to download media here; use YouTube's official download/export options when available, then upload the permitted video file.
- 10 Shorts per hour is a target, not a guarantee. The app makes short segments at evenly spaced candidate points; it does not yet understand which moments are funniest or most interesting.
- Long videos (2–10 hours) need substantial CPU, storage, and processing time. Free hosting may stop or time out.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app uses FFmpeg via `imageio-ffmpeg` and creates 9:16 MP4 clips. Subtitle generation and AI highlight ranking are not included in this starter build yet.
