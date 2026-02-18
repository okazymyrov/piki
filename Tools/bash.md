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
cat [file.txt] | xargs -L 1 -I {} printf "{}\nCg==" | base64 -d
```

# Generate random hex
```sh
dd if=/dev/urandom count=32 bs=1 | shasum -a 256
```

# Convert a binary file to the text declaring a C/C++ array
```sh
xxd -i [file]
```

# Generate HMAC
```sh
INPUT="example.com"; DATE=$(date +%s); NAME="Oleksandr Kazymyrov"; NONCE=$(openssl rand -hex 32); KEY=$(openssl rand -hex 32); MESSAGE="$DATE|$NAME|$INPUT|$NONCE"; HMAC=$(printf "%s" "$MESSAGE" | openssl dgst -sha256 -hmac "$KEY" | awk '{print $2}'); echo -e "Date: $DATE\nName: $NAME\nINPUT: $INPUT\nNonce: $NONCE\nKey: $KEY\nMessage: $MESSAGE\nHMAC: $HMAC\n\nVerification string:\nprintf \"%s\" \"$MESSAGE\" | openssl dgst -sha256 -hmac \"$KEY\""
```

# PS1 on Kali
```sh
# ~/.zshrc
export PS1="%F{%(#.blue.green)}┌──%F{yellow}(%D{%F %T})%F{%(#.blue.green)}-(%B%F{%(#.red.blue)}%n㉿%m%b%F{%(#.blue.green)})-[%B%F{reset}%(6~.%-1~/…/%4~.%5~)%b%F{%(#.blue.green)}]
└─%B%(#.%F{red}#.%F{blue}$)%b%F{reset} "
```
