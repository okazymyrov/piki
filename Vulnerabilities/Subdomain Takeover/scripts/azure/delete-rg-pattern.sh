#!/bin/bash

# -------- Parameters --------
PATTERN="dns-test"          # Resources starting with this pattern will be deleted
EXCLUDE_NAME="dns-test-2" # This specific resource will NOT be deleted
SUBSCRIPTION_ID="e09d32ee-ae58-41e9-8209-b3c44ed3b095"          # Optional – leave empty to use current subscription
# ----------------------------

echo "🔍 Searching for resource groups starting with '$PATTERN' (excluding '$EXCLUDE_NAME')..."

# Optionally set subscription
if [ -n "$SUBSCRIPTION_ID" ]; then
  az account set --subscription "$SUBSCRIPTION_ID"
fi

# Get matching resource group names
groups=$(az group list \
  --query "[?starts_with(name, '${PATTERN}') && name!='${EXCLUDE_NAME}'].name" \
  -o tsv)

if [ -z "$groups" ]; then
  echo "✔ No resource groups found matching the criteria."
  exit 0
fi

echo "⚠ The following resource groups will be DELETED:"
echo
for g in $groups; do
  echo " - $g"
done
echo

read -p "Are you sure you want to delete these resource groups? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Operation cancelled."
  exit 0
fi

# Delete each resource group
for g in $groups; do
  echo "🗑 Deleting resource group: $g ..."
  az group delete --name "$g" --yes --no-wait
done

echo "✅ Delete operations submitted (running asynchronously)."
