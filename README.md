# Rabbio Skills

Kolekcia [Cursor AI](https://cursor.com) skills od tímu [Rabbio Digital](https://rabbio.digital).

Skills rozširujú schopnosti AI agenta v Cursor IDE o špecializované workflow, znalosti a postupy.

## Dostupné skills

| Skill | Popis |
|-------|-------|
| [web-hosting-migration](./web-hosting-migration/) | Migrácia webov medzi hostingami (PHP, Laravel, WordPress, static) |
| [session-end](./session-end/) | Vytvára development log záznam na konci pracovnej session |

## Inštalácia

### Manuálna inštalácia (1 skill)

Skopíruj priečinok skillu do `~/.cursor/skills/`:

```bash
# Naklonuj repo
git clone https://github.com/rabbiodigital/rabbio-skills.git /tmp/rabbio-skills

# Skopíruj konkrétny skill
cp -r /tmp/rabbio-skills/web-hosting-migration ~/.cursor/skills/

# Vyčisti
rm -rf /tmp/rabbio-skills
```

### Inštalácia všetkých skills

```bash
git clone https://github.com/rabbiodigital/rabbio-skills.git /tmp/rabbio-skills
cp -r /tmp/rabbio-skills/*/ ~/.cursor/skills/
rm -rf /tmp/rabbio-skills
```

### Symlink (pre automatické aktualizácie)

```bash
git clone https://github.com/rabbiodigital/rabbio-skills.git ~/rabbio-skills

# Symlink konkrétneho skillu
ln -s ~/rabbio-skills/web-hosting-migration ~/.cursor/skills/web-hosting-migration
ln -s ~/rabbio-skills/session-end ~/.cursor/skills/session-end
```

## Štruktúra skillu

Každý skill je priečinok s `SKILL.md` súborom:

```
skill-name/
├── SKILL.md              # Hlavné inštrukcie (povinné)
├── reference.md          # Doplnkové info (voliteľné)
└── troubleshooting.md    # Riešenie problémov (voliteľné)
```

## Prispievanie

1. Forkni repo
2. Vytvor nový priečinok pre skill
3. Pridaj `SKILL.md` s YAML frontmatter (`name`, `description`)
4. Pošli Pull Request

## Licencia

MIT
