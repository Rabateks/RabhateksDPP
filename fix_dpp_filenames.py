#!/usr/bin/env python3
"""
fix_dpp_filenames.py
--------------------
Normalize DPP HTML filenames and update links inside RabateksDPPDashboard.html.

What it does:
1) Renames *.html files in the current folder to clean, URL-safe names:
   - lowercases
   - replaces spaces and unicode dashes with "-"
   - replaces "&" with "and"
   - removes problematic punctuation (e.g., ":" "—" "," "(" ")" "[" "]")
   - collapses multiple "-" into one
   - forces ".html" (lowercase) extension
2) Reads RabateksDPPDashboard.html and updates the dppUrls mapping values
   to the new filenames (based on the old->new renaming map).
3) Writes a backup of your dashboard before editing.

Usage:
    cd "/path/to/DPP FINAL VERSIONS"
    python3 fix_dpp_filenames.py
Options:
    --dry-run : Show what would change without renaming or writing files.
"""
import os
import re
import sys
import shutil
from unicodedata import normalize as uni_normalize

DASHBOARD_FILE = "RabateksDPPDashboard.html"  # main file name stays the same
BACKUP_SUFFIX = ".backup"

def slugify_filename(name: str) -> str:
    # Keep extension separated
    base, ext = os.path.splitext(name)
    ext = ".html" if ext.lower() in (".html", ".htm") else ext.lower()

    # Normalize unicode to NFKC and remove accents-ish
    s = uni_normalize("NFKC", base)
    s = s.strip().lower()

    # Replace common symbols first
    replacements = {
        "&": " and ",
        "—": "-",  # em dash
        "–": "-",  # en dash
        "‒": "-",  # figure dash
        "―": "-",  # horizontal bar
        "_": "-",  # underscores -> hyphen
        "/": "-",  # slashes -> hyphen
        ":": "-",  # colons -> hyphen
        ";": "-",
        ",": "-",
        "+": "-",
        "#": "-",
        "@": "-",
        "!": "",
        "?": "",
        "'": "",
        '"': "",
        "’": "",
        "“": "",
        "”": "",
        "(": "-",
        ")": "-",
        "[": "-",
        "]": "-",
        "{": "-",
        "}": "-",
        "|": "-",
        "\\": "-",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # Replace any whitespace with hyphen
    s = re.sub(r"\s+", "-", s)

    # Remove any character not alphanumeric, dot, or hyphen
    s = re.sub(r"[^a-z0-9\-.]", "", s)

    # Collapse multiple hyphens
    s = re.sub(r"-{2,}", "-", s)

    # Remove leading/trailing hyphens or dots
    s = s.strip("-.")

    # Ensure base not empty
    if not s:
        s = "file"

    return s + ext

def find_dpp_urls_block(html_text: str):
    """
    Finds the dppUrls object literal in JS:
        const dppUrls = { ... };
    Returns (start_index, end_index, block_text) or (None, None, None) if not found.
    """
    # This regex is forgiving about whitespace and quotes, but expects 'const dppUrls = { ... };'
    pattern = re.compile(
        r"const\s+dppUrls\s*=\s*\{(?P<body>.*?)\}\s*;",
        re.DOTALL
    )
    m = pattern.search(html_text)
    if not m:
        return None, None, None
    return m.start("body"), m.end("body"), m.group("body")

def replace_urls_in_block(block_text: str, rename_map: dict) -> str:
    """
    Replace string literal values in the object body using the rename_map.
    Example entries in block:
        'fibre': 'FibreDPPChatGPT08AUG25FINAL.html',
        "yarn": "Yarn_DPPChatGPTFINAL.html",
    """
    # String literal regex: match '...' or "..." capturing inner content
    def repl(match):
        quote = match.group("q")
        val = match.group("val")
        new_val = rename_map.get(val, val)  # only replace if renamed
        return f"{quote}{new_val}{quote}"

    string_val = re.compile(r"(?P<q>['\"])(?P<val>[^'\"]+?)(?P=q)")
    # But only replace on the right-hand side of key-value pairs; to be safe, apply globally
    return string_val.sub(repl, block_text)

def main():
    dry_run = "--dry-run" in sys.argv
    cwd = os.getcwd()
    print(f"Working directory: {cwd}")
    html_files = [f for f in os.listdir(cwd)
                  if os.path.isfile(f) and f.lower().endswith((".html", ".htm"))]

    if DASHBOARD_FILE not in html_files:
        print(f"ERROR: Cannot find '{DASHBOARD_FILE}' in this folder.")
        sys.exit(1)

    # Build rename map for all HTML files EXCEPT the dashboard (we keep its name)
    rename_map = {}
    targets = [f for f in html_files if f != DASHBOARD_FILE]

    for old in targets:
        new = slugify_filename(old)
        # Avoid collision with existing different file
        # If new already exists and it's not just a case-change of 'old', append a counter
        if new != old and os.path.exists(new):
            base, ext = os.path.splitext(new)
            i = 2
            candidate = f"{base}-{i}{ext}"
            while os.path.exists(candidate):
                i += 1
                candidate = f"{base}-{i}{ext}"
            new = candidate
        if new != old:
            rename_map[old] = new

    if not rename_map:
        print("Nothing to rename. Filenames already look clean.")
    else:
        print("Planned renames:")
        for old, new in rename_map.items():
            print(f"  {old}  -->  {new}")

    # Read dashboard and prepare to update mapping values that appear in rename_map values
    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        dashboard_html = f.read()

    start, end, body = find_dpp_urls_block(dashboard_html)
    if start is None:
        print("WARNING: Could not find 'const dppUrls = { ... };' block in RabateksDPPDashboard.html")
        print("Dashboard links will NOT be auto-updated. You can still manually adjust them.")
    else:
        # Build value-based map: old->new considering only base names present in the mapping
        # Extract values in the block to know which are referenced
        string_val = re.compile(r"(?P<q>['\"])(?P<val>[^'\"]+?)(?P=q)")
        referenced = set(m.group("val") for m in string_val.finditer(body))

        # Map only those referenced that were renamed
        mapping_for_block = {}
        for ref in referenced:
            # If block refers to a file that exists in current dir, check its rename
            if ref in rename_map:
                mapping_for_block[ref] = rename_map[ref]
            else:
                # If it's not in rename_map because file name already clean (or missing),
                # compute what its normalized name would be and if that differs AND the original file exists,
                # then include it.
                if os.path.exists(ref):
                    norm = slugify_filename(ref)
                    if norm != ref:
                        mapping_for_block[ref] = norm

        if mapping_for_block:
            print("\nDashboard link updates:")
            for old, new in mapping_for_block.items():
                print(f"  {old}  -->  {new}")
        else:
            print("\nNo dashboard mapping updates needed (or references not found).")

    if dry_run:
        print("\n--dry-run set: no files changed.")
        return

    # Perform renames
    for old, new in rename_map.items():
        print(f"Renaming: {old} -> {new}")
        os.rename(old, new)

    # Update dashboard (write a backup first)
    if start is not None:
        backup_path = DASHBOARD_FILE + BACKUP_SUFFIX
        if not os.path.exists(backup_path):
            shutil.copy2(DASHBOARD_FILE, backup_path)
            print(f"Backup created: {backup_path}")
        # Replace values in the object body
        new_body = replace_urls_in_block(body, mapping_for_block)
        new_html = dashboard_html[:start] + new_body + dashboard_html[end:]
        with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("Updated RabateksDPPDashboard.html link mapping.")
    print("\nDone.")
    print("Tip: Serve locally for testing:")
    print("  python3 -m http.server 8000  && open http://localhost:8000/RabateksDPPDashboard.html")

if __name__ == "__main__":
    main()
