# Google Cloud DNS: Dangling NS Delegation Leading to Subdomain Takeover

## Answer from Google (Issue Tracker: 467308576 / Cloud VRP)

>Our team has analyzed this report and decided not to track it as a security bug. When we file a security vulnerability to product teams, we impose monitoring and escalation processes for teams to follow, and the security risk described in this report does not meet the threshold that we require for this type of escalation on behalf of the security team.

## Timeline

| Date       | Status |
|------------|--------|
| 2025-12-09 | Report created (Issue Tracker: 467308576) |
| 2025-12-09 | Initial triage response |
| 2025-12-18 | Status: Won’t Fix (Intended behavior) |
| **before 2026-02-13** | **Google silently fixed the reported vulnerability** |


## Google Cloud DNS Specifics

### Name Server Shards

Google Cloud DNS assigns every public managed zone to [**one of five name server shards**](https://docs.cloud.google.com/dns/quotas#name-server-limits), identified by the letters **a** through **e**. Each shard consists of four name servers. The shard letter appears immediately before the number in the authoritative name server name:

| Shard | Name Servers |
|-------|-------------|
| A | `ns-cloud-a1.googledomains.com` through `ns-cloud-a4.googledomains.com` |
| B | `ns-cloud-b1.googledomains.com` through `ns-cloud-b4.googledomains.com` |
| C | `ns-cloud-c1.googledomains.com` through `ns-cloud-c4.googledomains.com` |
| D | `ns-cloud-d1.googledomains.com` through `ns-cloud-d4.googledomains.com` |
| E | `ns-cloud-e1.googledomains.com` through `ns-cloud-e4.googledomains.com` |

Because there are only five possible shards, an attacker has a **1-in-5 (20%) chance** of being assigned the correct shard on each zone creation attempt. This makes the delete-and-retry cycle highly practical - on average, only a small number of attempts are needed to match the dangling delegation.

### Takeover Procedure

1. **Identify the dangling NS delegation.** Determine which Google Cloud DNS shard the target subdomain's NS records reference (e.g., `ns-cloud-d1.googledomains.com` through `ns-cloud-d4.googledomains.com` indicates the **D** shard).

2. **Create a public managed zone** in Google Cloud DNS for the target subdomain (e.g., `monitor.example.com`).

3. **Check the assigned shard.** If the zone is assigned to a different shard than the dangling delegation, create it again. Repeat until the correct shard is assigned.

4. **Confirm authoritative control.** When the shard matches, the zone becomes active and answers DNS queries for the subdomain.

5. **Create DNS records.** Add required records (A, MX, TXT, etc.) to observe resolution behavior.

### Behavior After 13th of February 2026

Google has started strictly following the behavior stated at [Name server limits](https://docs.cloud.google.com/dns/quotas#name-server-limits) at least from 2026-02-13.

A new managed zone for a domain cannot be assigned to a shard if any of the following already exists on the same shard:

- A managed zone with the **same DNS name** (e.g., `domain.example.tld`)
- A **subdomain** of the DNS name (e.g., `sub.domain.example.tld`)
- A **parent domain** of the DNS name (e.g., `example.tld`)

This results in the following limitations for public managed zones:

- A maximum of **five zones** with the exact same DNS name can exist (one per shard).
- For any parent domain, a maximum of **five levels of subdomains** can be created.

These limitations apply across all projects and users in Google Cloud. Non-delegated subdomains and delegations hosted on other DNS services do not count against this limit. Before Cloud DNS creates a zone that occupies the last available name server shard, **domain ownership must be verified** with a TXT record.
