# OneDrive for Business: Bypass "Anyone with the link" restriction

## Answer from Microsoft (VULN-069036 / MSRC Case 72610 CRM:0022004898):
> We determined that a specific fix will not be released for the reported behavior.

## Steps to reproduce:
1.	Go to https://developer.microsoft.com/en-us/graph/graph-explorer
2.	Run query https://graph.microsoft.com/v1.0/me/drive/root/children
3.	Find the first file (i.e., "All Japan Revenues By City.xlsx") and copy "@microsoft.graph.downloadUrl"
4.	Open "@microsoft.graph.downloadUrl" in a browser on another device with another IP
5.	Observe that the file is downloaded without any security verification, which bypasses disabled "Anyone with the link".

# MFA bypass in multi-session AVD

## Answer from Microsoft (VULN-113950 / MSRC Case 83840 CRM:0022036283):
> Thank you again for submitting this issue to Microsoft. We determined that this behavior is considered to be by design because SSO is not enabled on the server and one has to enable AAD SSO https://learn.microsoft.com/en-us/azure/virtual-desktop/configure-single-sign-on if they want to get MFA to work.


## Summary
When using Microsoft Remote Desktop in the browser, the multi-factor authentication (MFA) is only applied to the web app (the client), not to the remote desktop session. This means that an attacker who accesses a shared Azure Virtual Desktop (AVD) with multiple sessions can switch to other users in the browser without MFA verification.

## Description
Some of our applications are accessible to guest users who need to connect to an internal system through a multi-session (hereinafter referred to as shared) Azure Virtual Desktop (AVD). This poses a security risk because an attacker who gains access to the tenant as user with the shared AVD can impersonate other users in the browser without having to pass multi-factor authentication (MFA).

## Steps to Reproduce
### Prerequisites
* The adversary can log on as User 1 (including MFA)
* Multi-session AVD is enabled for User 1, User 2 and User 3 in the same tenant
* The adversary knows passwords for User 2 and User 3 (no MFA)

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
* Obtain a valid session for User 1 with MFA satisfied (reproducible step 1).
* Open Edge (reproducible step 2).
* When prompted for credentials, use User 2 login and password (no MFA required) (reproducible step 3).
* Open the task manager (i.e., using the application escape technique) to monitor users logged into the shared AVD.
* During lunch (higher chance of having browsers open and a valid token with MFA satisfied), login as a different user via RDP shadowing using User 3's credentials (alternatively right clicki in the task manager on the user and then connect).
* If the user has recently authenticated to the Contoso tenant using MFA (i.e., the MFA requirement is contained in the token), update that user's security information to include an attacker-controlled security factor (such as TOTP).
