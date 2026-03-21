#!/usr/bin/env python3
"""
clip_retag.py — Re-tag all Pinry pins using RAM++ (Recognize Anything Model).

Runs locally (on a powerful machine), hits the remote Pinry API.

Requirements:
    pip install recognize-anything torch Pillow requests

Usage:
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN --dry-run
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN --limit 50
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN --pin-id 42
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN --dump-tags
    python scripts/clip_retag.py --api-url http://192.168.68.76:9002 --token YOUR_TOKEN --untagged-only
"""

import argparse
import io
import sys

import requests
import torch
from PIL import Image

# ---------------------------------------------------------------------------
# RAM setup
# ---------------------------------------------------------------------------
CHECKPOINT = "ram_plus_swin_large_14m.pth"
HF_REPO = "xinyu1205/recognize-anything-plus-model"


def load_ram(hf_repo: str = HF_REPO):
    from ram.models import ram_plus
    from ram import get_transform
    from huggingface_hub import hf_hub_download

    print(f"Loading RAM++ model from {hf_repo} ...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint = hf_hub_download(repo_id=hf_repo, filename=CHECKPOINT)
    transform = get_transform(image_size=384)
    model = ram_plus(pretrained=checkpoint, image_size=384, vit='swin_l')
    model.eval()
    model = model.to(device)
    print(f"  device: {device}")
    return model, transform, device


def tag_image(image: Image.Image, model, transform, device) -> list[str]:
    from ram import inference_ram as inference

    tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        res = inference(tensor, model)
    # res[0] is a string like "tag1 | tag2 | tag3"
    return [t.strip() for t in res[0].split('|') if t.strip()]


# ---------------------------------------------------------------------------
# Pinry API helpers
# ---------------------------------------------------------------------------
def make_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": f"Token {token}"})
    return s


def _rebase_url(next_url: str, api_url: str) -> str:
    """Replace host/port in a URL with the one from api_url."""
    from urllib.parse import urlparse, urlunparse
    base = urlparse(api_url)
    next_ = urlparse(next_url)
    return urlunparse(next_._replace(scheme=base.scheme, netloc=base.netloc))


def fetch_all_pins(session, api_url: str):
    """Yield every pin dict from the paginated API."""
    url = f"{api_url.rstrip('/')}/api/v2/pins/?limit=50&offset=0"
    while url:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        yield from data["results"]
        url = _rebase_url(data["next"], api_url) if data.get("next") else None


def fetch_one_pin(session, api_url: str, pin_id: int):
    url = f"{api_url.rstrip('/')}/api/v2/pins/{pin_id}/"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_image(session, image_url: str) -> Image.Image:
    resp = session.get(image_url, timeout=60, stream=True)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def fetch_all_tags(session, api_url: str):
    """Return sorted list of all tag names from the API."""
    url = f"{api_url.rstrip('/')}/api/v2/tags-auto-complete/"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return sorted(t["name"] for t in resp.json())


def clean_orphaned_tags(session, api_url: str, dry_run: bool = False):
    """Delete tags with no associated pins via the API."""
    url = f"{api_url.rstrip('/')}/api/v2/tags/orphans/"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data['count'] == 0:
        print("No orphaned tags found.")
        return
    print(f"{'Would delete' if dry_run else 'Deleting'} {data['count']} orphaned tags:")
    for name in sorted(data['tags']):
        print(f"  {name}")
    if not dry_run:
        resp = session.delete(url, timeout=30)
        resp.raise_for_status()
        print("Done.")


def patch_tags(session, api_url: str, pin_id: int, tags: list):
    url = f"{api_url.rstrip('/')}/api/v2/pins/{pin_id}/"
    resp = session.patch(url, json={"tags": tags}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def resolve_image_url(pin: dict, api_url: str) -> str:
    """Pull the best available image URL from a pin dict."""
    image = pin.get("image", {})
    for size in ("standard", "thumbnail", "square"):
        entry = image.get(size)
        if entry and entry.get("image"):
            url = entry["image"]
            if url.startswith("/"):
                url = api_url.rstrip("/") + url
            return _rebase_url(url, api_url)
    raw = image.get("image")
    if raw:
        if raw.startswith("/"):
            raw = api_url.rstrip("/") + raw
        return _rebase_url(raw, api_url)
    raise ValueError(f"No image URL found for pin {pin['id']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Re-tag Pinry pins with RAM++")
    parser.add_argument("--api-url", required=True, help="Base URL of your Pinry instance")
    parser.add_argument("--token", required=True, help="Pinry API auth token")
    parser.add_argument("--dry-run", action="store_true", help="Print tags without saving")
    parser.add_argument("--limit", type=int, default=None, help="Max pins to process")
    parser.add_argument("--pin-id", type=int, default=None, help="Process a single pin by ID")
    parser.add_argument("--model", default=HF_REPO,
                        help=f"HuggingFace repo for RAM++ (default: {HF_REPO})")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Seconds to wait between pins (default: 0)")
    parser.add_argument("--dump-tags", action="store_true",
                        help="Print all tags currently in the database and exit")
    parser.add_argument("--clean-orphans", action="store_true",
                        help="Delete tags with no pins via the API and exit (superuser only)")
    parser.add_argument("--untagged-only", action="store_true",
                        help="Only process pins that currently have no tags")
    args = parser.parse_args()

    if args.clean_orphans:
        session = make_session(args.token)
        clean_orphaned_tags(session, args.api_url, dry_run=args.dry_run)
        return

    session = make_session(args.token)

    if args.dump_tags:
        tags = fetch_all_tags(session, args.api_url)
        print(f"{len(tags)} tags in database:\n")
        for tag in tags:
            print(f"  {tag}")
        return

    model, transform, device = load_ram(args.model)

    if args.pin_id is not None:
        pins = [fetch_one_pin(session, args.api_url, args.pin_id)]
    else:
        pins = list(fetch_all_pins(session, args.api_url))
        if args.untagged_only:
            pins = [p for p in pins if not p.get("tags")]
        if args.limit:
            pins = pins[: args.limit]

    print(f"\nProcessing {len(pins)} pins ...\n")

    import time
    ok = skipped = 0
    for pin in pins:
        pin_id = pin["id"]
        try:
            image_url = resolve_image_url(pin, args.api_url)
            image = download_image(session, image_url)
            tags = tag_image(image, model, transform, device)

            if args.dry_run:
                print(f"  pin {pin_id}: {tags}  (dry run)")
            else:
                patch_tags(session, args.api_url, pin_id, tags)
                print(f"  pin {pin_id}: {tags}")
            ok += 1
        except Exception as exc:
            print(f"  pin {pin_id}: ERROR — {exc}", file=sys.stderr)
            skipped += 1
        if args.delay:
            time.sleep(args.delay)

    suffix = " (dry run)" if args.dry_run else ""
    print(f"\nDone{suffix}: {ok} tagged, {skipped} errors.")


if __name__ == "__main__":
    main()
