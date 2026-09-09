# Journal des prompts

Historique chronologique de tous les prompts utilisés avec Claude Code pour
construire ce projet. Nouvelle session de travail = nouvelle entrée ajoutée
**à la suite** (ne jamais réécrire les entrées existantes).

---

## 2026-09-09 — Fondation du projet

**Contexte** : mise en place initiale — choix du projet de démo, dépendances
Quarkus/JUnit/Cucumber/Jacoco, script de récap de couverture, et documentation
(`CLAUDE.md`, `PROMPT.md`, `DESCRIPTION.md`, présentation PowerPoint).

**Prompt initial (verbatim) :**

> Je dois faire une conférance prochainement sur le sujet des test des
> applications Java. Le stack téchnique est Quarkus, JUnit, Cucmber et
> Jaccoco. Le but de la conf est presenter la stack afin de montrer lors des
> builds la couverture de code et montrer quelles classes ont besoin d'etre
> couvertes. le but de l'exercice tout de suite est de créér la foncdation
> qui va permettre de réaliser le necessaire pour faire une demonstration
> lors de la conference. on doit avoir un projet (propose moi quelques idées
> de projets SIMPLES et facile a réaliser). ensuite il faut importer les
> dependance pour créer la stack technique qui permettre de réaliser le
> build afin de mettre en evidence la couverture de code. ce que nous
> voulons est que lors des builds avec tests on aimerai avoir un espese de
> rapport de recap de la couverture de code. apres ceci on va commencer la
> documentation. prepares le CLAUDE.md avec les besoins suivants. tous les
> prompts doivent etre logés dans un PROMPT.md, un DESCRIPTION.md qui decris
> le projet avec diagrams Mermaid, et pour finir un powerpoint de
> presentation (sans le AI Slop, je veux quelque chose d'original avec des
> couleurs bleu marines et des couleurs douces sur les yeux)

**Clarification (choix du projet)** : Claude a proposé 4 idées de projets
simples (panier e-commerce, éligibilité de prêt, gestionnaire de tâches,
gestionnaire de bibliothèque). Réponse de l'utilisateur :

> (aucune option choisie) avec un calendier et quelques trucs sympas

→ Décision retenue : un **agenda / planificateur d'événements** combinant un
calendrier (détection de conflits, récurrences, jours fériés) et une touche
« sympa » (citation du jour), qui offre naturellement plusieurs branches de
logique métier à mettre en évidence dans le rapport Jacoco.

**Travail réalisé dans cette session :**
- Domaine `com.sidev.agenda` (modèle `Event`, services `ConflictDetector`,
  `EventService`, `RecurrenceService`, `HolidayService`,
  `QuoteOfTheDayService`, ressource REST `CalendarResource`).
- Dépendances ajoutées au `pom.xml` : `quarkus-rest-jackson`,
  `io.quarkiverse.cucumber:quarkus-cucumber` (1.3.0), `io.quarkus:quarkus-jacoco`,
  plugin `jacoco-maven-plugin` (0.8.14, compatible Java 25).
- Tests JUnit (`ConflictDetectorTest`, `RecurrenceServiceTest`,
  `EventServiceTest`) et scénarios Cucumber en français
  (`gestion_evenements.feature` + `EventStepDefinitions`).
- Script `scripts/coverage-summary.sh` : récap coloré de la couverture dans
  le terminal après `./mvnw test`.
- Build validé de bout en bout (`./mvnw test` : 17 tests, 0 échec, rapport
  Jacoco généré dans `target/jacoco-report/`).
- Documentation : `CLAUDE.md`, `PROMPT.md` (ce fichier), `DESCRIPTION.md`
  (diagrammes Mermaid), présentation `presentation/couverture-code-conference.pptx`
  (palette bleu marine / tons doux, généré via `python-pptx`).

---

## 2026-09-09 — Scinder la couverture par type de test

**Prompt (verbatim) :**

> ce qui serait genial dans le rapport est de cinder la couverture par le
> test unitaire (Junit) et les tests par cucumber qui sont plus tests
> integrations. est ce que c'est possible ?

**Décision** : oui — refonte du `pom.xml` pour que `./mvnw test` produise
trois rapports Jacoco au lieu d'un seul : `jacoco-report-junit/`,
`jacoco-report-cucumber/`, `jacoco-report/` (global).

**Difficulté rencontrée et corrigée** : un premier découpage naïf (deux
exécutions Surefire, deux agents `-javaagent` Jacoco) donnait des rapports
incohérents — la plupart des classes remontaient à 0 % dans les deux vues.
Cause : l'extension `io.quarkus:quarkus-jacoco` mesure séparément, dans son
propre fichier `.exec`, tout le code qui s'exécute dans le
`QuarkusClassLoader` (CDI, REST) — indépendamment de l'agent du
`jacoco-maven-plugin`. Il fallait pointer `quarkus.jacoco.data-file` vers un
fichier distinct par exécution Surefire, puis fusionner (`jacoco:merge`) les
deux sources avant de générer chaque rapport. Voir `DESCRIPTION.md` pour le
diagramme du flux corrigé.

**Résultat obtenu** (mesures réelles, 17 tests) : JUnit et Cucumber couvrent
des lignes presque disjointes — ex. `CalendarResource` 0 % en JUnit / 58 % en
Cucumber, `RecurrenceService` 78 % en JUnit / 4 % en Cucumber. Bon matériel
de conférence pour illustrer la complémentarité des deux types de test.

**Travail réalisé :**
- `pom.xml` : deux exécutions Surefire (JUnit / Cucumber), chacune avec son
  propre agent Jacoco + son propre `quarkus.jacoco.data-file` ; exécutions
  `jacoco:merge` et `jacoco:report` pour produire les trois rapports.
- `scripts/coverage-summary.sh` : réécrit pour afficher les trois tableaux
  (JUnit / Cucumber / global) à la suite.
- `DESCRIPTION.md` : diagramme de flux et tableau de mesures mis à jour pour
  refléter le découpage par type de test.
- `presentation/couverture-code-conference.pptx` : la slide Jacoco montre
  désormais deux barres (JUnit en or, Cucumber en bleu-teal) par classe, sur
  les mêmes données réelles.

---

## 2026-09-09 — Intégration SonarQube

**Prompts (verbatim, deux messages)** :

> est ce qu'il y a une integration possible dans un soar pour ces données de
> sortie jacoco

Réponse : clarification que SOAR (orchestration d'incidents de sécurité)
n'a pas de connecteur natif pour de la donnée de couverture — proposition de
SonarQube/DefectDojo comme pistes plus pertinentes, et question de
clarification sur l'intention.

> je voulais dire SONAR, pour la couverture

**Décision** : ajouter `sonar-maven-plugin` au `pom.xml` (sans exécution
liée au lifecycle) configuré pour importer directement les deux rapports
Jacoco XML (`jacoco-report-junit/jacoco.xml` et
`jacoco-report-cucumber/jacoco.xml`) — Sonar recalcule lui-même l'union,
pas besoin de lui donner le rapport déjà fusionné.

**Travail réalisé et validé de bout en bout (Docker disponible en local)** :
- `pom.xml` : plugin `sonar-maven-plugin` (5.8.0.7211) + propriétés
  `sonar.projectKey`, `sonar.coverage.jacoco.xmlReportPaths`,
  `sonar.junit.reportPaths`.
- `sonarqube/docker-compose.yml` : SonarQube Community local pour la démo
  (pas de compte SonarCloud requis).
- Validation réelle : conteneur lancé, jeton généré via l'API, analyse
  exécutée (`./mvnw test sonar:sonar -Dsonar.token=...`) — succès, 77,7 % de
  couverture globale remontée dans Sonar, cohérent avec le rapport
  `jacoco-report` fusionné. Conteneur arrêté après validation
  (`docker compose down`, volumes conservés).
- `CLAUDE.md` et `DESCRIPTION.md` mis à jour (section SonarQube, diagramme
  Mermaid du flux, avertissement à ne jamais committer un jeton Sonar).

**Prompt de suivi (verbatim) :**

> comment je valide sur sonar ?

Réponse : parcours pas-à-pas (démarrer le conteneur, générer un jeton,
lancer `sonar:sonar`, où regarder dans le dashboard — Overview, Measures →
Coverage, vue ligne-par-ligne d'une classe — puis arrêter proprement).

**Prompt de suivi (verbatim) :**

> mets a jour la documentation, les md et powerpoint

**Travail réalisé :**
- `DESCRIPTION.md` : ajout du mode d'emploi complet de validation SonarQube
  (commandes + où regarder dans le dashboard) et mise à jour de la liste des
  fichiers associés (`sonarqube/docker-compose.yml`, pptx passé à 11 slides).
- `CLAUDE.md` : ajout de la même procédure de validation, et rappel de
  repartir d'une instance Sonar propre (`down -v`) avant la vraie
  conférence.
- `presentation/couverture-code-conference.pptx` : nouvelle slide 9 « Bonus
  — Et dans un vrai dashboard ? » (chiffres réels mesurés : 77,7 % global /
  82 % lignes / 65 % branches, commandes docker compose + sonar:sonar) ;
  « À retenir » et « Merci » décalées en 10 et 11.
