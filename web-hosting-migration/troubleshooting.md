# Troubleshooting - bežné problémy pri migrácii

## SSH pripojenie

### Permission denied (publickey)
- **Príčina:** Kľúč nie je autorizovaný na serveri
- **Riešenie:** V cPanel → SSH Access → Manage → Authorize verejný kľúč

### Kľúč vyžaduje passphrase
- **Symptóm:** SSH sa pýta heslo aj keď je kľúč správny
- **Overenie:** Hlavička kľúča obsahuje `aes256-ctr` + `bcrypt`
- **Riešenie:** Použiť ssh-agent s expect (viď hlavný SKILL.md)

### Connection refused
- **Príčina:** Nesprávny port
- **Riešenie:** Overiť port v hosting dashboarde. Bežné porty: 22, 2222, 27229

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
- **Tip:** Heslo s `$`, `!`, `|`, `{`, `}` treba obalíť single quotes a escapovať

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
- **Riešenie:**
```sql
UPDATE wp_options SET option_value = 'https://nova-domena.sk' WHERE option_name IN ('siteurl', 'home');
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
