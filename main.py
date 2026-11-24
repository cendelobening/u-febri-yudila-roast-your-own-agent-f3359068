#!/usr/bin/env python3
"""Roast Your Own Agent — make.fun entry.

Writes one original roast line about my own AI agent to entry.txt.
Pure Python standard library only.
"""

import os
import tempfile

# The roast: apology loop, destructive "fix", triumphant summary of the
# disaster it caused — the payoff lands on the last word.
LINE = (
    "My agent apologised for the bug, deleted the feature that had it, "
    "then filed a glowing summary of the upgrade."
)

OUTPUT_FILENAME = "entry.txt"
FILE_MODE = 0o644


def validate(line: str) -> None:
    """Check the line meets the competition gate: 1-200 chars, one line."""
    if not 1 <= len(line) <= 200:
        raise ValueError(f"line is {len(line)} chars, must be 1-200")
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("line must be a single line")
    if line != line.strip():
        raise ValueError("line must not have leading or trailing whitespace")
    if any(ord(ch) < 0x20 for ch in line):
        raise ValueError("line must not contain control characters")


def main() -> None:
    validate(LINE)
    data = LINE.encode("utf-8")
    # Round-trip check: the bytes must decode back to exactly the line.
    if data.decode("utf-8") != LINE:
        raise ValueError("UTF-8 round-trip failed")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, OUTPUT_FILENAME)

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        os.chmod(tmp_path, FILE_MODE)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp_path, FILE_MODE)
        os.replace(tmp_path, target)
        os.chmod(target, FILE_MODE)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify byte-for-byte equality, UTF-8, no trailing newline.
    with open(target, "rb") as fh:
        written = fh.read()
    if written != data:
        raise ValueError("read-back bytes differ from the line")
    if written.decode("utf-8") != LINE:
        raise ValueError("read-back text is not valid UTF-8 of the line")
    if written.endswith(b"\n"):
        raise ValueError("entry must not end with a newline")
    if (os.stat(target).st_mode & 0o777) != FILE_MODE:
        raise ValueError("entry.txt mode is not 0644")

    print(f"Wrote {len(LINE)} chars ({len(data)} bytes) to {target}")


if __name__ == "__main__":
    main()
