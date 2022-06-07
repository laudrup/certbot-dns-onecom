One.com DNS Authenticator plugin for Certbot
============================================

Create a text file with the following content:

```
# One.com credentials used by Certbot
dns_onecom_username = johndoe
dns_onecom_password = hunter2
```

Run the following command: `sudo certbot certonly -d \*.example.com -d example.com -a dns-onecom`

When prompted for the config file, enter the path to the above text file.

About
-----

Since [One.com](https://one.com) doesn't have an official API this
plugin is made by reverse engineering the web interface and uses web
scraping.

This means it might stop working any time or even worse, do something
unexpected. Use at your own risk. I do use this myself though until I
change to a better DNS provider though.

This is plugin is more or less made by modifying
[`certbot-dns-ispconfig`](https://github.com/m42e/certbot-dns-ispconfig).
and
[`certbot-dns-gratisdns`](https://github.com/Mortal/certbot-dns-gratisdns)
