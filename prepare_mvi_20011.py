"""Download the UA-DETRAC MVI_20011 frames and encode the test video."""

import argparse
import tempfile
from pathlib import Path

import cv2
import numpy as np


REPO_ID = "kalyan1729/sentineledgedataset"
REVISION = "de18d2110ac93e94f9955029ee20341e4cd5ea61"
SEQUENCE = "DETRAC/DETRAC-Images/DETRAC-Images/MVI_20011"
FRAME_NAMES = tuple(f"img{number:05d}.jpg" for number in range(1, 665))
SIZE = (960, 540)
FPS = 25
OUTPUT = Path(__file__).resolve().parent / "ultralytics/yolo/v8/detect/MVI_20011.mp4"


def download_frames():
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("Install huggingface_hub==0.36.0 first.") from exc

    snapshot = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=REVISION,
        allow_patterns=[f"{SEQUENCE}/img[0-9][0-9][0-9][0-9][0-9].jpg"],
    )
    return Path(snapshot) / SEQUENCE


def encode_video(frames_dir):
    frames = [frames_dir / name for name in FRAME_NAMES]
    missing = [frame.name for frame in frames if not frame.is_file()]
    if missing:
        raise ValueError(f"Missing {len(missing)} frames in {frames_dir}: {', '.join(missing[:5])}")

    with tempfile.TemporaryDirectory(prefix="mvi20011-", dir=OUTPUT.parent) as temp_dir:
        temp_video = Path(temp_dir) / OUTPUT.name
        writer = cv2.VideoWriter(str(temp_video), cv2.VideoWriter_fourcc(*"mp4v"), FPS, SIZE)
        try:
            if not writer.isOpened():
                raise RuntimeError("OpenCV could not open an MP4 video writer.")
            for frame in frames:
                encoded = np.frombuffer(frame.read_bytes(), dtype=np.uint8)
                image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
                if image is None or (image.shape[1], image.shape[0]) != SIZE:
                    raise ValueError(f"Expected a readable {SIZE[0]}x{SIZE[1]} image: {frame}")
                writer.write(image)
        finally:
            writer.release()
        if OUTPUT.exists():
            raise FileExistsError(f"Video already exists: {OUTPUT}")
        temp_video.rename(OUTPUT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", type=Path, help="Use local frames instead of downloading.")
    args = parser.parse_args()
    if OUTPUT.exists():
        print(f"Using existing video: {OUTPUT}")
        return
    try:
        frames_dir = args.frames_dir if args.frames_dir is not None else download_frames()
        encode_video(frames_dir)
    except Exception as exc:
        parser.exit(1, f"Could not prepare MVI_20011: {exc}\n")
    print(f"Prepared {len(FRAME_NAMES)} frames at {FPS} FPS: {OUTPUT}")


if __name__ == "__main__":
    main()
