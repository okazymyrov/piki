#!/bin/bash

#############################################
#   USAGE
#############################################
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [INPUT_FILE]

Run baddns for each subdomain in the input file.

OPTIONS:
    -ns, --nameserver       Enable NS module (adds -m NS to baddns)
    -h, --help              Show this help message

ARGUMENTS:
    INPUT_FILE              File containing subdomains (default: ./subdomains.txt)

EXAMPLES:
    $0                          # Use default ./subdomains.txt
    $0 domains.txt              # Process domains.txt
    $0 -ns domains.txt          # Process with NS module
    $0 --nameserver domains.txt # Process with NS module (long option)

EOF
    exit 0
}

#############################################
#   OPTIONS & CONFIGURATION
#############################################
baddns_args=""
input_file=""

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -ns|--nameserver)
            baddns_args="$baddns_args -m NS"
            shift
            ;;
        -n|--nameserver-ip)
            if [[ -z "$2" ]]; then
                echo "Error: -n requires an IP argument"
                exit 1
            fi
            baddns_args="$baddns_args -n $2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Error: Unknown option: $1"
            echo "Run '$0 -h' for usage information."
            exit 1
            ;;
        *)
            # Positional argument - input file
            if [[ -z "$input_file" ]]; then
                input_file="$1"
            else
                echo "Error: Multiple input files specified: '$input_file' and '$1'"
                exit 1
            fi
            shift
            ;;
    esac
done

# Set default input file if not specified
input_file="${input_file:-./subdomains.txt}"

#############################################
#   VALIDATION
#############################################
# Check if file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

#############################################
#   MAIN PROCESSING
#############################################
while read -r line; do
    # Extract the first column
    subdomain=$(echo "$line" | awk '{print $1}')

    # Skip empty lines
    [[ -z "$subdomain" ]] && continue

    echo "Running: baddns -s $subdomain $baddns_args"
    baddns -s "$subdomain" $baddns_args
done < "$input_file"
