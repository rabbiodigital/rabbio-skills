---
name: session-end
description: Vytvorí development log záznam na konci pracovnej session. Použiť keď používateľ chce ukončiť session, zdokumentovať prácu, vytvoriť dev log, alebo keď sa blíži koniec kontextu.
---

# Session End Documentation

Vytvor development log záznam dokumentujúci prácu vykonanú v tejto session.

## Kedy použiť

- Používateľ chce ukončiť/uzavrieť session
- Používateľ žiada dokumentáciu práce
- Blíži sa limit kontextu
- Po dokončení väčšej úlohy

## Inštrukcie

### 1. Analyzuj session

Prejdi celú konverzáciu a identifikuj:
- Aké úlohy sa riešili
- Aké súbory sa zmenili
- Aké rozhodnutia sa prijali
- Čo fungovalo, čo nie
- Čo zostalo nedokončené

### 2. Zisti kam uložiť

Opýtaj sa používateľa (ak nevieš):
- Existuje už `docs/devlogs/` priečinok v projekte?
- Ak nie, má sa vytvoriť?
- Alebo má ísť do iného umiestnenia?

### 3. Vytvor dev log

Použi tento formát:

```markdown
# YYYY-MM-DD - Stručný názov

## Overview
2-3 vety čo sa dosiahlo.

## Context
Prečo sa to robilo. Odkaz na issue/task ak existuje.

## Čo sa spravilo
- Konkrétna zmena 1
- Konkrétna zmena 2

## Súbory zmenené
- `cesta/k/suboru.ts` - čo sa zmenilo

## Design Decisions
Ak boli dôležité rozhodnutia:
- **Zvažované:** Aké možnosti existovali
- **Zamietnuté:** Prečo sa niektoré zavrhli  
- **Zvolené:** Prečo sa vybralo toto riešenie

## Key Learnings
- Chyby a ako sa opravili
- Prekvapivé zistenia
- Lepšie prístupy do budúcna

## Remaining Work
Čo zostalo nedokončené, ďalšie kroky.

## Open Questions
Nezodpovedané otázky, veci na preskúmanie.
```

### 4. Voliteľne: Aktualizuj knowledge files

Ak projekt má `docs/knowledge/` priečinok, pridaj tam:
- Nové architektonické rozhodnutia
- Objavené vzory
- Bežné problémy a riešenia

## Príklad výstupu

```markdown
# 2026-01-29 - Refaktoring auth modulu

## Overview
Prepísaný autentifikačný modul na JWT tokeny. Odstránená závislosť na session storage.

## Context
Issue #142 - potreba škálovať na viacero serverov bez zdieľaného session store.

## Čo sa spravilo
- Vytvorený nový JWT service
- Migrované všetky endpointy na bearer tokens
- Pridané refresh token flow

## Súbory zmenené
- `src/auth/jwt.service.ts` - nový JWT service
- `src/auth/middleware.ts` - prepísaný na JWT validáciu
- `src/routes/login.ts` - vracia JWT namiesto session

## Design Decisions
- **Zvažované:** JWT vs session s Redis
- **Zamietnuté:** Redis - zbytočná infraštruktúra pre náš scale
- **Zvolené:** JWT - stateless, jednoduché škálovanie

## Key Learnings
- Refresh tokeny musia byť uložené v DB pre možnosť revokácie
- Access token expiry 15min je dobrý kompromis

## Remaining Work
- [ ] Implementovať token revocation endpoint
- [ ] Pridať rate limiting na refresh
```

## Poznámky

- **Viac detailov je lepšie** - AI nemá pamäť medzi sessions
- Dokumentuj aj **chyby** - budúca session sa z nich poučí
- Ak session pokrývala viacero tém, rozdeľ do sekcií
