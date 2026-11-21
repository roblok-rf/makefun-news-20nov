#!/usr/bin/env python3
"""Entry program for the make.fun bounty news-image-20261120 submission.

Copies the rendered front page (entry.png, in this directory) to the
output directory and prints its SHA-256 hash.

Deterministic: identical input bytes produce identical output bytes.
Standard library only; no network access.
"""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.exists(src):
        print("error: entry.png not found next to main.py", file=sys.stderr)
        return 1

    out_dir = "/output" if os.path.isdir("/output") else os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    # Copy the exact bytes; never re-encode.
    shutil.copyfile(src, dst)

    # The copy must be byte-identical to the source image.
    with open(src, "rb") as f:
        src_hash = hashlib.sha256(f.read()).hexdigest()

    digest = hashlib.sha256()
    with open(dst, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)

    if digest.hexdigest() != src_hash:
        print("error: copied bytes differ from entry.png", file=sys.stderr)
        return 1

    print("output:", dst)
    print("sha256:", digest.hexdigest())
    print("bytes:", os.path.getsize(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
