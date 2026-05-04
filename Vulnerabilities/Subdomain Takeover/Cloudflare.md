# Cloudflare DNS: Dangling NS Delegation Leading to Subdomain Takeover

## Free Tier

Cloudflare's **free tier does not allow creating subdomain zones**. Attempting to add a subdomain as a zone on a free account results in an error, making the free tier **not vulnerable** to NS delegation takeover.

![Cloudflare free tier error when creating a subdomain zone](https://raw.githubusercontent.com/okazymyrov/piki/master/Vulnerabilities/Subdomain%20Takeover/assets/cloudflare.png)

## Subdomain Setup (Enterprise)

Cloudflare offers a [subdomain setup](https://developers.cloudflare.com/dns/zone-setups/subdomain-setup/) feature that allows managing Cloudflare configurations for one or more subdomains separately from the apex domain. With this setup, subdomains like `blog.example.com` appear as separate zones on the account dashboard, each with independent settings.

This feature is only available on the **Enterprise** plan. It requires the parent zone to also be on Cloudflare, and the available configurations depend on both the parent zone setup and the child zone setup.

**Enterprise tiers were not tested** due to access limitations.
