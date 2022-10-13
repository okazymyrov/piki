# Capturing

## SMB
```sh
tcpdump port 445 -w <path_to_pcap>
```

# Extraction
## NTLMv2
### NTLMRawUnhide
[NTLMRawUnHide](https://github.com/mlgualtieri/NTLMRawUnHide)
```sh
./NTLMRawUnhide.py -i <path_to_pcap> -o <path_to_hashes>
```
