# Špecifiká hosting providerov

## Websupport

| Parameter | Hodnota |
|-----------|---------|
| SSH host | `shell.rX.websupport.sk` (X = číslo clustra) |
| SSH port | Neštandardný (napr. 27229) - zistiť v dashboarde |
| Document root | `~/domena.sk/web/` |
| DB host | `db.rX.websupport.sk` |
| DB port | 3306 |
| PHP verzia | Nastavuje sa v admin dashboarde (nie .htaccess) |
| SMTP | `smtp.websupport.sk`, port 465 (SSL) |
| Shell timeout | Konzola sa deaktivuje po 60 minútach - treba aktivovať v dashboarde |
| Autentifikácia | Len heslo (SSH kľúč nie je štandardne podporovaný) |
| sshpass | Nutný pre automatizáciu (`brew install hudochenkov/sshpass/sshpass`) |

**Poznámky:**
- AddHandler v .htaccess pre PHP verziu **nefunguje** - Websupport používa PHP-FPM
- Shell sa aktivuje v sekcii Konzola a má časový limit
- Databázové mená a useri sú generované (napr. `7wAupgx9`)

## Verpex

| Parameter | Hodnota |
|-----------|---------|
| SSH port | 22 |
| Panel | cPanel |
| Document root | `~/public_html/` |
| DB host | `localhost` |
| PHP verzia | MultiPHP Manager v cPanel, alebo `.htaccess` AddHandler |
| SSH kľúče | Generovanie cez cPanel → SSH Access |

**Poznámky:**
- SSH kľúč vygenerovaný v cPanel musí byť **autorizovaný** (Manage → Authorize)
- Kľúč môže byť zašifrovaný passphrase - treba ssh-agent s expect
- Server name formát: `sXXXX.fraX.stableserver.net`

## Wedos

| Parameter | Hodnota |
|-----------|---------|
| SSH | Podporované na vyšších balíčkoch |
| Document root | `~/www/` alebo `~/subdom/domena/` |
| DB host | Interný (napr. `wm123.wedos.net`) |
| PHP verzia | Admin panel → Nastavenie → PHP |
| SMTP | `smtp.wedos.net` |

## Všeobecné cPanel hostingy

| Parameter | Hodnota |
|-----------|---------|
| SSH port | 22 (niekedy 2222 alebo iný) |
| Document root | `~/public_html/` |
| DB host | `localhost` |
| PHP verzia | MultiPHP Manager alebo `.htaccess`: `AddHandler application/x-httpd-phpXX .php` |
| SSH kľúče | cPanel → SSH/Shell Access |
