# From "foo" to the end of file
```sh
sed -n '/foo/,$p' ./users.txt > ./users.foo-.txt
```

# Compare two files with exact matches
```sh
grep -xFf ./ntlm.txt ./pwned-passwords-ntlm-ordered-by-hash-v8.txt
```
