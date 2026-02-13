# Šablóna pre projektový rule

Skopíruj obsah nižšie do `.cursor/rules/session-docs.mdc` v tvojom projekte.

---

```markdown
---
description: Konfigurácia session dokumentácie pre tento projekt
globs:
alwaysApply: true
---

# Session Documentation - Projektová konfigurácia

## Umiestnenie súborov

- **Dev logs:** `docs/devlogs/`
- **Knowledge base:** `docs/knowledge/`

## Konvencie pre tento projekt

### Názvy dev log súborov
Formát: `YYYY-MM-DD_kratky-popis.md`
Príklad: `2026-01-29_auth-refactor.md`

### Knowledge súbory
- `docs/knowledge/architecture.md` - Architektonické rozhodnutia
- `docs/knowledge/patterns.md` - Osvedčené vzory v projekte
- `docs/knowledge/pitfalls.md` - Bežné problémy a riešenia
- `docs/knowledge/api.md` - API konvencie (ak relevantné)

### Čo dokumentovať v dev logoch
- Každú session kde sa robili zmeny v kóde
- Dôležité rozhodnutia a ich odôvodnenie
- Chyby a ako sa vyriešili
- Nedokončené úlohy

### Čo aktualizovať v knowledge
- Nové architektonické vzory
- Objavené edge cases
- Integrácie s externými službami
- Performance optimalizácie

## Jazyk
Dokumentáciu píš v slovenčine (alebo: angličtine).
```

---

## Ako použiť

1. V projekte vytvor priečinok `.cursor/rules/` (ak neexistuje)
2. Vytvor súbor `session-docs.mdc`
3. Vlož obsah z bloku vyššie
4. Uprav podľa potrieb projektu (cesty, jazyk, konvencie)

## Poznámka

Projektový rule sa automaticky načíta pri práci v danom projekte a doplní globálny skill o špecifické informácie pre projekt.
