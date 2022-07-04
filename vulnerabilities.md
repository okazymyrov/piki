# OneDrive for Business: Bypass "Anyone with the link" restriction

Answer from Microsoft (MSRC Case 72610 CRM:0022004898):
> We determined that a specific fix will not be released for the reported behavior.

Steps to reproduce:
1.	Go to https://developer.microsoft.com/en-us/graph/graph-explorer
2.	Run query https://graph.microsoft.com/v1.0/me/drive/root/children
3.	Find the first file (i.e., "All Japan Revenues By City.xlsx") and copy "@microsoft.graph.downloadUrl"
4.	Open "@microsoft.graph.downloadUrl" in a browser on another device with another IP
5.	Observe that the file is downloaded without any security verification, which bypasses disabled "Anyone with the link".
