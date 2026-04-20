#!/usr/bin/env bash

#############################################
#   DESCRIPTION
#############################################
# Batch orchestrator for baddns scanning.
# Runs scan-baddns.sh for multiple subdomain files in parallel.
#
# DEPENDENCY: Requires scan-baddns.sh in the same directory

#############################################
#   CONFIG
#############################################
NS_FLAG=""
MAX_JOBS="2"
SCAN_PATTERN="${BADDNS_SCAN_PATTERN:-$HOME/.bbot/scans/*/subdomains.txt}"
WORKER_SCRIPT="./scan-baddns.sh"
LOG_DIR="./baddns_logs"

#############################################
#   USAGE
#############################################
usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Batch process multiple subdomain files using scan-baddns.sh in parallel.

OPTIONS:
    -ns, --nameserver       Pass -ns flag to scan-baddns.sh (enable NS module)
    -p, --pattern PATTERN   Scan pattern (default: ~/.bbot/scans/*/subdomains.txt)
    -j, --jobs N            Concurrency limit (default: 2)
    -o, --output-dir DIR    Output directory (default: ./baddns_logs)
    -h, --help              Show this help message

EXAMPLES:
    $0                                      # Process with default settings
    $0 -j 4                                 # Run 4 concurrent jobs
    $0 --nameserver --jobs 4                # Run 4 jobs with NS module
    $0 -p "~/scans/*/domains.txt" -j 5      # Custom pattern

ENVIRONMENT:
    BADDNS_SCAN_PATTERN    Default scan pattern (overridden by -p)

OUTPUTS:
    ./baddns_logs/<domain>.log     Per-domain log files

EOF
    exit 0
}

#############################################
#   ARGUMENT PARSING
#############################################
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -ns|--nameserver)
            NS_FLAG="--nameserver"
            shift
            ;;
        -p|--pattern)
            if [[ -z "$2" ]]; then
                echo "Error: -p requires a pattern argument"
                exit 1
            fi
            SCAN_PATTERN="$2"
            shift 2
            ;;
        -j|--jobs)
            if [[ -z "$2" || ! "$2" =~ ^[0-9]+$ ]]; then
                echo "Error: -j requires a numeric argument"
                exit 1
            fi
            MAX_JOBS="$2"
            shift 2
            ;;
        -o|--output-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown option: $1"
            echo "Run '$0 --help' for usage information."
            exit 1
            ;;
    esac
done

#############################################
#   VALIDATION
#############################################
# Check if worker script exists
if [[ ! -f "$WORKER_SCRIPT" ]]; then
    echo "Error: Required script '$WORKER_SCRIPT' not found in current directory."
    echo "This script depends on scan-baddns.sh to process individual subdomain files."
    exit 1
fi

# Make worker script executable if it isn't
if [[ ! -x "$WORKER_SCRIPT" ]]; then
    echo "Warning: Making $WORKER_SCRIPT executable..."
    chmod +x "$WORKER_SCRIPT"
fi

# Expand tilde in scan pattern
SCAN_PATTERN="${SCAN_PATTERN/#\~/$HOME}"

# Create log directory
mkdir -p "$LOG_DIR"

#############################################
#   COLLECT FILES
#############################################
# Use glob expansion for pattern matching
shopt -s nullglob
FILES=($SCAN_PATTERN)
shopt -u nullglob

# Check if we found any files
if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Error: No files found matching pattern: $SCAN_PATTERN"
    echo "Make sure the scan directory exists and contains subdomain files."
    exit 1
fi

# Sort files so the order is stable and predictable
IFS=$'\n' FILES=($(sort <<<"${FILES[*]}"))
unset IFS

TOTAL=${#FILES[@]}
COUNT=0

echo "=========================================="
echo "Batch baddns runner"
echo "=========================================="
echo "Scan pattern: $SCAN_PATTERN"
echo "Found files:  $TOTAL"
echo "Concurrency:  $MAX_JOBS jobs"
echo "NS module:    ${NS_FLAG:-disabled}"
echo "Output dir:   $LOG_DIR"
echo "=========================================="
echo

#############################################
#   JOB CONTROL
#############################################
PIDS=()

count_jobs() {
    local alive=0
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            ((alive++))
        fi
    done
    echo "$alive"
}

run_job() {
    local file="$1"
    local num="$2"
    local domain
    domain=$(basename "$(dirname "$file")")
    local log_file="$LOG_DIR/${domain}.log"

    echo "[$num/$TOTAL] Starting: $domain"
    echo "    → Log: $log_file"

    nohup "$WORKER_SCRIPT" "$file" $NS_FLAG >"$log_file" 2>&1 &
    PIDS+=($!)
}

#############################################
#   MAIN LOOP
#############################################
for file in "${FILES[@]}"; do

    # Enforce concurrency limit
    while [[ "$(count_jobs)" -ge "$MAX_JOBS" ]]; do
        echo -ne "Waiting… $(count_jobs) jobs running…\r"
        sleep 2
    done

    ((COUNT++))
    run_job "$file" "$COUNT"
    sleep 0.5

done

echo
echo "All jobs started. Waiting for them to finish…"

#############################################
#   WAIT FOR ALL JOBS TO FINISH
#############################################
while [[ "$(count_jobs)" -gt 0 ]]; do
    echo -ne "Still running: $(count_jobs) jobs…\r"
    sleep 3
done

echo
echo "======================================"
echo " All baddns jobs completed!"
echo " Logs saved in: $LOG_DIR"
echo "======================================"
