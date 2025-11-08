# GitHub Push Anleitung

## Repository auf GitHub erstellen und pushen

### Option 1: GitHub CLI (gh)

```bash
# GitHub CLI installieren (falls noch nicht vorhanden)
brew install gh

# Login bei GitHub
gh auth login

# Repository erstellen
gh repo create Textverarbeitung --public --source=. --remote=origin --push

# Tag pushen
git push origin v1.0
```

### Option 2: Manuell via GitHub.com

1. Gehe zu https://github.com/new
2. Repository Name: `Textverarbeitung`
3. Beschreibung: `IFB PROFI - KI-gestützte Textverarbeitung mit LM Studio & Qwen 2.5`
4. Public/Private auswählen
5. **NICHT** "Initialize this repository with a README" aktivieren
6. Repository erstellen

Dann im Terminal:

```bash
cd /Users/patrick.zackert/projects/masterprojekt

# Remote hinzufügen (USERNAME durch deinen GitHub Username ersetzen)
git remote add origin https://github.com/USERNAME/Textverarbeitung.git

# Pushen
git push -u origin main

# Tag pushen
git push origin v1.0
```

### Verifizierung

Nach dem Push solltest du auf GitHub sehen:
- ✅ Alle Dateien und Ordner
- ✅ Tag v1.0 unter "Releases"
- ✅ README.md wird auf der Hauptseite angezeigt

### Remote URL prüfen

```bash
git remote -v
```

Sollte ausgeben:
```
origin  https://github.com/USERNAME/Textverarbeitung.git (fetch)
origin  https://github.com/USERNAME/Textverarbeitung.git (push)
```
