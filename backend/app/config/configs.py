from pathlib import Path

image_dir = Path(__file__).parent.parent / "data" / "images"
image_dir.mkdir(parents=True, exist_ok=True)
