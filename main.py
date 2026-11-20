#!/usr/bin/env python3
"""news-image-20261120: deliver the front page image to the output folder.

The front page (entry.png, 1024x1024, a one-page summary of world news
for Friday 20 November 2026) lives in this repository beside this file.
All this program does is copy it into $MAKEFUN_OUTPUT_DIR (falling back
to /output), after confirming the file is a complete PNG of the right
size. Standard library only, no network access, fully deterministic:
every run writes exactly the same bytes.
"""

import hashlib
import os
import struct
import sys

# First eight bytes of every PNG file.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The final 12 bytes of a complete PNG: an empty IEND chunk plus its
# fixed CRC value.
PNG_TRAILER = b"\x00\x00\x00\x00IEND\xaeB`\x82"
WANTED_DIMS = (1024, 1024)
MAX_BYTES = 1024 * 1024


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(base, "entry.png")
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(dest_dir, "entry.png")

    with open(source, "rb") as handle:
        payload = handle.read()

    # Cross-check the bytes read against the file size on disk, so a
    # short or torn read cannot slip through silently.
    if os.path.getsize(source) != len(payload):
        print("entry.png: size on disk does not match bytes read",
              file=sys.stderr)
        return 1

    if not payload.startswith(PNG_SIGNATURE):
        print("entry.png: not a PNG (bad signature)", file=sys.stderr)
        return 1
    if not payload.endswith(PNG_TRAILER):
        print("entry.png: truncated PNG (no IEND chunk)", file=sys.stderr)
        return 1
    img_w, img_h = struct.unpack(">II", payload[16:24])
    if (img_w, img_h) != WANTED_DIMS:
        print(f"entry.png: expected 1024x1024, found {img_w}x{img_h}",
              file=sys.stderr)
        return 1
    if len(payload) > MAX_BYTES:
        print("entry.png: larger than the 1 MiB cap", file=sys.stderr)
        return 1

    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as handle:
        handle.write(payload)

    checksum = hashlib.sha256(payload).hexdigest()
    print(f"wrote {dest} ({img_w}x{img_h}, {len(payload)} bytes, "
          f"sha256 {checksum})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
