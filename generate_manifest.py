#!/usr/bin/env python3
"""
Generate manifest files (CSV and JSON) for all HTML files in the repository.
Uses naming convention: first_3_letters_last_3_digits
"""

import csv
import json
import os
import re
from pathlib import Path


def derive_prefix(name: str) -> str:
    """Extract first 3 letters from filename, pad with 'x' if needed."""
    letters = re.sub(r'[^A-Za-z]', '', name).lower()
    prefix = (letters[:3] if letters else '').ljust(3, 'x')
    
    # Use 'amx' (AM) as default for files without clear 3-letter prefix
    if len(letters) < 3:
        return 'amx'
    
    return prefix


def derive_last3(name: str) -> str:
    """
    Extract last 3 digits before .html extension.
    Handles patterns like:
    - (10).html -> 010
    - -07.html -> 007
    - .580.html -> 580
    - .html (no digits) -> 000
    """
    # First try: (digits).html pattern
    m = re.search(r'\((\d+)\)\.html?$', name, flags=re.IGNORECASE)
    if m:
        digits = m.group(1)
        return digits.zfill(3)[-3:]  # Pad and take last 3
    
    # Second try: -digits.html or .digits.html pattern
    m = re.search(r'[-.](\d+)\.html?$', name, flags=re.IGNORECASE)
    if m:
        digits = m.group(1)
        return digits.zfill(3)[-3:]  # Pad and take last 3
    
    # No digits found
    return "000"


def scan_html_files(root_dir: str) -> list:
    """Scan directory for all HTML files and generate manifest entries."""
    manifest = []
    root_path = Path(root_dir)
    
    # Find all HTML files
    html_files = sorted(root_path.glob("*.html"))
    
    for file_path in html_files:
        filename = file_path.name
        prefix = derive_prefix(filename)
        last3 = derive_last3(filename)
        
        manifest.append({
            "id": f"{prefix}_{last3}",
            "prefix": prefix,
            "last3": last3,
            "file": filename
        })
    
    # Sort by prefix first, then by filename within each prefix group
    # This ensures arcs align with needle position
    manifest.sort(key=lambda x: (x['prefix'], x['file']))
    
    return manifest


def write_manifest(manifest: list, output_dir: str):
    """Write manifest to CSV and JSON files."""
    csv_path = os.path.join(output_dir, "manifest.csv")
    json_path = os.path.join(output_dir, "manifest.json")
    
    # Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        if manifest:
            w = csv.DictWriter(fp, fieldnames=["id", "prefix", "last3", "file"])
            w.writeheader()
            w.writerows(manifest)
    
    # Write JSON
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2, ensure_ascii=False)
    
    return csv_path, json_path


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Scanning HTML files in: {script_dir}")
    manifest = scan_html_files(script_dir)
    
    print(f"Found {len(manifest)} HTML files")
    
    csv_path, json_path = write_manifest(manifest, script_dir)
    
    print(f"\nManifest files created:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    
    # Show first few entries
    print(f"\nFirst 5 entries:")
    for entry in manifest[:5]:
        print(f"  {entry['id']:15} -> {entry['file']}")
    
    # Show some statistics
    prefixes = {}
    for entry in manifest:
        prefix = entry['prefix']
        prefixes[prefix] = prefixes.get(prefix, 0) + 1
    
    print(f"\nPrefix distribution:")
    for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1])[:10]:
        print(f"  {prefix}: {count} files")


if __name__ == "__main__":
    main()
