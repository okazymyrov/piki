# Bypass MFA authorization in multi-session AVD

## Answer from Microsoft (VULN-113950 / MSRC Case 83840 CRM:0022036283):
> Thank you again for submitting this issue to Microsoft. We determined that this behavior is considered to be by design because SSO is not enabled on the server and one has to enable AAD SSO https://learn.microsoft.com/en-us/azure/virtual-desktop/configure-single-sign-on if they want to get MFA to work.

## Timeline

<!--

```mermaid
 info
```

Tested on v10.6.1

```mermaid
%%{init: { 'theme': 'base', 'gitGraph': {'mainBranchName':"okazymyrov"}}}%%
    gitGraph TB:
	commit id: "2023-11-21" tag: "Report created"
    branch Microsoft
    checkout Microsoft
	commit id: "2023-11-23" tag: "Status changed from New to Review / Repro"
	commit id: "2023-11-28" tag: "Questions from Microsoft"
    checkout okazymyrov
    merge Microsoft
	commit id: "2023-11-29" tag: "Reproduction"
    commit id: "2023-11-30" tag: "Answers to Microsoft"
    checkout Microsoft
    merge okazymyrov
	commit id: "2023-12-04" tag: "Complete (Rejected / By design)"
```

-->

| Date | Status|
| --- | --- |
| 2023-11-21| Report created |
| 2023-11-23| Status changed from **New** to **Review / Repro** |
| 2023-11-29| Questions from Microsoft |
| 2023-11-28| Reproduction in the test environment |
| 2023-11-30| Answers to Microsoft |
| 2023-12-04| Complete (**Rejected / By design**) |

## Summary
When using Microsoft Remote Desktop in the browser, the multi-factor authentication (MFA) is only applied to the web app (the client), not to the remote desktop session. This means that an attacker who accesses a shared Azure Virtual Desktop (AVD) with multiple sessions can switch to other users in the browser without MFA verification.

## Description
On occasions, applications are open to guest users requiring connection to an internal system via a multi-session, commonly referred to as a shared, Azure Virtual Desktop (AVD). This introduces a security concern, as an unauthorized individual gaining entry to the tenant through a user with shared AVD privileges can impersonate other users in the browser without undergoing multi-factor authentication (MFA).

## Steps to Reproduce
### Prerequisites
* The adversary can log on as User 1 (including MFA)
* Multi-session AVD is enabled for User 1, User 2 and User 3 in the same tenant
* The adversary knows passwords for User 2 and User 3 (not MFA)

### Steps
1. Log on AVD as User 1
2. Open an app in AVD
3. On the logon page, use credentials from User 2
4. Observe that MFA is not required for User 2

### Supporting materials/references:
#### Possible Consequences
* Take over active sessions (including desktop applications and active sessions in browsers) for User 2
* Create an MFA backdoor for users satisfying MFA in the token
* Connect to other accounts on the same server using RDP. For example, by using the application escape technique shadow the remote desktop session of User 3 from User 2.

#### A kill chain from a real engagement:
* Compromize an account from 3rd party vendor (i.e., User 1) having access to the Contoso tenant.
* Collect a list of valid passwords for users in Contoso (i.e., for User 2 and User 3).
* Obtain a valid session for User 1 with MFA satisfied ([reproducible step 1](https://github.com/okazymyrov/piki/blob/master/Vulnerabilities/Vulnerabilities.md#steps)).
* Open Edge ([reproducible step 2](https://github.com/okazymyrov/piki/blob/master/Vulnerabilities/Vulnerabilities.md#steps)).
* When prompted for credentials, use User 2 login and password (no MFA required) ([reproducible step 3](https://github.com/okazymyrov/piki/blob/master/Vulnerabilities/Vulnerabilities.md#steps)).
* Open the task manager (i.e., using the application escape technique) to monitor users logged into the shared AVD.
* During lunch (higher chance of having browsers open and a valid token with MFA satisfied), login as a different user via RDP shadowing using User 3's credentials (alternatively right click in the task manager on the user and then connect).
* If the user has recently authenticated to the Contoso tenant using MFA (i.e., the MFA requirement is contained in the token), update that user's security information to include an attacker-controlled security factor (such as TOTP).
