# AWS Route 53: Dangling NS Delegation Leading to Subdomain Takeover

## Answer from AWS (Report #3461603 on HackerOne)

> After further investigation, we confirmed that the behavior described in your report does not represent a security vulnerability with AWS products or services, rather, it is on the customer side of the shared responsibility model. We have updated our public documentation to include [three new scenarios](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/protection-from-dangling-dns.html) (Scenario 4, Scenario 5, Scenario 6) to more clearly communicate the available protections for customers.

## Timeline

| Date       | Status |
|------------|--------|
| 2025-12-11 | Report submitted to AWS VDP |
| 2025-12-12 | AWS requested additional information |
| 2025-12-12 | Provided clarification |
| 2025-12-13 | Severity set to High <br> Pending program review |
| 2026-01-20 | AWS confirmed investigation in progress |
| 2026-02-09 | Requested status update |
| 2026-02-18 | Reported real-world takeover |
| 2026-02-27 | Severity changed to None <br> Closed as Informative (Customer-side under Shared Responsibility Model) <br> Complete |
