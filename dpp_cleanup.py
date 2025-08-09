#!/usr/bin/env python3
"""
dpp_cleanup.py
- Move conflicting clean-named HTML files to OLD_FILES
- Normalize HTML filenames to URL-safe slugs (lowercase, hyphens)
- Update dppUrls mapping inside RabateksDPPDashboard.html
- Create a .backup of the dashboard before editing
Usage:
  python3 dpp_cleanup.py --dry-run   # simulate
  python3 dpp_cleanup.py             # apply
"""
import os, re, sys, shutil
from unicodedata import normalize as uni_normalize

DASHBOARD_FILE = "RabateksDPPDashboard.html"
BACKUP_SUFFIX = ".backup"
OLD_DIR = "OLD_FILES"

def slugify_filename(name: str) -> str:
    base, ext = os.path.splitext(name)
    ext = ".html" if ext.lower() in (".html", ".htm") else ext.lower()
    s = uni_normalize("NFKC", base).strip().lower()
    replacements = {
        "&": " and ", "—": "-", "–": "-", "‒": "-", "―": "-",
        "_": "-", "/": "-", ":": "-", ";": "-", ",": "-",
        "+": "-", "#": "-", "@": "-", "!": "", "?": "",
        "'": "", '"': "", "’": "", "“": "", "”": "",
        "(": "-", ")": "-", "[": "-", "]": "-", "{": "-", "}": "-",
        "|": "-", "\\": "-"
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-.]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-.")
    if not s: s = "file"
    return s + ext

def find_dpp_urls_block(html_text: str):
    pat = re.compile(r"const\s+dppUrls\s*=\s*\{(?P<body>.*?)\}\s*;", re.DOTALL)
    m = pat.search(html_text)
    if not m: return None, None, None
    return m.start("body"), m.end("body"), m.group("body")

def replace_urls_in_block(block_text: str, rename_map: dict) -> str:
    def repl(m):
        q, val = m.group("q"), m.group("val")
        return f"{q}{rename_map.get(val, val)}{q}"
    string_val = re.compile(r"(?P<q>['\"])(?P<val>[^'\"]+?)(?P=q)")
    return string_val.sub(repl, block_text)

def main():
    dry = "--dry-run" in sys.argv
    cwd = os.getcwd()
    print(f"Working in: {cwd}")
    html_files = [f for f in os.listdir(cwd)
                  if os.path.isfile(f) and f.lower().endswith((".html", ".htm"))]
    if DASHBOARD_FILE not in html_files:
        print(f"ERROR: '{DASHBOARD_FILE}' not found here.")
        sys.exit(1)

    rename_map = {}
    targets = [f for f in html_files if f != DASHBOARD_FILE]
    for old in targets:
        new = slugify_filename(old)
        if new != old:
            rename_map[old] = new

    if rename_map:
        conflicts = [v for k, v in rename_map.items() if os.path.exists(v)]
    else:
        conflicts = []
    if conflicts:
        print("\nConflicts to secure (will move existing clean-named files to OLD_FILES):")
        for c in conflicts: print("  ", c)
    else:
        print("\nNo conflicts detected.")

    if not dry and conflicts:
        os.makedirs(OLD_DIR, exist_ok=True)
        for c in conflicts:
            src = os.path.join(cwd, c)
            dst = os.path.join(cwd, OLD_DIR, c)
            base, ext = os.path.splitext(dst)
            i = 2
            while os.path.exists(dst):
                dst = f"{base}-{i}{ext}"
                i += 1
            print(f"Moving: {src}  ->  {dst}")
            shutil.move(src, dst)

    if rename_map:
        print("\nPlanned renames:")
        for old, new in rename_map.items():
            print(f"  {old}  -->  {new}")
    else:
        print("\nNothing to rename. Filenames already look clean.")

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        dashboard_html = f.read()
    start, end, body = find_dpp_urls_block(dashboard_html)
    if start is None:
        print("\nWARNING: Could not find mapping block.")
        mapping_for_block = {}
    else:
        string_val = re.compile(r"(?P<q>['\"])(?P<val>[^'\"]+?)(?P=q)")
        referenced = set(m.group("val") for m in string_val.finditer(body))
        mapping_for_block = {}
        for ref in referenced:
            if ref in rename_map:
                mapping_for_block[ref] = rename_map[ref]
            elif os.path.exists(ref):
                norm = slugify_filename(ref)
                if norm != ref:
                    mapping_for_block[ref] = norm
        if mapping_for_block:
            print("\nDashboard link updates:")
            for old, new in mapping_for_block.items():
                print(f"  {old}  -->  {new}")
        else:
            print("\nNo dashboard mapping updates needed.")

    if dry:
        print("\n--dry-run complete. No changes made.")
        return

    for old, new in rename_map.items():
        if old == new: continue
        print(f"Renaming: {old} -> {new}")
        if os.path.exists(new):
            base, ext = os.path.splitext(new)
            i = 2
            candidate = f"{base}-{i}{ext}"
            while os.path.exists(candidate):
                i += 1
                candidate = f"{base}-{i}{ext}"
            new = candidate
            print(f"  Target existed; using: {new}")
        os.rename(old, new)

    if start is not None:
        backup_path = DASHBOARD_FILE + BACKUP_SUFFIX
        if not os.path.exists(backup_path):
            shutil.copy2(DASHBOARD_FILE, backup_path)
            print(f"Backup created: {backup_path}")
        new_body = replace_urls_in_block(body, mapping_for_block)
        new_html = dashboard_html[:start] + new_body + dashboard_html[end:]
        with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("Updated dashboard mapping.")

    print("\nDone.")
    print("Test with:")
    print("  python3 -m http.server 8000")
    print("  open http://localhost:8000/RabateksDPPDashboard.html")

if __name__ == "__main__":
    main()
