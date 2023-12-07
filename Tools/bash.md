# From "foo" to the end of file
```sh
sed -n '/foo/,$p' ./users.txt > ./users.foo-.txt
```

# Compare two files with exact matches
```sh
grep -xFf ./ntlm.txt ./pwned-passwords-ntlm-ordered-by-hash-v8.txt
```

# Decode base64 encoded lines
```sh
cat ./file.txt | xargs -L 1 -I {} printf "{}\nCg==" | base64 -d
```

# Generate random hex
```sh
dd if=/dev/urandom count=32 bs=1 | shasum -a 256
```
