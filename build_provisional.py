from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
COMMON_ROOT = PROJECT_ROOT / "common"
INDUCTION_ROOT = PROJECT_ROOT / "general-induction"
BUILD_MODULES = PROJECT_ROOT / "scripts" / "build_provisional_modules.py"

ROOT_REDIRECT = """<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0; url=/general-induction/">
  <title>General Induction (Provisional) | clubSENsational</title>
  <script>location.replace("/general-induction/");</script>
</head>
<body><p><a href="/general-induction/">Continue to General Induction</a></p></body>
</html>
"""

NOT_FOUND = """<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="UTF-8"><title>Not found</title></head>
<body style="font-family:Montserrat,sans-serif;text-align:center;padding:40px;">
<h1>Page not found</h1><p><a href="/general-induction/">Return to General Induction</a></p></body></html>
"""


def main() -> None:
    subprocess.run([sys.executable, str(BUILD_MODULES)], check=True, cwd=PROJECT_ROOT)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(COMMON_ROOT / "assets", DIST_DIR / "assets", dirs_exist_ok=True)
    shutil.copytree(COMMON_ROOT / "shared", DIST_DIR / "shared", dirs_exist_ok=True)
    (DIST_DIR / "general-induction").mkdir(parents=True)
    shutil.copy2(INDUCTION_ROOT / "dashboard" / "index.html", DIST_DIR / "general-induction" / "index.html")
    for n in range(1, 7):
        src = INDUCTION_ROOT / "modules" / f"module-{n}" / "index.html"
        dest = DIST_DIR / "general-induction" / "modules" / f"module-{n}" / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    (DIST_DIR / "index.html").write_text(ROOT_REDIRECT, encoding="utf-8")
    (DIST_DIR / "404.html").write_text(NOT_FOUND, encoding="utf-8")
    print(f"Built provisional induction into {DIST_DIR}")


if __name__ == "__main__":
    main()
