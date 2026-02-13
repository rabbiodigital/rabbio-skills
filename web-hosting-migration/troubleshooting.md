# Troubleshooting - bežné problémy pri migrácii

## SSH pripojenie

### Permission denied (publickey)
- **Príčina:** Kľúč nie je autorizovaný na serveri
- **Riešenie:** V cPanel → SSH Access → Manage → Authorize verejný kľúč

### Kľúč vyžaduje passphrase (neinteraktívne prostredie)
- **Symptóm:** `read_passphrase: can't open /dev/tty: Device not configured`
- **Diagnostika:** V `-v` výstupe vidíš `Server accepts key` ale potom `read_passphrase` error
- **Overenie:** Hlavička kľúča obsahuje `aes256-ctr` + `bcrypt`
- **Riešenie:** **VŽDY** použiť `expect` + `ssh-agent`:
```bash
eval "$(ssh-agent -s)"
expect -c '
spawn ssh-add /path/to/key
expect "Enter passphrase"
send "PASSPHRASE\r"
expect eof
'
ssh-add -l  # Overenie
```
- **Poznámka:** Passphrase býva často rovnaké ako SSH heslo od používateľa
- **NIKDY** nefallbackuj na manuálny postup – `expect` vždy funguje

### Kľúč je adresár, nie súbor
- **Symptóm:** `Load key "/path/to/key": Is a directory`
- **Príčina:** Používateľ stiahol kľúč z cPanel ako adresár s `id_rsa` vnútri
- **Riešenie:** Použiť celú cestu vrátane `id_rsa`:
```bash
ls -la /path/to/key/       # Zistiť obsah
ssh -i /path/to/key/id_rsa ...
```

### Nesprávne oprávnenia kľúča
- **Symptóm:** `WARNING: UNPROTECTED PRIVATE KEY FILE! Permissions 0755 are too open`
- **Riešenie:**
```bash
chmod 700 /path/to/key_directory
chmod 600 /path/to/key_directory/id_rsa
```

### sshpass: Permission denied
- **Príčina:** Heslo pre SSH nemusí byť rovnaké ako heslo v cPanel. Na cPanel hostingoch je často primárna autentifikácia kľúčom.
- **Riešenie:** Najprv skúsiť kľúč. Heslo je pravdepodobne passphrase ku kľúču, nie SSH heslo.

### Connection refused
- **Príčina:** Nesprávny port
- **Riešenie:** Overiť port v hosting dashboarde. Bežné porty: 22, 2222, 27229, 27376

## PHP verzia

### MB_OVERLOAD_STRING error
```
Undefined constant "Patchwork\Utf8\MB_OVERLOAD_STRING"
```
- **Príčina:** PHP 8.0+ odstránilo `MB_OVERLOAD_STRING` konštantu
- **Riešenie:** Prepnúť na PHP 7.4 alebo nižšie

### Artisan beží ale web padá
- **Príčina:** CLI artisan načíta len jadro, web načíta aj vendor balíčky (dompdf, image, excel...)
- **Riešenie:** Nastaviť rovnakú PHP verziu ako na pôvodnom serveri

### AddHandler nefunguje na Websupport
- **Príčina:** Websupport používa PHP-FPM, nie Apache mod_php
- **Riešenie:** Nastaviť PHP verziu cez admin dashboard

## Databáza

### Access denied pri importe
- **Overiť:** Správny host (nie localhost ak je externý DB server)
- **Overiť:** Špeciálne znaky v hesle - escapovať v shell príkaze
- **Tip:** Heslo s `$`, `!`, `|`, `{`, `}`, `&`, `;`, `<`, `>` treba obalíť single quotes
- **Najlepšie riešenie pre špeciálne znaky:** Použiť `MYSQL_PWD` environment premennú:
```bash
export MYSQL_PWD='heslo_so_specialnymi_znakmi'
mysql -h HOST -u USER DB_NAME < dump.sql
unset MYSQL_PWD
```

### Character set problémy
- **Symptóm:** Diakritika sa zobrazuje nesprávne
- **Riešenie:** Pri dumpe aj importe špecifikovať charset:
```bash
mysqldump --default-character-set=utf8 ...
mysql --default-character-set=utf8 ...
```

## Web nefunguje po migrácii

### 500 Internal Server Error
1. Skontrolovať error_log v document root
2. Overiť oprávnenia na storage/cache priečinkoch
3. Overiť PHP verziu
4. Overiť databázové pripojenie

### Stránky vrátia 404 (okrem homepage)
- **Príčina:** mod_rewrite nie je aktívny alebo .htaccess sa neaplikuje
- **Riešenie:** Overiť že .htaccess existuje v document root

### WordPress - "Error establishing database connection"
- **Príčina:** Nesprávne DB údaje v wp-config.php
- **Riešenie:** Overiť DB_HOST - na Websupport nie je localhost ale `db.rX.websupport.sk`

### WordPress - presmerovanie na starú doménu
- **Príčina:** siteurl a home v wp_options tabuľke
- **Riešenie:** Najprv zistiť prefix tabuliek (nie vždy `wp_`):
```bash
grep 'table_prefix' wp-config.php  # Napr. $table_prefix = 'NAIKr7y_';
```
```sql
UPDATE PREFIX_options SET option_value = 'https://nova-domena.sk' WHERE option_name IN ('siteurl', 'home');
```

### WordPress - hardcoded cesty v wp-config.php
- **Príčina:** Pluginy (napr. AIOWPSEC) pridávajú do wp-config.php absolutné cesty k starému serveru
- **Symptóm:** `include_once('/home/STARY_USER/public_html/plugin-file.php')` → file not found
- **Riešenie:** Nahradiť relatívnou cestou alebo odstrániť:
```bash
grep -n '/home/' wp-config.php  # Nájsť hardcoded cesty
sed -i "s|/home/STARY_USER/public_html/|./|g" wp-config.php
```

## SMTP / Emaily

### Emaily sa neodosielajú
1. Overiť SMTP host pre nový hosting (napr. `smtp.websupport.sk`)
2. Overiť port (465/SSL alebo 587/TLS)
3. Overiť že mailová schránka existuje na novom hostingu
4. Overiť heslo (niektoré hostingy vyžadujú špeciálne znaky)

### SMTP timeout
- **Príčina:** Nesprávny port alebo encryption typ
- **Riešenie:** Skúsiť port 587 s TLS ak 465 s SSL nefunguje (alebo naopak)
