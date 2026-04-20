echo -e "\n=== DNS Zones and their NS Servers ===\n"

# List all DNS zones
az network dns zone list -o json | jq -c '.[]' | while read -r zone; do
    name=$(echo "$zone" | jq -r '.name')
    rg=$(echo "$zone" | jq -r '.resourceGroup')

    echo "Zone: $name (Resource Group: $rg)"

    # Fetch NS record set JSON
    ns_json=$(az network dns record-set ns show \
        --zone-name "$name" \
        --resource-group "$rg" \
        --name "@" \
        -o json)

    # Extract NS records (handle NSRecords or nsRecords)
    echo "$ns_json" | jq -r '
        (.NSRecords // .nsRecords // [])[]?.nsdname
    '

    echo ""
done
