# Régénérer la présentation

Le pptx et les captures d'écran sont générés par script — ne pas éditer
`couverture-code-conference.pptx` à la main.

## Mise en place (une fois)

```bash
python3 -m venv .venv
./.venv/bin/pip install python-pptx Pillow playwright
```

`playwright` pilote le Google Chrome déjà installé sur la machine
(`channel="chrome"`) — pas de téléchargement de navigateur supplémentaire.

## Régénérer les captures d'écran

```bash
# 1. Rapport Jacoco (depuis la racine du projet)
./mvnw test

# 2. Captures Jacoco (fichiers statiques, Chrome headless suffit)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --window-size=1600,1100 \
  --screenshot=presentation/screenshots/jacoco-overview.png \
  "file://$(pwd)/target/jacoco-report/index.html"
"$CHROME" --headless=new --window-size=1600,1400 \
  --screenshot=presentation/screenshots/jacoco-recurrence-source.png \
  "file://$(pwd)/target/jacoco-report/com.sidev.agenda.service/RecurrenceService.java.html"
./.venv/bin/python presentation/build/crop.py presentation/screenshots/jacoco-*.png

# 3. Mock terminal (coverage-summary.sh stylé, pas de vraie capture de terminal)
"$CHROME" --headless=new --window-size=1300,760 \
  --screenshot=presentation/screenshots/terminal-mock.png \
  "file://$(pwd)/presentation/build/terminal-mock.html"
# recadrer manuellement si besoin (voir crop.py pour un fond non-blanc)

# 4. SonarQube (nécessite Docker) : voir CLAUDE.md pour up/down -v, puis
docker compose -f sonarqube/docker-compose.yml up -d
# générer un token, lancer ./mvnw test sonar:sonar -Dsonar.token=...
./.venv/bin/python presentation/build/sonar_shots.py
docker compose -f sonarqube/docker-compose.yml down
```

`sonar_shots.py` gère lui-même la connexion (admin/admin) et le changement
de mot de passe forcé au premier login d'une instance fraîche — sur une
instance déjà initialisée, changer le mot de passe utilisé dans le script.

## Régénérer le pptx

```bash
./.venv/bin/python presentation/build/generate_pptx.py
```

Écrit directement dans `presentation/couverture-code-conference.pptx`.
