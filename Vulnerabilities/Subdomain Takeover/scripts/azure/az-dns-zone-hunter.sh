#!/usr/bin/env bash
set -euo pipefail

# Run with
# echo "" > ./az-dns-zone-hunter.sh && nano ./az-dns-zone-hunter.sh && chmod +x ./az-dns-zone-hunter.sh && ./az-dns-zone-hunter.sh -z [zone] -ns [ns1-09.azure-dns.com] -p [dns-ns-test] -s "e09d32ee-ae58-41e9-8209-b3c44ed3b095"

##############################################
# COLORS
##############################################
GREEN="\e[32m"
YELLOW="\e[33m"
RED="\e[31m"
CYAN="\e[36m"
BOLD="\e[1m"
NC="\e[0m"

log()  { echo -e "${GREEN}[+]${NC} $*" >&2; }
warn() { echo -e "${YELLOW}[!]${NC} $*" >&2; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

##############################################
# MODIFIABLE CONFIGURATION
# These can be changed here OR via command-line options
##############################################

# Required (must be provided via CLI if not set here)
ZONE=""                         # DNS zone name to create
NEEDLE_NS="ns1-01.azure-dns.com"                    # Target nameserver to match

# Azure Settings
SUBSCRIPTION_ID=""              # Azure subscription ID (empty = use current)

# Resource Group Settings
RG_PREFIX="dns-st"              # Prefix for resource group names

# Failure Handling
MAX_CONSECUTIVE_FAILURES=3      # Stop after N consecutive DNS zone failures

# Behavior Flags
DRY_RUN=false                   # Show commands without executing
CLEANUP_ON_FAILURE=true         # Auto-cleanup resources on failure
CLEAN_ONLY=false                # Cleanup mode (delete existing RGs and exit)

##############################################
# RUNTIME VARIABLES (do not modify)
##############################################
MATCH_FOUND=false
ZONES_CREATED=0
RGS_CREATED=0

usage() {
cat <<EOF
Usage: $0 -z <zone> -ns <nameserver> [OPTIONS]

Required:
  -z <zone>        DNS zone name to create
  -ns <nameserver> Target nameserver to match (FQDN)

Optional:
  -s <sub-id>      Azure subscription ID
  -p <prefix>      Resource group prefix (default: $RG_PREFIX)
  -f <number>      Max consecutive DNS failures before stop (default: $MAX_CONSECUTIVE_FAILURES)
  
  -c               Cleanup mode (delete RGs with prefix and exit)
  -d, --dry-run    Dry-run mode (show commands without executing)
  --no-cleanup     Don't cleanup resources on failure
  
  -h, --help       Show this help message

Examples:
  $0 -z example.com -ns ns1-01.azure-dns.com
  $0 -z example.com -ns ns1-01.azure-dns.com -p my-rg -f 5
  $0 -z example.com -ns ns1-01.azure-dns.com -s 12345678-1234-1234-1234-123456789abc
  $0 -c -p dns-st  # Cleanup mode
EOF
}

normalize_ns() { sed 's/\.$//'; }

##############################################
# AZURE CLI WRAPPER FOR DRY-RUN
##############################################
az_cmd() {
    if [[ "$DRY_RUN" == true ]]; then
        log "[DRY-RUN] Would execute: az $*"
        return 0
    else
        az "$@"
    fi
}

##############################################
# CLEANUP ON EXIT
##############################################
cleanup_on_exit() {
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]] && [[ "$CLEANUP_ON_FAILURE" == true ]] && [[ "$CLEAN_ONLY" != true ]]; then
        warn "Script failed with exit code $exit_code. Cleaning up resources..."
        
        # Get list of RGs to delete
        local groups
        groups=$(az group list --query "[?starts_with(name, '$RG_PREFIX')].name" -o tsv 2>/dev/null || true)
        
        if [[ -n "$groups" ]]; then
            declare -A DEL_PIDS
            
            for g in $groups; do
                warn "Initiating delete for RG: $g"
                (
                    az group delete --yes --no-wait -n "$g" >/dev/null 2>&1 || true
                    while az group show -n "$g" >/dev/null 2>&1; do
                        sleep 5
                    done
                ) &
                DEL_PIDS["$g"]=$!
            done
            
            for g in "${!DEL_PIDS[@]}"; do
                wait "${DEL_PIDS[$g]}" 2>/dev/null || true
                log "Deleted: $g"
            done
        fi
    fi
    
    # Print summary statistics
    if [[ "$CLEAN_ONLY" != true ]]; then
        local end_time=$(date +%s)
        local duration=$((end_time - START_TIME))
        
        echo "" >&2
        log "═══════════════════════════════════════"
        log "Summary Statistics"
        log "═══════════════════════════════════════"
        log "  Duration: ${duration}s"
        log "  Resource Groups Created: $RGS_CREATED"
        log "  DNS Zones Created: $ZONES_CREATED"
        log "  Match Found: $([ "$MATCH_FOUND" == true ] && echo "Yes" || echo "No")"
        log "═══════════════════════════════════════"
    fi
}

trap cleanup_on_exit EXIT

##############################################
# ARGUMENT PARSING
# Command-line options override configuration defaults
##############################################
while [[ $# -gt 0 ]]; do
    case "$1" in
        -z)  ZONE="$2"; shift 2 ;;
        -ns|--ns) NEEDLE_NS="$2"; shift 2 ;;
        -s|--subscription) SUBSCRIPTION_ID="$2"; shift 2 ;;
        -p|--prefix) RG_PREFIX="$2"; shift 2 ;;
        -f|--failures) MAX_CONSECUTIVE_FAILURES="$2"; shift 2 ;;
        -c|--cleanup) CLEAN_ONLY=true; shift ;;
        -d|--dry-run) DRY_RUN=true; shift ;;
        --no-cleanup) CLEANUP_ON_FAILURE=false; shift ;;
        -h|--help) usage; exit 0 ;;
        *) err "Unknown option $1"; usage; exit 1 ;;
    esac
done

##############################################
# PRE-FLIGHT CHECKS
##############################################
log "Running pre-flight checks..."

# Check for Azure CLI
if ! command -v az &> /dev/null; then
    err "Azure CLI (az) not found. Please install it first."
    err "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Verify Azure login status
if ! az account show &>/dev/null; then
    err "Not logged into Azure. Run 'az login' first."
    exit 1
fi

# Check for required utilities
if ! command -v shuf &> /dev/null; then
    warn "shuf not found. Location randomization will be limited."
fi

log "Pre-flight checks passed ✓"

# Set subscription if specified
if [[ -n "$SUBSCRIPTION_ID" ]]; then
    log "Setting Azure subscription to: $SUBSCRIPTION_ID"
    if ! az account set --subscription "$SUBSCRIPTION_ID" &>/dev/null; then
        err "Failed to set subscription to '$SUBSCRIPTION_ID'"
        err "Run 'az account list' to see available subscriptions"
        exit 1
    fi
    log "Subscription set successfully"
fi

##############################################
# CLEANUP MODE (ASYNC DELETE + WAIT)
##############################################
if [[ "$CLEAN_ONLY" == true ]]; then
    warn "Cleanup mode enabled — deleting RGs with prefix '$RG_PREFIX'"

    groups=$(az group list --query "[?starts_with(name, '$RG_PREFIX')].name" -o tsv)

    if [[ -z "$groups" ]]; then
        warn "No RGs found to delete."
        exit 0
    fi

    declare -A DEL_PIDS

    for g in $groups; do
        warn "Initiating delete for RG: $g"
        (
            az group delete --yes --no-wait -n "$g" >/dev/null 2>&1 || true
            # Poll until the group is actually gone
            while az group show -n "$g" >/dev/null 2>&1; do
                sleep 5
            done
        ) &
        DEL_PIDS["$g"]=$!
    done

    log "Waiting for RG deletion to finish…"
    for g in "${!DEL_PIDS[@]}"; do
        wait "${DEL_PIDS[$g]}"
        log "Deleted: $g"
    done

    log "Cleanup complete."
    exit 0
fi

##############################################
# VALIDATION
##############################################
if [[ -z "$ZONE" || -z "$NEEDLE_NS" ]]; then
    usage
    exit 1
fi

NEEDLE_NS=$(echo "$NEEDLE_NS" | normalize_ns)

# Start timing
START_TIME=$(date +%s)

##############################################
# BUILD LOCATION LIST
##############################################
log "Fetching locations that support resource groups in your subscription…"

FILTERED_LOCS=()

# Try resource provider query (most accurate)
while IFS= read -r loc; do
    [[ -z "$loc" ]] && continue
    if [[ "$loc" == *"stage"* ]] || [[ "$loc" == *"euap"* ]]; then
        continue
    fi
    FILTERED_LOCS+=("$loc")
done < <(az provider show --namespace Microsoft.Resources \
    --query "resourceTypes[?resourceType=='resourceGroups'].locations[]" \
    -o tsv 2>/dev/null | awk '{print tolower($0)}' | sed 's/ //g' | sort -u)

# Fallback to list-locations
if [[ ${#FILTERED_LOCS[@]} -eq 0 ]]; then
    warn "Provider query returned no results, falling back to list-locations"
    while IFS= read -r loc; do
        [[ -z "$loc" ]] && continue
        if [[ "$loc" == *"stage"* ]] || [[ "$loc" == *"euap"* ]] || \
           [[ "$loc" == *"china"* ]] || [[ "$loc" == *"gov"* ]] || \
           [[ "$loc" =~ ^(brazil|uae|india|korea|canada|australia|japan|uk|france|switzerland|norway|sweden)$ ]]; then
            continue
        fi
        FILTERED_LOCS+=("$loc")
    done < <(az account list-locations --query "[].name" -o tsv 2>/dev/null | awk '{print tolower($0)}' | sort -u)
fi

if [[ ${#FILTERED_LOCS[@]} -eq 0 ]]; then
    err "No locations available for resource group creation"
    exit 1
fi

# Shuffle locations for randomization
if command -v shuf &> /dev/null; then
    LOCATIONS=( $(printf "%s\n" "${FILTERED_LOCS[@]}" | shuf) )
else
    LOCATIONS=("${FILTERED_LOCS[@]}")
fi

LOCATION_COUNT=${#LOCATIONS[@]}
NEXT_LOC_INDEX=0

log "Found ${#FILTERED_LOCS[@]} usable locations"
log "Sample locations: ${LOCATIONS[@]:0:5}"

##############################################
# SEQUENTIAL RG + DNS ZONE CREATION
# Create RG → Create DNS Zone → Check → Repeat
# Stop on: match found OR 3 consecutive DNS failures
##############################################
log "Starting sequential RG and DNS zone creation…"

rg_counter=0
consecutive_failures=0

while true; do
    # Get next location
    if (( NEXT_LOC_INDEX >= LOCATION_COUNT )); then
        NEXT_LOC_INDEX=0  # Wrap around
    fi
    location="${LOCATIONS[$NEXT_LOC_INDEX]}"
    NEXT_LOC_INDEX=$((NEXT_LOC_INDEX + 1))
    
    # Generate RG name
    rg_name="${RG_PREFIX}-${rg_counter}"
    rg_counter=$((rg_counter + 1))
    
    # Create Resource Group with error capture
    log "Creating resource group '$rg_name' in location '$location'"
    error_output=$(mktemp)
    if ! az_cmd group create -n "$rg_name" -l "$location" >/dev/null 2>"$error_output"; then
        error_msg=$(cat "$error_output" 2>/dev/null | head -n 3)
        rm -f "$error_output"
        warn "Failed to create RG '$rg_name' in '$location'"
        if [[ -n "$error_msg" ]]; then
            warn "Error: $error_msg"
        fi
        continue
    fi
    rm -f "$error_output"
    
    RGS_CREATED=$((RGS_CREATED + 1))
    log "RG created successfully: $rg_name"
    
    # Create DNS Zone immediately with error capture
    log "Creating DNS zone '$ZONE' in '$rg_name'"
    error_output=$(mktemp)
    if ! az_cmd network dns zone create -g "$rg_name" -n "$ZONE" >/dev/null 2>"$error_output"; then
        error_msg=$(cat "$error_output" 2>/dev/null)
        rm -f "$error_output"
        
        # Check for fatal "zone not available" error
        if echo "$error_msg" | grep -qi "zone.*is not available"; then
            err "FATAL: DNS zone '$ZONE' is not available (already taken by another subscription)"
            err "This zone name cannot be used. Please try a different zone name."
            exit 1
        fi
        
        # Display error (first 3 lines)
        error_summary=$(echo "$error_msg" | head -n 3)
        warn "Failed to create DNS zone in $rg_name"
        if [[ -n "$error_summary" ]]; then
            warn "Error: $error_summary"
        fi
        consecutive_failures=$((consecutive_failures + 1))
        
        if (( consecutive_failures >= MAX_CONSECUTIVE_FAILURES )); then
            err "Stopped after $MAX_CONSECUTIVE_FAILURES consecutive DNS zone creation failures"
            exit 1
        fi
        
        continue
    fi
    rm -f "$error_output"
    
    # Reset failure counter on success
    consecutive_failures=0
    ZONES_CREATED=$((ZONES_CREATED + 1))
    
    # Get nameservers
    raw_ns=$(az network dns zone show -g "$rg_name" -n "$ZONE" --query "nameServers" -o tsv 2>/dev/null)
    clean_ns=$(echo "$raw_ns" | normalize_ns)
    
    echo -e "${CYAN}Name servers for '$rg_name':${NC}"
    echo "$clean_ns" | sed 's/^/  /'
    
    # Check for match
    if echo "$clean_ns" | grep -Fxq "$NEEDLE_NS"; then
        echo -e "${GREEN}${BOLD}MATCH FOUND!${NC}"
        echo -e "${GREEN}NS '${NEEDLE_NS}' found in RG '${BOLD}$rg_name${NC}'"
        
        MATCH_FOUND=true
        CLEANUP_ON_FAILURE=false
        exit 0
    fi
    
    log "No match, continuing to next RG..."
done
