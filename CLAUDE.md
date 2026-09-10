# couverture-code — instructions du projet

## Contexte

Ce dépôt est le support technique d'une conférence sur les tests des applications
Java. La stack de démonstration est **Quarkus + JUnit + Cucumber + Jacoco**, et
l'objectif de la conférence est de montrer, lors d'un build, un rapport de
couverture de code qui met en évidence **quelles classes ont besoin d'être
mieux couvertes**.

Le projet de démo est un agenda/planificateur d'événements simple (voir
`DESCRIPTION.md`). Il n'a pas vocation à évoluer en produit réel : sa seule
raison d'être est de fournir un terrain d'exemple crédible pour parler de
couverture de tests.

## Stack technique

- **Quarkus** (`3.39.2`) — framework applicatif, packaging `quarkus-rest` +
  `quarkus-rest-jackson`.
- **JUnit 5** (via l'extension `quarkus-junit`) — tests unitaires, notamment
  sur les classes de logique métier pure (`ConflictDetector`,
  `RecurrenceService`).
- **Cucumber** (`io.quarkiverse.cucumber:quarkus-cucumber`) — tests BDD en
  français, exécutés contre l'API REST via RestAssured. Runner :
  `src/test/java/com/sidev/cucumber/RunCucumberTest.java`, features dans
  `src/test/resources/features/`.
- **Jacoco** (`io.quarkus:quarkus-jacoco` + `jacoco-maven-plugin` `0.8.14`,
  requis pour Java 25) — instrumente `mvn test` (JUnit + Cucumber confondus)
  et produit le rapport dans `target/jacoco-report/`.

## Build & couverture

- `./mvnw test` : lance deux exécutions Surefire distinctes — une pour les
  classes JUnit « pures » (tout sauf `com.sidev.cucumber`), une pour
  `RunCucumberTest` — et génère automatiquement **trois** rapports Jacoco :
  - `target/jacoco-report-junit/` — couverture JUnit seule
  - `target/jacoco-report-cucumber/` — couverture Cucumber seule
  - `target/jacoco-report/` — vue globale (union des deux)

  C'est LA commande de démo — pas besoin de `mvn verify` ni de profil
  particulier.
- `./scripts/coverage-summary.sh` : affiche les trois récapitulatifs colorés
  (rouge / orange / vert) l'un après l'autre dans le terminal — pensé pour
  être montré en direct pendant la conférence, en complément des rapports
  HTML.

**Piège à connaître si on retouche le `pom.xml` autour de Jacoco** :
l'extension `io.quarkus:quarkus-jacoco` mesure, **séparément** de l'agent
`-javaagent` du `jacoco-maven-plugin`, tout le code qui s'exécute dans le
`QuarkusClassLoader` (un bean CDI appelé depuis un `@QuarkusTest` ou un
scénario Cucumber). Elle écrit dans le fichier pointé par la propriété
système `quarkus.jacoco.data-file` (un chemin distinct par exécution
Surefire, sinon les deux exécutions écrasent le même fichier par défaut).
Il faut donc fusionner (`jacoco:merge`) les deux `.exec` — celui de l'agent
et celui de l'extension — avant de générer chaque rapport (`jacoco:report`).
Voir le détail dans `DESCRIPTION.md` (diagramme du flux de build) et les
commentaires du `pom.xml`.

Ne pas ajouter de règle `jacoco:check` qui ferait échouer le build sur un
seuil de couverture : le but de ce projet est de **montrer** les trous de
couverture, pas de bloquer un build dessus.

## SonarQube (optionnel, pour aller plus loin que le terminal)

Le `pom.xml` embarque `sonar-maven-plugin` (aucune `<execution>` liée au
lifecycle — il ne se déclenche jamais tout seul). SonarQube importe
directement les deux rapports Jacoco XML (`sonar.coverage.jacoco.xmlReportPaths`
pointe vers `jacoco-report-junit/jacoco.xml` **et**
`jacoco-report-cucumber/jacoco.xml`) et recalcule lui-même la couverture
globale par union des deux — donc pas besoin de lui donner le rapport déjà
fusionné.

- `docker compose -f sonarqube/docker-compose.yml up -d` : lance un
  SonarQube Community local (aucun compte SonarCloud requis, pas de
  dépendance réseau pendant la démo une fois l'image récupérée).
  `SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true` évite d'avoir à toucher au
  `vm.max_map_count` de l'hôte.
- Générer un jeton depuis `http://localhost:9000` (identifiants par défaut
  `admin` / `admin`, changement de mot de passe imposé au premier login) ou
  via l'API : `curl -u admin:admin -X POST "http://localhost:9000/api/user_tokens/generate" -d "name=demo"`.
- Lancer l'analyse : `./mvnw test sonar:sonar -Dsonar.token=<le_jeton>`.
- Valider : `http://localhost:9000/dashboard?id=couverture-code` — onglet
  **Overview** pour le % global, **Measures → Coverage** pour le détail par
  classe, cliquer une classe pour voir les lignes couvertes/non couvertes en
  surbrillance dans le code source.
- **Ne jamais committer un jeton Sonar** dans le pom ou un fichier versionné
  — toujours le passer en `-D` ou variable d'environnement (`SONAR_TOKEN`).
- Avant la vraie conférence, repartir d'une instance propre avec
  `docker compose -f sonarqube/docker-compose.yml down -v` puis relancer
  `up -d`, pour ne pas montrer l'historique d'analyses de cette session.

Validé de bout en bout dans cette session : couverture globale mesurée par
Sonar = 77,7 % (82 % en lignes, 65 % en branches), cohérent avec les chiffres
du rapport `jacoco-report` global.

## Convention : les classes volontairement sous-testées

Certaines classes/méthodes sont **intentionnellement** moins couvertes que
les autres, pour servir d'exemple concret pendant la conférence
(`CalendarResource.createRecurrence`, la branche `MENSUELLE` de
`RecurrenceService`, le DTO `RecurrenceRequest`). Ne pas "corriger" ces trous
de couverture sans consulter l'utilisateur — ils font partie du script de la
démo. Le détail exact et son origine sont documentés dans `DESCRIPTION.md`.

## Documentation attendue dans ce dépôt

Cinq livrables doivent rester à jour au fur et à mesure des évolutions :

1. **`CLAUDE.md`** (ce fichier) — les instructions et conventions du projet.
2. **`PROMPT.md`** — le journal de **tous** les prompts utilisés pour
   construire ce projet avec Claude Code, dans l'ordre chronologique. Chaque
   nouvelle session de travail doit y ajouter une entrée (date + prompt
   utilisateur, résumé succinct si le prompt est long). Ne jamais réécrire
   l'historique existant, seulement ajouter à la suite.
3. **`DESCRIPTION.md`** — description du projet (objectif, architecture,
   choix techniques) illustrée par des **diagrammes Mermaid** (architecture,
   séquence, flux de build/couverture). À tenir à jour si l'architecture du
   projet de démo change.
4. **`SCRIPT.md`** — le script de présentation à suivre pendant la
   conférence (minutage, texte à dire, cues pour les démos en direct). Ton
   volontairement comique (jeux de mots, auto-dérision sur les situations
   "évidentes" du métier) — c'est un choix délibéré de l'utilisateur, ne pas
   le "assagir" sans demande explicite. À tenir à jour si l'ordre ou le
   contenu des slides change (le minutage notamment).
5. **`presentation/couverture-code-conference.pptx`** — le support de
   présentation pour la conférence (28 slides pour ~1h, avec captures d'écran
   réelles du projet — pas des maquettes). Généré via `python-pptx` : le
   script source et tout ce qui produit les captures d'écran sont versionnés
   dans `presentation/build/` (voir `presentation/build/README.md` pour la
   procédure complète de régénération). **Ne jamais éditer le `.pptx`
   directement** — toujours régénérer via
   `presentation/build/generate_pptx.py` si un changement structurel est
   nécessaire, pour que le fichier reste reproductible. Contraintes de
   design à respecter strictement :
   - palette **bleu marine** + tons **doux pour les yeux** (fond crème/écru,
     pas de blanc pur ni de noir pur, accents or/terracotta/sauge en petites
     touches) ;
   - **pas d'"AI slop"** : pas d'icônes stock génériques, pas de dégradés
     criards, pas de robot/IA en illustration, pas de listes à puces
     génériques — préférer des diagrammes construits à partir de vraies
     formes géométriques, des captures d'écran réelles, et des données
     réelles du projet (ex. les pourcentages de couverture mesurés, pas des
     chiffres inventés) ;
   - contenu original et spécifique à ce projet, pas de texte de remplissage
     générique.

Les captures d'écran vivent dans `presentation/screenshots/` (Jacoco,
SonarQube, un mock de terminal stylé pour `coverage-summary.sh`) et sont
régénérées via `presentation/build/` — elles se périment vite (les chiffres
de couverture changent avec le code), les regénérer avant chaque relecture
sérieuse du support plutôt que de faire confiance à d'anciennes captures.

## Style de code

- Domaine dans `com.sidev.agenda` (`model`, `service`, `resource`,
  `resource.dto`), tests Cucumber dans `com.sidev.cucumber`.
- Code et commentaires en français (contexte de la conférence), noms
  techniques (classes, méthodes) en anglais/français mixte comme déjà en
  place — rester cohérent avec l'existant plutôt que d'introduire une
  nouvelle convention.
- Pas de base de données : le `EventService` utilise un `ConcurrentHashMap`
  en mémoire. Ne pas ajouter de persistance sauf demande explicite — ce
  n'est pas le sujet de la démo.
