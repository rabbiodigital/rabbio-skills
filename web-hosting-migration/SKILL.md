---
name: web-hosting-migration
description: Migrácia webov medzi hostingami (PHP, Laravel, WordPress, static). Použiť keď používateľ chce presunúť web z jedného hostingu na druhý, migrovať hosting, preniesť databázu a súbory, alebo zmeniť hosting provider.
---

# Migrácia webu medzi hostingami

Systematický postup na migráciu webov cez SSH/SCP medzi ľubovoľnými hosting providermi.

## Prerekvizity od používateľa

Pred začatím zhromaždi tieto informácie:

### Zdrojový server (starý hosting)
- SSH host / IP adresa
- SSH port (štandardne 22, na cPanel hostingoch často 2222)
- SSH username
- SSH kľúč alebo heslo
- Cesta k webu (napr. `/home/user/public_html/`)

### Cieľový server (nový hosting)
- SSH/FTP prístupy (host, port, username, heslo)
- Databázové údaje (host, port, názov DB, username, heslo)
- SMTP údaje (ak web odosiela emaily)
- Document root cesta

## Workflow

Sleduj postup a aktualizuj TODO list:

```
Task Progress:
- [ ] Krok 1: Pripojenie na zdrojový server
- [ ] Krok 2: Prieskum štruktúry a konfigurácie
- [ ] Krok 3: Export databázy
- [ ] Krok 4: Záloha súborov
- [ ] Krok 5: Stiahnutie na lokál
- [ ] Krok 6: Nahratie na cieľový server
- [ ] Krok 7: Import databázy
- [ ] Krok 8: Úprava konfigurácie
- [ ] Krok 9: PHP verzia
- [ ] Krok 10: Test a DNS
```

## Krok 1: Pripojenie na zdrojový server

### DÔLEŽITÉ: Diagnostický postup pri SSH zlyhaniach
Vždy použi `-v` (verbose) flag na diagnostiku:
```bash
ssh -v -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i /path/to/key -p PORT user@host "echo OK" 2>&1 | tail -20
```

Kľúčové riadky na sledovanie:
- `Server accepts key` → kľúč je OK, problém je passphrase alebo oprávnenia
- `Offering public key ... explicit` → kľúč sa ponúka serveru
- `Authentications that can continue` → server kľúč odmietol
- `read_passphrase: can't open /dev/tty` → kľúč vyžaduje passphrase, neinteraktívne prostredie

### SSH kľúč
Ak kľúč z cPanel:
- Overiť autorizáciu verejného kľúča (cPanel → SSH Access → Manage → Authorize)
- **Overiť oprávnenia kľúča** – musia byť `600` (súbor) a `700` (adresár):
```bash
chmod 700 /path/to/key_directory
chmod 600 /path/to/key_directory/id_rsa
```
- **Pozor:** Používateľ môže uviesť cestu ku kľúču, ale reálne to je adresár obsahujúci `id_rsa`. Vždy overiť:
```bash
ls -la /path/to/key  # Je to súbor alebo adresár?
```

### SSH kľúč s passphrase (KRITICKÉ pre neinteraktívne prostredie)
Cursor shell nemá prístup k `/dev/tty` – nemôže interaktívne zadať passphrase.
**Jediné riešenie:** Použiť `expect` + `ssh-agent`:

```bash
eval "$(ssh-agent -s)"
expect -c '
spawn ssh-add /path/to/key
expect "Enter passphrase"
send "PASSPHRASE\r"
expect eof
'
# Overenie
ssh-add -l
```

**Poznámky:**
- Passphrase je často rovnaké ako SSH heslo poskytnuté používateľom
- Po pridaní do agenta všetky SSH/SCP príkazy v tej istej shell session fungujú automaticky
- `ssh-agent` platí len pre aktuálnu shell session – ak sa session zmení, treba znova
- NIKDY sa nevzdávaj pri passphrase – vždy použi `expect`, nefallbackuj na manuálny postup

### SSH s heslom
Nainštalovať sshpass (ak nie je):
```bash
brew install hudochenkov/sshpass/sshpass
```
Potom:
```bash
sshpass -p 'HESLO' ssh -T -o StrictHostKeyChecking=no -p PORT user@host "command"
```
**Poznámka:** Vždy použi `-T` flag (no pseudo-terminal) pri `sshpass` v neinteraktívnom prostredí.

### Overenie pripojenia
```bash
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p PORT user@host "echo 'SSH OK' && pwd && ls -la"
```

## Krok 2: Prieskum štruktúry

Na zdrojovom serveri zisti:

```bash
# Veľkosť webu
du -sh public_html/

# Štruktúra
ls -la public_html/

# PHP verzia
php -v | head -1
```

### Identifikácia typu webu

**Laravel** - hľadaj `artisan`, `composer.json`, `vendor/`
- Verzia: `php artisan --version`
- DB config: `.env` (Laravel 5+) alebo `app/config/database.php` (Laravel 4)
- Mail config: `.env` alebo `app/config/mail.php`

**WordPress** - hľadaj `wp-config.php`, `wp-content/`
- DB config: `wp-config.php` (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST)

**Statický web** - len HTML/CSS/JS, bez DB

### Nájdenie databázových údajov
```bash
# Laravel 5+
cat .env | grep -E "(DB_|MAIL_)"

# Laravel 4
cat app/config/database.php

# WordPress
grep -E "(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST)" wp-config.php
```

### Nájdenie SMTP údajov
```bash
grep -r 'smtp\|mail.*host\|mail.*password' --include='*.php' --include='*.env' /path/to/web/ -l
```

## Krok 3: Export databázy

```bash
mysqldump -u DB_USER -p'DB_PASS' DB_NAME > ~/backup.sql
ls -lh ~/backup.sql
```

## Krok 4: Záloha súborov

```bash
cd /home/user
tar czf web_backup.tar.gz public_html/
ls -lh web_backup.tar.gz
```

## Krok 5: Stiahnutie na lokál

```bash
mkdir -p /local/project/backup

# Databáza
scp -P PORT user@host:~/backup.sql /local/project/backup/

# Súbory
scp -P PORT user@host:~/web_backup.tar.gz /local/project/backup/
```

## Krok 6: Nahratie na cieľový server

```bash
# Upload
sshpass -p 'HESLO' scp -P PORT /local/project/backup/web_backup.tar.gz user@host:~/
sshpass -p 'HESLO' scp -P PORT /local/project/backup/backup.sql user@host:~/

# Rozbalenie do document root s automatickou detekciou štruktúry archívu
sshpass -p 'HESLO' ssh -p PORT user@host "cd ~/DOCROOT && \
  if tar tzf ~/web_backup.tar.gz | head -1 | grep -q 'public_html'; then \
    tar xzf ~/web_backup.tar.gz -C . --strip-components=1; \
  else \
    tar xzf ~/web_backup.tar.gz -C .; \
  fi"
```

**DÔLEŽITÉ:** Zisti document root na cieľovom serveri:
- Websupport: `~/domena.sk/web/`
- Wedos: `~/www/`  
- cPanel hostingy: `~/public_html/`

**Poznámka:** Archív z cPanel hostingov typicky obsahuje `public_html/` adresár.
Použiť `--strip-components=1` ak rozbaľujeme do iného document root.

## Krok 7: Import databázy

```bash
mysql -h DB_HOST -P DB_PORT -u DB_USER -p'DB_PASS' DB_NAME < ~/backup.sql
```

**Ak heslo obsahuje špeciálne znaky** (`&`, `;`, `<`, `>`, `|`, `!`, `$`):
```bash
# Použiť MYSQL_PWD environment premennú namiesto -p
export MYSQL_PWD='heslo_so_specialnymi_znakmi'
mysql -h DB_HOST -u DB_USER DB_NAME < ~/backup.sql
unset MYSQL_PWD
```

Overiť:
```bash
mysql -h DB_HOST -u DB_USER -p'DB_PASS' DB_NAME -e "SHOW TABLES;"
```

## Krok 8: Úprava konfigurácie

Zmeniť databázové a SMTP údaje:

**Laravel 5+ (.env):**
```
DB_HOST=novy_host
DB_DATABASE=nova_db
DB_USERNAME=novy_user
DB_PASSWORD=nove_heslo

MAIL_HOST=novy_smtp
MAIL_PASSWORD=nove_heslo
```

**Laravel 4 (app/config/database.php, app/config/mail.php):**
Editovať hodnoty priamo v PHP poliach pomocou sed alebo priameho editovania.

**WordPress (wp-config.php):**
```bash
# Použiť | ako delimiter v sed (heslo môže obsahovať / a iné znaky)
sed -i "s|define( 'DB_NAME', '.*' );|define( 'DB_NAME', 'NOVA_DB' );|" wp-config.php
sed -i "s|define( 'DB_USER', '.*' );|define( 'DB_USER', 'NOVY_USER' );|" wp-config.php
sed -i "s|define( 'DB_PASSWORD', '.*' );|define( 'DB_PASSWORD', 'NOVE_HESLO' );|" wp-config.php
sed -i "s|define( 'DB_HOST', '.*' );|define( 'DB_HOST', 'NOVY_HOST' );|" wp-config.php
```

**WordPress - opraviť hardcoded cesty:**
```bash
# Pluginy ako AIOWPSEC majú hardcoded cesty v wp-config.php
# Hľadať cesty so starým document root a nahradiť
grep -n '/home/STARY_USER/public_html/' wp-config.php
# Ak nájdené, nahradiť relatívnou cestou alebo novým document root
```

**WordPress - URL zmena v DB** (ak sa mení doména):
```sql
UPDATE wp_options SET option_value = 'https://nova-domena.sk' WHERE option_name IN ('siteurl', 'home');
```

## Krok 9: PHP verzia

### Kľúčové pravidlo
**Vždy najprv zisti PHP verziu na zdrojovom serveri** a nastav rovnakú na cieľovom.

```bash
# Na zdrojovom serveri
php -v | head -1
```

### Nastavenie PHP verzie podľa hostingu

| Hosting | Kde nastaviť |
|---------|-------------|
| Websupport | Admin dashboard (nie .htaccess) |
| Wedos | Admin panel → PHP verzia |
| cPanel | MultiPHP Manager alebo `.htaccess` AddHandler |

### Známe problémy s PHP verziami
- **Laravel 4.x:** vyžaduje PHP 5.4+ , reálne najlepšie funguje na PHP 5.6
- **Laravel 5.x:** vyžaduje PHP 5.6+ alebo 7.0+
- **Laravel 6+:** vyžaduje PHP 7.2+
- **WordPress 5.x:** PHP 7.4 odporúčané
- **WordPress 6.x:** PHP 8.0+ odporúčané
- `MB_OVERLOAD_STRING` error → PHP 8.0+ odstránilo túto konštantu, treba PHP 7.x
- `artisan` môže bežať na novšom PHP, ale web padne na vendor závislostiach

### Oprávnenia
```bash
# Laravel - storage musí byť zapisovateľný
chmod -R 777 laravel/app/storage   # Laravel 4
chmod -R 777 storage bootstrap/cache  # Laravel 5+

# WordPress
chmod -R 755 wp-content
chmod 644 wp-config.php
```

## Krok 10: Test a DNS

### Lokálne testovanie (pred DNS zmenou)
Zistiť IP cieľového servera a pridať do `/etc/hosts`:
```
NOVA_IP  domena.sk
NOVA_IP  www.domena.sk
```

### DNS prepnutie
Po overení funkčnosti zmeniť A záznam u registrátora na novú IP.

### Post-migrácia checklist
- [ ] Web sa načíta správne
- [ ] Podstránky fungujú (routing)
- [ ] Formuláre odosielajú emaily
- [ ] SSL certifikát (Let's Encrypt) aktivovaný
- [ ] Odstrániť záznam z `/etc/hosts`
- [ ] Vyčistiť dočasné súbory na oboch serveroch
- [ ] Lokálna záloha uložená

## Známe špecifiká hostingov

Pre detaily o konkrétnych hosting provideroch pozri [hostings.md](hostings.md).

## Troubleshooting

Pre bežné problémy a ich riešenia pozri [troubleshooting.md](troubleshooting.md).
