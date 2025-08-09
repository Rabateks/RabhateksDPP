#!/usr/bin/env python3
import os, re

DASHBOARD_FILE = "RabateksDPPDashboard.html"

def main():
    if not os.path.exists(DASHBOARD_FILE):
        print(f"ERROR: {DASHBOARD_FILE} not found in current folder")
        return

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Extract all string literals ending with .html inside the file
    pattern = re.compile(r"(?P<q>['\"])(?P<val>[^'\"]+?)(?P=q)")
    urls = set(m.group("val") for m in pattern.finditer(html) if m.group("val").lower().endswith(".html"))

    html_files = set(f for f in os.listdir(".") if os.path.isfile(f) and f.lower().endswith(".html"))

    missing = [u for u in urls if u not in html_files]
    unused = [f for f in html_files if f not in urls and f != DASHBOARD_FILE]

    print("=== Dashboard Link Check ===\n")
    for u in sorted(urls):
        if u in html_files:
            print(f"✅ OK       {u}")
        else:
            print(f"❌ MISSING  {u}")

    if unused:
        print("\n⚠️ UNUSED files (in folder but not in dashboard):")
        for f in sorted(unused):
            print(f"   {f}")
    else:
        print("\nNo unused files.")

    print("\nCheck complete.")

if __name__ == '__main__':
    main()
