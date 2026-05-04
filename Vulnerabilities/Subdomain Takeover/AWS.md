# AWS Route 53: Dangling NS Delegation Leading to Subdomain Takeover

## Answer from AWS (Report #3461603 on HackerOne)

> After further investigation, we confirmed that the behavior described in your report does not represent a security vulnerability with AWS products or services, rather, it is on the customer side of the shared responsibility model. We have updated our public documentation to include [three new scenarios](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/protection-from-dangling-dns.html) (Scenario 4, Scenario 5, Scenario 6) to more clearly communicate the available protections for customers.

## Timeline

| Date       | Status |
|------------|--------|
| 2025-12-11 | Report submitted to AWS VDP |
| 2025-12-12 | AWS requested additional information |
| 2025-12-12 | Provided clarification |
| 2025-12-13 | Severity set to High; Pending program review |
| 2026-01-20 | AWS confirmed investigation in progress |
| 2026-02-09 | Requested status update |
| 2026-02-18 | Reported real-world takeover |
| 2026-02-27 | Severity changed to None; Closed as Informative (Customer-side under Shared Responsibility Model); Complete |

## AWS Route 53 Specifics

### Name Server Assignment

AWS Route 53 assigns every hosted zone a set of **four name servers**, one from each of the four top-level domains:

- `ns-XXX.awsdns-XX.com`
- `ns-XXXX.awsdns-XX.net`
- `ns-XXXX.awsdns-XX.org`
- `ns-XXX.awsdns-XX.co.uk`

Route 53 draws from a pool of **2,000+ name servers**. Each zone is assigned **4 random name servers** from this pool, and zone creation is a time-consuming process. This makes direct brute-force through hosted zone creation impractical.

### Reusable Delegation Sets

AWS Route 53 supports **reusable delegation sets**, which allow multiple hosted zones to share the same set of four name servers. Without a reusable delegation set, each zone gets different name servers assigned randomly. With a reusable delegation set, all zones created using it share the same 4 name servers.

This feature is key to the takeover attack: instead of creating hosted zones repeatedly (which is slow and costly), an attacker can rapidly create and delete **reusable delegation sets** to brute-force a name server match. A **partial overlap of just 1 out of 4 matching name servers** is sufficient for takeover.

![Reusable Delegation Set](https://raw.githubusercontent.com/okazymyrov/piki/master/Vulnerabilities/Subdomain%20Takeover/assets/route53-reusable-delegation-set.svg)

### Takeover Procedure

1. **Reconnaissance.** Identify targets with dangling NS delegations pointing to Route 53 name servers.

2. **Create a reusable delegation set.** AWS assigns 4 name servers from the global pool.

3. **Compare name servers.** Check if any of the assigned name servers match the dangling NS delegation. A partial overlap (1 of 4 matching NS) is sufficient.

4. **Delete & retry.** If no name servers match, delete the delegation set and create a new one. Repeat until a match is found.

5. **Create hosted zone.** Once a matching delegation set is found, create a hosted zone for the target subdomain using that delegation set.

6. **Actions on objectives.** Add DNS records (A, MX, TXT, etc.) to achieve traffic interception, identity compromise, or cross-environment pivoting.

![Route 53 Exploitation Flow](https://raw.githubusercontent.com/okazymyrov/piki/master/Vulnerabilities/Subdomain%20Takeover/assets/route53-exploitation.svg)
