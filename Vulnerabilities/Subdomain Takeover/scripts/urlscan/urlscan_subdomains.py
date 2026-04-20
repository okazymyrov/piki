#!/usr/bin/env python3
import argparse
import concurrent.futures
import csv
import glob
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

import requests

API_URL = "https://pro.urlscan.io/api/v1/search"


def normalize_domain(raw: str) -> str:
    raw = raw.strip().lower()
    if not raw:
        return ""
    if "://" in raw:
        try:
            parsed = urlparse(raw)
            if parsed.hostname:
                return parsed.hostname.rstrip(".")
        except Exception:
            pass
    if "/" in raw:
        raw = raw.split("/", 1)[0]
    return raw.rstrip(".")


def load_domains_from_csv(path: str) -> list[str]:
    """Parse a semicolon-delimited CSV and extract all domains from the 'Domains' column."""
    domains: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        # Find the Domains column (case-insensitive)
        domain_col = None
        if reader.fieldnames:
            for col in reader.fieldnames:
                if col.strip().lower() == "domains":
                    domain_col = col
                    break

        if domain_col is None:
            print("Error: No 'Domains' column found in CSV.", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            cell = row.get(domain_col, "")
            if not cell:
                continue
            # Domains column contains comma-separated values like "spp.se, storebrand.no"
            for raw_domain in cell.split(","):
                d = normalize_domain(raw_domain)
                if d:
                    domains.add(d)

    return sorted(domains)


def load_domains_from_text(path: str) -> list[str]:
    """Load domains from a plain text file (one per line). Falls back for non-CSV inputs."""
    domains: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            d = normalize_domain(line)
            if d:
                domains.add(d)
    return sorted(domains)


def load_domains(path: str) -> list[str]:
    """Auto-detect input format: .csv → semicolon-delimited CSV, otherwise plain text."""
    if path.lower().endswith(".csv"):
        return load_domains_from_csv(path)
    return load_domains_from_text(path)


def is_subdomain(host: str, root: str) -> bool:
    """Check if host is a subdomain of root (including the root itself)."""
    host = host.lower().rstrip(".")
    root = root.lower().rstrip(".")
    if host == root:
        return True
    return host.endswith("." + root)


def extract_hosts(result: dict) -> set[str]:
    hosts = set()

    # Pro API (datasource=hostnames)
    hostname = result.get("hostname")
    if isinstance(hostname, str):
        hosts.add(hostname.lower().rstrip("."))

    # Standard Search API (fallback)
    page = result.get("page") or {}
    task = result.get("task") or {}

    for key in ("domain",):
        val = page.get(key)
        if isinstance(val, str):
            hosts.add(val.lower().rstrip("."))

    for key in ("domain",):
        val = task.get(key)
        if isinstance(val, str):
            hosts.add(val.lower().rstrip("."))

    for key in ("url",):
        val = page.get(key)
        if isinstance(val, str):
            h = urlparse(val).hostname
            if h:
                hosts.add(h.lower().rstrip("."))

    for key in ("url",):
        val = task.get(key)
        if isinstance(val, str):
            h = urlparse(val).hostname
            if h:
                hosts.add(h.lower().rstrip("."))

    return hosts


def query_domain(
    session: requests.Session,
    api_key: str,
    root: str,
    size: int,
    max_pages: int | None,
    sleep_s: float,
) -> set[str]:
    q = f'hostname:*.{root}'

    headers = {"API-Key": api_key}
    params = {"q": q, "size": size, "datasource": "hostnames"}
    subdomains = set()

    pages = 0
    search_after = None

    while True:
        if search_after:
            params["search_after"] = search_after

        resp = session.get(API_URL, headers=headers, params=params, timeout=60)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "5"))
            print(f"  Rate limited, retrying in {retry_after}s...", file=sys.stderr)
            time.sleep(retry_after)
            continue
        resp.raise_for_status()

        data = resp.json()
        results = data.get("results", [])
        if not results:
            break

        for r in results:
            for host in extract_hosts(r):
                if host.startswith("*."):
                    continue
                if is_subdomain(host, root):
                    subdomains.add(host)

        last_sort = results[-1].get("sort")
        if not last_sort:
            break
        if isinstance(last_sort, list):
            search_after = ",".join(str(x) for x in last_sort)
        else:
            search_after = str(last_sort)

        pages += 1
        if max_pages and pages >= max_pages:
            break

        if sleep_s > 0:
            time.sleep(sleep_s)

    return subdomains


def save_subdomains(output_dir: str, root: str, subdomains: set[str]) -> str:
    """Save subdomains for a single apex domain to <output_dir>/<root>.txt. Returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{root}.txt")
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        for sub in sorted(subdomains):
            f.write(sub + "\n")
    return filepath


def _run_baddns_single(
    subdomain: str, 
    log_dir: str, 
    modules: list[str], 
    nameserver: str | None, 
    extra_args: list[str],
    debug: bool = False
) -> tuple[str, bool, str]:
    """Run baddns for a single subdomain. Returns (subdomain, success, message)."""
    # Construct command: baddns -s -m <modules> [-n <nameserver>] <subdomain>
    cmd = ["baddns", "-s"]
    
    if modules:
        # Assuming standard usage: -m Mod1,Mod2
        cmd.extend(["-m", ",".join(modules)])
    
    if nameserver:
        cmd.extend(["-n", nameserver])
        
    cmd.extend(extra_args)
    
    # Target is positional, usually last
    cmd.append(subdomain)

    if debug:
        print(f"DEBUG: Executing: {' '.join(cmd)}", flush=True)

    try:
        # Capture output instead of writing to file
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout.strip()
        # Combine stdout and stderr if needed, or just stdout as baddns -s prints findings there
        if result.stderr:
             # If significant stderr exists, maybe append? baddns usually keeps findings in stdout
             pass
        return (subdomain, result.returncode == 0, output)
    except FileNotFoundError:
        return (subdomain, False, "baddns command not found")
    except subprocess.TimeoutExpired:
        return (subdomain, False, "timeout after 300s")
    except Exception as e:
        return (subdomain, False, str(e))


def run_baddns_batch(
    output_dir: str | None = None,
    files: list[str] | None = None,
    skip_combined: bool = True,
    modules: str = "NS",
    nameserver: str | None = "1.1.1.1",
    jobs: int = 10,
    raw_args: str = "",
    debug: bool = False
):
    """Run baddns against specified files or all .txt files in output_dir."""
    
    # Parse modules and extra args
    mod_list = [m.strip() for m in modules.split(",") if m.strip()]
    extra_args = [a for a in raw_args.split() if a.strip()]

    target_files = []
    if files:
        target_files = files
    elif output_dir:
        # Collect all subdomains from per-domain files in output_dir
        pattern = os.path.join(output_dir, "*.txt")
        target_files = sorted(glob.glob(pattern))
    if not target_files:
        print("No subdomain files found/provided, skipping BadDNS scan.", file=sys.stderr)
        return

    # Create timestamped log directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_dir_name = f"baddns_results_{timestamp}"
    
    # Use output_dir specific logic for log placement?
    # User said "Logs from baddns in the current directory with timestamp".
    # Assuming "current directory" means CWD, or relative to script execution.
    log_dir = os.path.abspath(log_dir_name)
    os.makedirs(log_dir, exist_ok=True)

    # Infer output_dir if not provided, for log storage (logs go to new timestamped dir anyway, but target_files logic used output_dir)
    if not output_dir and target_files:
        output_dir = os.path.dirname(target_files[0]) or "."
    if not output_dir:
        output_dir = "."

    # Exclude combined file if requested
    if skip_combined:
        target_files = [f for f in target_files if os.path.basename(f) != "all_subdomains.txt"]

    if not target_files:
        print("No valid target files after filtering.", file=sys.stderr)
        return

    # Prepare tasks: list of (subdomain, log_file_path)
    # We want to write logs to "apex domain". Assuming input file "domain.txt" corresponds to apex.
    # Log file will be "domain.baddns.log"
    
    tasks = []
    
    # Initialize/Clear log files first
    unique_log_files = set()
    log_file_counts = {}
    
    for filepath in target_files:
        if not os.path.isfile(filepath):
            continue
        
        # Determine log file path: <log_dir>/<filepath_no_ext>.baddns.log
        base = os.path.splitext(os.path.basename(filepath))[0]
        log_file = os.path.join(log_dir, f"{base}.baddns.log")
        unique_log_files.add(log_file)
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                sub = line.strip()
                if sub and not sub.startswith("*."):
                    tasks.append((sub, log_file))

    # Clear logs
    for lf in unique_log_files:
        with open(lf, "w", encoding="utf-8") as f:
            pass

    if not tasks:
        print("No subdomains to scan.", file=sys.stderr)
        return

    print(f"\n{'=' * 50}")
    print("Running BadDNS batch scan")
    print(f"{'=' * 50}")
    print(f"Targets:     {len(tasks)} tasks (from {len(target_files)} source files)")
    print(f"Concurrency: {jobs} jobs")
    print(f"Modules:     {', '.join(mod_list)}")
    print(f"Nameserver:  {nameserver or 'default'}")
    if extra_args:
        print(f"Extra Args:  {' '.join(extra_args)}")
    print(f"Logs:        {log_dir}")
    
    # Show example command
    example_cmd = ["baddns", "-s"]
    if mod_list:
        example_cmd.extend(["-m", ",".join(mod_list)])
    if nameserver:
        example_cmd.extend(["-n", nameserver])
    example_cmd.append(tasks[0][0]) # first subdomain
    print(f"Example Cmd: {' '.join(example_cmd)} ...")
    print(f"{'=' * 50}\n")

    completed = 0
    failed = 0
    total = len(tasks)

    # Use ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        # Map future to (subdomain, log_file)
        futures = {
            pool.submit(_run_baddns_single, sub, "", mod_list, nameserver, extra_args, debug): (sub, lf) 
            for (sub, lf) in tasks
        }
        
        for future in concurrent.futures.as_completed(futures):
            sub, log_path = futures[future]
            try:
                # result is (subdomain, success, output)
                _, success, output = future.result()
                
                # If output is non-empty, write to log
                if output and output.strip():
                     with open(log_path, "a", encoding="utf-8") as f:
                         f.write(output.strip() + "\n")
                     msg = "Found results"
                     log_file_counts[log_path] = log_file_counts.get(log_path, 0) + 1
                else:
                     msg = "No results"

                completed += 1
                status = "OK" if success else "FAIL"
                if not success:
                    failed += 1
                    msg = output # Error message usually in output/str(e)
                
                print(f"  [{completed}/{total}] {status}: {sub} → {msg}")
            except Exception as e:
                print(f"  ERROR processing {sub}: {e}")

    print(f"\n{'=' * 50}")
    print(f" BadDNS complete: {completed - failed}/{total} succeeded")
    print(f" Logs written to: {log_dir}")
    
    if log_file_counts:
        print("\n Vulnerabilities found per file:")
        for lf, count in sorted(log_file_counts.items()):
            print(f"  - {os.path.basename(lf)}: {count} record(s)")
    else:
        print(" No vulnerabilities found.")

    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch unique subdomains per root domain via pro.urlscan.io, then run BadDNS.\n"
                    "In normal mode, BadDNS runs only against domains found in the current session.\n"
                    "In --baddns-only mode, use -i/--input to specify file(s) or directory to scan.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # URLScan group
    scan_grp = parser.add_argument_group("URLScan Options")
    scan_grp.add_argument("-i", "--input", help="Input file (CSV/text). For --baddns-only: file, glob pattern, or directory.")
    scan_grp.add_argument("-o", "--output-dir", default="./subdomain_results", help="Output directory")
    scan_grp.add_argument("--api-key", help="urlscan.io API key (or set URLSCAN_API_KEY)")
    scan_grp.add_argument("--size", type=int, default=10000, help="Results per page (default: 10000)")
    scan_grp.add_argument("--max-pages", type=int, help="Limit number of pages per domain")
    scan_grp.add_argument("--sleep", type=float, default=0.2, help="Sleep between requests (seconds)")
    scan_grp.add_argument("--debug", action="store_true", help="Enable debug logging (show all commands)")

    # BadDNS group
    bad_grp = parser.add_argument_group("BadDNS Options")
    bad_grp.add_argument("--skip-baddns", action="store_true", help="Skip BadDNS scan (default: run on new results)")
    bad_grp.add_argument("--baddns-only", action="store_true", help="Skip urlscan discovery, run BadDNS on input files defined by -i")
    bad_grp.add_argument("--baddns-modules", default="NS", help="Comma-separated modules (default: NS)")
    bad_grp.add_argument("--baddns-ip", default="1.1.1.1", help="Custom nameserver IP (default: 1.1.1.1)")
    bad_grp.add_argument("--baddns-jobs", type=int, default=10, help="Concurrency (default: 10)")
    bad_grp.add_argument("--baddns-args", default="", help="Extra raw arguments for baddns")

    args = parser.parse_args()

    # --baddns-only logic
    if args.baddns_only:
        targets = []
        if args.input:
            # Check if input is a directory or file/glob
            if os.path.isdir(args.input):
                pattern = os.path.join(args.input, "*.txt")
                targets = sorted(glob.glob(pattern))
            else:
                # Assume it's a file pattern or single file
                targets = sorted(glob.glob(args.input))
                if not targets and os.path.isfile(args.input):
                    targets = [args.input]
        else:
            # Default to output dir
            if os.path.isdir(args.output_dir):
                pattern = os.path.join(args.output_dir, "*.txt")
                targets = sorted(glob.glob(pattern))
        
        if not targets:
            print(f"Error: No target files found for --baddns-only (input: {args.input or args.output_dir}).", file=sys.stderr)
            sys.exit(1)
            
        run_baddns_batch(
            output_dir=args.output_dir if os.path.isdir(args.output_dir) else os.path.dirname(targets[0]),
            files=targets,
            skip_combined=True,
            modules=args.baddns_modules,
            nameserver=args.baddns_ip,
            jobs=args.baddns_jobs,
            raw_args=args.baddns_args,
            debug=args.debug
        )
        return

    # Normal mode: URLScan + optional BadDNS
    if not args.input:
        parser.error("the following arguments are required: -i/--input")

    api_key = args.api_key or os.getenv("URLSCAN_API_KEY")
    if not api_key:
        print("Missing API key. Use --api-key or set URLSCAN_API_KEY.", file=sys.stderr)
        sys.exit(1)

    roots = load_domains(args.input)
    if not roots:
        print("No domains found in input.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(roots)} unique domains from {args.input}")
    print(f"Output directory: {args.output_dir}")
    print()

    session = requests.Session()
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    all_subdomains: set[str] = set()
    generated_files: list[str] = []
    total = len(roots)

    for idx, root in enumerate(roots, 1):
        print(f"[{idx}/{total}] Querying: {root} ...", end=" ", flush=True)
        try:
            subs = query_domain(
                session=session,
                api_key=api_key,
                root=root,
                size=args.size,
                max_pages=args.max_pages,
                sleep_s=args.sleep,
            )
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            continue

        print(f"found {len(subs)} subdomain(s)")

        if subs:
            filepath = save_subdomains(output_dir, root, subs)
            print(f"  → Saved to {filepath}")
            all_subdomains.update(subs)
            generated_files.append(filepath)

    if all_subdomains:
        combined_path = os.path.join(output_dir, "all_subdomains.txt")
        with open(combined_path, "w", encoding="utf-8", newline="") as f:
            for sub in sorted(all_subdomains):
                f.write(sub + "\n")
        print(f"\nTotal unique subdomains: {len(all_subdomains)}")
        print(f"Combined file: {combined_path}")
    else:
        print("\nNo subdomains found across any domain.")

    if not args.skip_baddns and generated_files:
        run_baddns_batch(
            output_dir=output_dir,
            files=generated_files,
            skip_combined=True,
            modules=args.baddns_modules,
            nameserver=args.baddns_ip,
            jobs=args.baddns_jobs,
            raw_args=args.baddns_args,
            debug=args.debug
        )


if __name__ == "__main__":
    main()
