# Subdomain Takeover via Dangling NS Records

## What is NS Dangling

NS Dangling (also known as *dangling name server delegation*) is a DNS misconfiguration condition in which a domain’s NS records point to name servers that are no longer valid, no longer authoritative, or whose ownership has changed.

This typically occurs during:

- DNS provider migrations  
- Decommissioning of DNS infrastructure  
- Expired or deleted DNS accounts  
- Incomplete cleanup of legacy NS records  

If the referenced name servers become available for re-registration or reassignment, a third party may claim them and potentially gain control over DNS resolution for the affected domain.

## Security Impact

Because NS records control **delegation authority**, NS Dangling can enable high-impact compromise scenarios affecting multiple services simultaneously. Depending on the environment and DNS usage, impacts may include:

- **Full DNS takeover / zone control**  
  Ability to publish arbitrary DNS records (A/AAAA/CNAME/TXT/MX/NS), fully controlling resolution behavior.

- **Web traffic redirection and credential theft**  
  Redirection of production services to attacker infrastructure for phishing and impersonation.

- **TLS certificate issuance and HTTPS impersonation**  
  DNS control enables satisfying DNS-based certificate validation (e.g., ACME DNS-01), allowing issuance of valid TLS certificates for the affected domain.

- **Email compromise (MX, SPF, DKIM, DMARC)**  
  Manipulation of mail routing and anti-spoofing mechanisms can:
  - Redirect inbound mail
  - Enable convincing outbound spoofing
  - Break legitimate mail delivery
  - Damage sender reputation

- **Abuse of wildcard records and cookie scoping weaknesses**  
  Attackers may leverage wildcard DNS entries to stand up arbitrary subdomains. Combined with overly broad cookie scopes, this may enable session fixation, token leakage, or cross-subdomain attacks.

- **Interception of internal service calls (trusted internal resolution)**  
  In environments where internal systems implicitly trust DNS resolution for service-to-service communication, manipulated NS delegation may allow interception, spoofing, or tampering of backend traffic.

- **Targeted redirection of CI/CD or service endpoints**  
  Build pipelines, artifact repositories, container registries, webhook receivers, or deployment endpoints that rely on DNS resolution may be selectively redirected, enabling code tampering, artifact poisoning, or deployment manipulation.

- **Supply chain implications**  
  If update endpoints, SDK download domains, package repositories, or third-party integrations rely on the affected delegation, attackers may introduce malicious components into downstream systems.

- **Account takeover via password reset interception**  
  Control over authentication-related DNS endpoints can facilitate interception of reset flows and compromise of privileged accounts.

- **API, webhook, and integration hijacking**  
  DNS manipulation of service endpoints may enable data exfiltration, malicious responses, or integrity violations.

- **Operational disruption and reputational damage**  
  Even without full exploitation, dangling NS configurations may cause instability, outage conditions, and significant trust impact.


## Provider Evaluation Summary

The following table summarizes where **Proof of Validation (PoV)** was performed on non-owned apex domains.

| DNS Provider | PoV (December 2025) | PoV (February 2026)|
|--------------|---------------------|---------------------|
| Cloudflare (Free) | ❌ | ❌ |
| Amazon Route 53* | ❌ | ✅ |
| Microsoft (Azure DNS) | ✅ | ✅ |
| Google Cloud DNS | ✅ | ❌ |
| DNSimple | ✅ | ❌ |
| Imperva |  ❌ | ❌ |

### Notes

- Cloudflare Business/Enterprise, CSCDBS, MarkMonitor, and other enterprise-focused DNS providers were not evaluated due to subscription requirements.
- \*Initially Route 53 considered complex to exploit, but later successfully validated on a real-world domain. This demonstrates that despite higher operational complexity, the vulnerability condition can exist and be practically exploitable. The attack scenario primarily applies when NS delegation originates from an external DNS provider (e.g., delegation from Cloudflare to AWS).
