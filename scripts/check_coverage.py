#!/usr/bin/env python3
import json
import sys
import argparse

def check_coverage(json_file, total_threshold, file_threshold):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found. Run coverage json first.")
        sys.exit(1)
    
    total_pct = data['totals']['percent_covered']
    print(f"Overall coverage: {total_pct:.2f}% (Threshold: {total_threshold}%)")
    
    failed = False
    if total_pct < total_threshold:
        print(f"❌ FAILED: Overall coverage {total_pct:.2f}% is below {total_threshold}%")
        failed = True
    else:
        print(f"✅ Overall coverage threshold met.")
    
    files_under_threshold = []
    # filter out files that are not in the source directory if needed, 
    # but coverage json usually only includes what we tracked.
    for file_path, file_data in data['files'].items():
        file_pct = file_data['summary']['percent_covered']
        if file_pct < file_threshold:
            files_under_threshold.append((file_path, file_pct))
    
    if files_under_threshold:
        print(f"\n❌ FAILED: The following files are below the {file_threshold}% per-file threshold:")
        for file_path, file_pct in sorted(files_under_threshold):
            print(f"  - {file_path}: {file_pct:.2f}%")
        failed = True
    else:
        print(f"✅ All files met the {file_threshold}% per-file threshold.")
        
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check coverage thresholds.")
    parser.add_argument("--json", default="coverage.json", help="Path to coverage JSON report")
    parser.add_argument("--total", type=float, default=90.0, help="Total coverage threshold (%)")
    parser.add_argument("--file", type=float, default=80.0, help="Per-file coverage threshold (%)")
    
    args = parser.parse_args()
    check_coverage(args.json, args.total, args.file)
