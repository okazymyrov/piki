# Azure DNS: Dangling NS Delegation Leading to Subdomain Takeover

## Answer from Microsoft (VULN-167964 / MSRC Case 104484 CRM:0022115875)

> After careful investigation, this case has been assessed as **moderate severity** and does not meet Microsoft's bar for immediate servicing. However, we have shared the report with the team responsible for maintaining the product or service. They will take appropriate action as needed to help **keep customers protected**.

## Timeline

| Date       | Status |
|------------|--------|
| 2025-12-10 | Report created (VULN-167964) |
| 2025-12-11 | MSRC case opened (MSRC Case 104484) |
| 2026-02-09 | Requested update |
| 2026-02-17 | MSRC response: moderate severity; below servicing bar; case closed |
| 2026-02-17 | Complete |

## Azure DNS Specifics

### Name Server Assignment

Azure DNS assigns every public managed zone to a set of **four name servers**, one from each of the four top-level domains:

- `ns1-XX.azure-dns.com`
- `ns2-XX.azure-dns.net`
- `ns3-XX.azure-dns.org`
- `ns4-XX.azure-dns.info`

Where `XX` is a number assigned from a pool. The same zone name can be reused in a different resource group or a different Azure subscription, and each instance is assigned different name server addresses.

Unlike Google Cloud DNS which has only 5 fixed shards, Azure DNS draws from a larger pool of name server sets. During testing, only servers numbered **01 to 09** were observed being assigned. Each zone creation requires a **new resource group** and takes some time to provision, making manual brute-force attempts impractical.

### Takeover Procedure

1. **Identify the dangling NS delegation.** Determine which Azure DNS name server set the target subdomain's NS records reference (e.g., `ns1-09.azure-dns.com`, `ns2-09.azure-dns.net`, `ns3-09.azure-dns.org`, `ns4-09.azure-dns.info`).

2. **Create a public DNS zone** in Azure DNS for the target subdomain in a new resource group.

3. **Check the assigned name servers.** If the zone is assigned a different name server set than the dangling delegation, create another zone in a new resource group. Repeat until the correct set is assigned or an error indicates the zone name is already taken.

4. **Confirm authoritative control.** When the name servers match, the zone becomes active and answers DNS queries for the subdomain.

5. **Create DNS records.** Add required records (A, MX, TXT, etc.) to observe resolution behavior.

### Automation

Because each zone creation requires a new resource group and takes time to provision, a script was created to automate the process: [az-dns-zone-hunter.sh](https://github.com/okazymyrov/piki/blob/master/Vulnerabilities/Subdomain%20Takeover/scripts/azure/az-dns-zone-hunter.sh).

The script is designed to run in **Azure Cloud Shell** (Bash) and can be executed with the following command:

```bash
echo "" > ./az-dns-zone-hunter.sh && nano ./az-dns-zone-hunter.sh && chmod +x ./az-dns-zone-hunter.sh && ./az-dns-zone-hunter.sh -z [zone] -ns [ns1-09.azure-dns.com] -p [dns-ns-test] -s ["e09d32ee-ae58-41e9-8209-b3c44ed3b095"]
```
