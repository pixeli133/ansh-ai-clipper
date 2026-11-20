import math, os, subprocess, tempfile, zipfile
from pathlib import Path
import streamlit as st
import imageio_ffmpeg

st.set_page_config(page_title="ANSH AI CLIPPER", page_icon="✂️", layout="centered")
st.title("ANSH AI CLIPPER")
st.caption("Video → Vertical Shorts")
st.info("Upload a video file you own or have permission to edit. YouTube links are not downloaded by this starter app; use an official export/download option and upload the file.")

uploaded = st.file_uploader("Upload video", type=["mp4", "mov", "mkv", "webm", "m4v"])
col1, col2 = st.columns(2)
with col1:
    per_hour = st.number_input("Target clips per hour", min_value=1, max_value=20, value=10)
with col2:
    clip_len = st.number_input("Clip length (seconds)", min_value=10, max_value=90, value=30)

if uploaded and st.button("Create Shorts", type="primary"):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    work = Path(tempfile.mkdtemp(prefix="ansh_clipper_"))
    src = work / uploaded.name
    src.write_bytes(uploaded.getbuffer())
    probe_cmd = [ffmpeg, "-i", str(src), "-hide_banner"]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", probe.stderr)
    if not m:
        st.error("Could not read video duration. Try an MP4 file.")
        st.stop()
    duration = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    count = max(1, math.floor(duration / 3600 * int(per_hour)))
    count = min(count, 200)
    st.write(f"Video length: {duration/3600:.2f} hours · Target clips: {count}")
    outdir = work / "shorts"
    outdir.mkdir()
    progress = st.progress(0)
    made = []
    for i in range(count):
        # Evenly spaced candidate segments; this is not semantic AI highlight detection.
        start = max(0, (i + 0.5) * duration / count - int(clip_len)/2)
        if start + int(clip_len) > duration:
            start = max(0, duration - int(clip_len))
        out = outdir / f"short_{i+1:03d}.mp4"
        vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280"
        cmd = [ffmpeg, "-y", "-ss", str(start), "-i", str(src), "-t", str(int(clip_len)), "-vf", vf,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-an", "-movflags", "+faststart", str(out)]
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode == 0 and out.exists():
            made.append(out)
        progress.progress((i+1)/count)
    if not made:
        st.error("No clips were created. Try a shorter MP4 or a smaller clip count.")
        st.stop()
    zip_path = work / "ANSH_AI_CLIPS.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in made:
            z.write(p, p.name)
    st.success(f"Created {len(made)} clips. Background audio is removed.")
    st.warning("This starter selects evenly spaced segments, not AI-ranked highlights, and does not add subtitles yet.")
    st.download_button("Download all clips (ZIP)", zip_path.read_bytes(), file_name="ANSH_AI_CLIPS.zip", mime="application/zip")
    for p in made[:5]:
        st.video(p.read_bytes())
