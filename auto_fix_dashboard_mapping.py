#!/usr/bin/env python3
import os, re, sys, shutil

DASHBOARD_FILE = "RabateksDPPDashboard.html"
BACKUP_SUFFIX = ".backup"
TARGET_FILENAME = "rabateks-dpp-retail-distribution-management.html"

def main():
    if not os.path.exists(DASHBOARD_FILE):
        print(f"ERROR: {DASHBOARD_FILE} not found in current folder")
        sys.exit(1)

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Backup once
    backup_path = DASHBOARD_FILE + BACKUP_SUFFIX
    if not os.path.exists(backup_path):
        shutil.copy2(DASHBOARD_FILE, backup_path)
        print(f"Backup created: {backup_path}")

    changed = False

    # 1) Update inside the dppUrls object for key "retail"
    pattern = re.compile(r"([\"\']retail[\"\']\s*:\s*)([\"\'])(?P<val>[^\"\']+?)(\2)", re.DOTALL)
    def repl(m):
        nonlocal changed
        prefix = m.group(1)
        quote = m.group(2)
        oldval = m.group("val")
        if oldval != TARGET_FILENAME:
            changed = True
            return f"{prefix}{quote}{TARGET_FILENAME}{quote}"
        return m.group(0)

    new_html = pattern.sub(repl, html)

    # 2) Safety net: replace known old variants anywhere
    old_variants = [
        "Rabateks DPP — Retail/Distribution Management.html",
        "Rabateks DPP — Retail:Distribution Management.html",
        "Rabateks DPP - Retail/Distribution Management.html",
        "Rabateks DPP - Retail:Distribution Management.html",
    ]
    for ov in old_variants:
        if ov in new_html:
            new_html = new_html.replace(ov, TARGET_FILENAME)
            changed = True

    if not changed:
        print("No changes made. Mapping already points to the clean filename or pattern not found.")
        return

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("Updated 'retail' mapping to:", TARGET_FILENAME)
    print("Done. You can re-run: python3 check_dashboard_links.py")

if __name__ == "__main__":
    main()
