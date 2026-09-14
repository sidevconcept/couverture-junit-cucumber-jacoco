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

---

## 2026-09-10 — Présentation d'une heure, captures d'écran, script comique

**Prompt (verbatim) :**

> il faut que la presentation dure une heure, pourais tu étoffer la
> presentation, s'il est possible pour toi de mettre des captures ecrans
> dans la presentation et m'ecrire une script a suivre, je suis quelqun de
> comique qui aime bien les jeux de mots et me moques des situations
> evidentes

**Décision** : passer le pptx de 11 à 28 slides pour couvrir ~1h (avec deux
blocs de démo live), intégrer de vraies captures d'écran (pas des
maquettes), et écrire `SCRIPT.md` — un script de présentation complet, ton
comique/jeux de mots assumé, avec minutage et deux « soupapes » si le timing
déborde.

**Captures d'écran obtenues** (Chrome headless + Playwright, piloté via
`channel="chrome"` pour réutiliser le Chrome déjà installé, sans
téléchargement de navigateur) :
- Rapport Jacoco : vue d'ensemble + `RecurrenceService.java` avec la branche
  MENSUELLE en rouge (le « money shot » de la conf).
- Terminal : mock HTML stylé du vrai texte produit par
  `coverage-summary.sh` (pas une vraie capture de terminal — plus net,
  recadrable, mêmes données réelles).
- SonarQube : dashboard, mesures par fichier, et le même code source en
  rouge/vert — nécessite Playwright pour gérer la connexion et le
  changement de mot de passe forcé au premier login d'une instance fraîche
  (rencontré : token généré sur une instance dont le mot de passe avait déjà
  été changé lors d'une session précédente → 401 → repartir d'une instance
  propre avec `down -v`).

**Travail réalisé :**
- `presentation/build/` (nouveau) : scripts versionnés
  (`generate_pptx.py`, `sonar_shots.py`, `terminal-mock.html`, `crop.py`) +
  `README.md` avec la procédure complète de régénération. Auparavant le
  script pptx n'existait que dans l'historique de session — corrigé.
- `presentation/screenshots/` (nouveau) : 6 captures réelles, référencées
  par le pptx.
- `presentation/couverture-code-conference.pptx` : réécrit, 28 slides —
  intro/bio/icebreaker/agenda, zoom dédié JUnit et Cucumber (théorie +
  code), comparatif JUnit vs Cucumber, deux blocs Jacoco avec captures, bloc
  SonarQube avec captures, slide comique « excuses classiques », slide
  retour d'expérience (les deux vrais pièges rencontrés pendant ce
  projet), conclusion étoffée.
- `SCRIPT.md` (nouveau) : script complet minuté (~74 min de contenu pour un
  format 1h, avec deux coupes possibles si en retard), texte à dire pour
  chaque slide, cues pour les deux blocs de démo live.
- `CLAUDE.md` et `DESCRIPTION.md` mis à jour (5 livrables au lieu de 4,
  convention sur le ton comique de `SCRIPT.md` à préserver, rappel que les
  captures se périment et doivent être régénérées avant une relecture
  sérieuse).

---

## 2026-09-10 — Restructuration multi-module + module Vidocq

**Prompt (verbatim) :**

> je voudrais essayer de faire une version au lieu de quarkus mettre une
> version avec Vidocq (https://doc.vidocq.dev/vidocq/0.3.0/getting-started).
> pouvons nous mettre la version Quarkus dans un module et créér un module
> pour Vidocq

**Recherche menée sur Vidocq** (la doc officielle bloque le fetch direct —
403 sur `doc.vidocq.dev` et `vidocq.dev` — contournée via le miroir Forgejo
public du projet, `codefloe.com/Vidocq/vidocq`, et Maven Central directement
en `curl`) :
- Vidocq est réel : runtime Jakarta EE Core Profile + MicroProfile,
  « souverain européen », zéro réflexion, **JPMS strict** (nécessite un
  `module-info.java`), Java 25 requis. Dernière version stable publiée sur
  Maven Central : **0.3.0** (tag `v0.3.0` du dépôt, 2026-08-30).
- Coordonnées Maven vérifiées (existent réellement sur Central, pas
  devinées) : `io.vidocq:vidocq-parent:0.3.0`,
  `io.vidocq.runtime:vidocq-runtime-core:0.3.0`,
  `io.vidocq.runtime:vidocq-runtime-maven-plugin:0.3.0`,
  `io.vidocq.runtime.extensions.jakartaee.core:vidocq-runtime-cassini-rest-extension:0.3.0`
  (+ `-codegen`), `io.vidocq.vauban:vauban-core/vauban-indexer/vauban-junit:0.3.0`,
  `io.vidocq.chappe:chappe-api/chappe-core:0.3.0`,
  `io.vidocq.cassini:cassini-api/cassini-core:0.3.0`.
- Un exemple REST officiel existe et a été lu intégralement au tag `v0.3.0`
  (`vidocq-runtime-examples/vidocq-runtime-cassini-rest-example`) : `pom.xml`
  complet + `RestExampleApp.java`, `TodoResource.java`, `module-info.java`.
- Pour les tests, la propre suite de Vidocq (module
  `vidocq-runtime-it-cassini-rest`) utilise **Arquillian**
  (`vidocq-runtime-arquillian` + `arquillian-junit5-container` +
  `shrinkwrap-api`), pas un équivalent de RestAssured/`@QuarkusTest`. Classe
  de test réelle lue (`RestExtensionTest.java`) : déploiement d'une
  `JavaArchive`, `@ArquillianResource URL baseUrl`, appels HTTP bruts via
  `HttpURLConnection`.
- **Aucune trace d'intégration Cucumber** trouvée pour Vidocq, nulle part.
- Le repo `quickstarts` officiel existe mais est vide à ce jour (projet très
  jeune, en construction active).

**Décision (calibrage avec l'utilisateur)** : face à cette complexité réelle
(JPMS strict, Arquillian plus lourd que RestAssured, aucune garantie
empirique de compatibilité Jacoco), deux options ont été proposées — parité
complète tout de suite, ou une phase 1 minimale (logique métier pure, sans
framework, pour valider le montage multi-module + Jacoco avant d'introduire
Vidocq). L'utilisateur a choisi **la phase 1 minimale**.

**Travail réalisé (validé de bout en bout, `./mvnw test` vert sur les deux
modules) :**
- `pom.xml` racine transformé en agrégateur pur (`packaging=pom`,
  `<modules>quarkus-app, vidocq-app</modules>`), sans `<parent>` partagé
  entre modules (pour ne pas coupler BOM Quarkus et coordonnées Vidocq).
- `quarkus-app/` : tout le contenu existant déplacé via `git mv` (préserve
  l'historique), artifactId renommé `couverture-code` → `quarkus-app`.
- `vidocq-app/` (nouveau) : `ConflictDetector` et `RecurrenceService` portés
  sans annotation CDI (classes « nues »), tests JUnit identiques à ceux de
  `quarkus-app` (déjà indépendants du framework), `jacoco-maven-plugin` en
  configuration simple (un seul agent, pas de split — bon contrepoint
  pédagogique avec la complexité du module quarkus-app). JUnit Jupiter
  6.1.3 (dernière version stable vérifiée sur Central). `README.md` détaillant
  la phase 1 et les phases suivantes prévues (CDI/Vauban, REST/Cassini,
  tests probablement Arquillian, pas de Cucumber).
- `scripts/coverage-summary.sh` : chemins mis à jour pour les nouveaux
  répertoires `quarkus-app/target/` et `vidocq-app/target/site/jacoco/` ;
  affiche maintenant les deux modules à la suite.
- `CLAUDE.md` et `DESCRIPTION.md` mis à jour (structure multi-module,
  commandes `-pl`, section Vidocq phase 1, avertissement sur le statut
  "chantier en cours" de `vidocq-app`).

---

## 2026-09-10 — Faire tourner Vidocq pour de vrai (phase 2)

**Prompt (verbatim) :**

> je veux pouvoir voir vidocq en action, est ce qu'on peux faire des modules
> maven pour chaire, quarkus et vidocq

(Les modules existaient déjà depuis la session précédente — compris comme :
faire tourner un vrai serveur REST Vidocq, pas juste des classes nues.)

**Recherche complémentaire** : lecture du code source réel des dépôts
séparés `Vidocq/cassini`, `Vidocq/vauban` (groupIds Maven distincts,
chacun son propre dépôt Forgejo — pas dans `Vidocq/vidocq`), au tag
`v0.3.0`, via l'API Forgejo (`/git/trees/<sha>?recursive=true` pour lister,
`/raw/tag/v0.3.0/<path>` pour le contenu). Fichiers clés lus en entier :
`RestExampleApp.java`, `TodoResource.java`, `module-info.java` (exemple
officiel), `Vidocq.java`, `CassiniExtension.java`,
`ChappeMountConfigExtension.java`, `CassiniMountHandlerProvider.java`,
`VaubanBeanProvider.java`, `GenerateMojo.java` (vauban-maven-plugin),
`VaubanGenerator.java`.

**Trois problèmes réels rencontrés, dans l'ordre, chacun diagnostiqué en
lisant le code source du framework (pas de doc à disposition) :**

1. `IllegalAccessException` au tout premier lancement de l'image jlink —
   `io.vidocq.runtime.core.Vidocq` instancie la classe `@VidocqMain` par
   réflexion ; sans `exports com.sidev.vidocqapp;`, échec immédiat.
2. Une fois corrigé : le serveur démarre, mais **toutes** les routes
   répondent 404, sans la moindre erreur ni log. Cause découverte en lisant
   `Vidocq.java` : le trampoline `@VidocqMain` (utilisé) est documenté pour
   l'usage IDE/dev-mode — il crée un « layer » applicatif dynamique qui
   accorde un accès réflexif large. Pour une distribution packagée
   (jlink), la javadoc recommande un point d'entrée différent
   (`java -m io.vidocq.runtime.core/io.vidocq.runtime.core.Vidocq`, sans
   layer). Changé le `mainClass` du jlink en conséquence — toujours 404.
3. En lisant `VaubanBeanProvider.getResourceClasses()` :
   `bm.getBeans(Object.class, ANY)` — dépend entièrement du `BeanManager`
   Vauban, qui ne connaissait aucun bean. Cause : `vauban-maven-plugin`
   (goal `generate`, **distinct** de `vidocq-runtime-maven-plugin` déjà en
   place) n'était pas déclaré dans le `pom.xml` — sans lui, aucun
   `META-INF/vauban-beans.list` n'est généré pour les classes du module.
   Ajouté → **7 beans CDI découverts**, mais nouvel échec : `jlink`/`jdeps`
   rc=2, "split package" sur `jakarta.ws.rs.core`. Cause : le plugin scanne
   *toutes* les dépendances résolues (y compris `jakarta.ws.rs-api`) et
   génère par erreur un client-proxy pour `jakarta.ws.rs.core.Application`
   (la classe de la spec elle-même) dans son propre package, à l'intérieur
   de notre module → collision avec le module `jakarta.ws.rs`. Contourné
   avec une exécution `maven-antrun-plugin` qui supprime le proxy en trop
   et sa mention dans les fichiers d'index juste après le scan Vauban.

**Résultat validé en direct** (serveur lancé, vrais appels `curl`) :
`POST /api/calendrier/evenements` → `201 Created` avec le JSON attendu,
conflit d'horaire → `409 Conflict` avec le même message que `quarkus-app`,
jour férié (25 décembre) → `holidayGreeting` avec l'emoji. Tests JUnit +
Jacoco toujours verts (26 classes analysées, proxies CDI inclus).

**Travail réalisé :**
- `vidocq-app/pom.xml` : dépendances Vidocq réelles (`vidocq-runtime-core`,
  `vidocq-runtime-cassini-rest-extension` (+ `-codegen`), `chappe-api`,
  `chappe-core`, `vauban-indexer`, `jakarta.ws.rs-api` 4.0.0,
  `jakarta.json.bind-api` 3.0.1, `yasson` 3.0.4 + `parsson` 1.1.7 en
  runtime) ; plugins `vauban-maven-plugin` (generate), `maven-antrun-plugin`
  (contournement split-package, commenté en détail), `vidocq-runtime-maven-plugin`
  (generate + jlink, `mainClass=io.vidocq.runtime.core.Vidocq`).
- `module-info.java` : `requires` complets (jakarta.cdi, jakarta.ws.rs,
  jakarta.json.bind, io.vidocq.runtime.core/spi, cassini, chappe, vauban),
  `exports com.sidev.agenda.model` + `resource.dto` (JSON-B), `exports
  com.sidev.vidocqapp` (réflexion runtime), `provides` explicites pour
  `ResourceAdapter`/`RouteProvider`, `opens resource`/`service` (CDI).
- Domaine : `ConflictDetector`/`RecurrenceService` re-deviennent des beans
  CDI (`@ApplicationScoped`) ; `EventService`, `HolidayService`,
  `QuoteOfTheDayService`, `EventConflictException` portés à l'identique
  depuis `quarkus-app` (mêmes annotations CDI standard).
- `CalendarResource` (nouveau) : même API que `quarkus-app`, conflit
  intercepté par `try/catch` → 409 plutôt que par un `ExceptionMapper`
  (pas vérifié si Cassini découvre les providers `@Provider`
  automatiquement). DTOs avec `@JsonbCreator`/`@JsonbProperty` pour les
  records en entrée (nécessaire pour Yasson en mode module strict — même
  motif que `Todo` dans l'exemple officiel).
- `AgendaApp` (`@VidocqMain`) + `vidocq.properties` (port **8081**, pas
  8080, pour tourner en même temps que `quarkus-app`).
- `vidocq-app/README.md`, `CLAUDE.md`, `DESCRIPTION.md` mis à jour avec les
  trois pièges ci-dessus, en détail, pour ne pas avoir à refaire cette
  recherche si le module est retouché plus tard.

---

## 2026-09-14 — Retour au focus conférence : QR code sur la dernière slide

**Contexte** : entre la session précédente et celle-ci, l'utilisateur a
demandé un module `dashboard-app` (client HTTP + TDD), l'a vu fonctionner
en direct (`montres moi le dashboard`), puis a posé une question de
clarification (`c'est quoi le lien vers le dashboard ?` — pas de lien,
c'était un rapport console, pas un endpoint web, choix fait explicitement
plus tôt). Il a ensuite **rollback et supprimé** ce module de lui-même,
avant cette session — `dashboard-app/`, les entrées `PROMPT.md`
correspondantes et les modifications de `CLAUDE.md`/`DESCRIPTION.md`/
`pom.xml`/`scripts/coverage-summary.sh` qui l'accompagnaient ont disparu du
disque. Traité comme l'état de référence voulu, pas annulé ni recréé.

**Prompt (verbatim) :**

> j'ai rollback et supprimé le dashboard, on va se focaliser sur le talk et
> acomplir le speach, les slides et faire quelque chose de propre. je te
> demande donc de mettre un QR Code sur le dernier slide pour le github :
> https://github.com/sidevconcept/couverture-junit-cucumber-jacoco

**Découverte en cours de route** : le `.pptx` sur disque différait du
dernier commit (taille différente) — inspection avec `python-pptx` :
l'utilisateur avait édité la slide finale **directement dans PowerPoint**
pour y mettre la vraie URL du dépôt et le vrai email, remplaçant les
placeholders `<ton-repo>`/`<ton-email>` du script. Pour ne pas perdre cette
personnalisation à la prochaine régénération (rappel `CLAUDE.md` : ne
jamais éditer le `.pptx` à la main), les mêmes valeurs ont été reportées
**dans le script générateur** avant de régénérer, plutôt que d'éditer le
fichier binaire directement.

**Travail réalisé :**
- `presentation/build/generate_qr.py` (nouveau) : génère
  `presentation/screenshots/qr-github.png` (QR navy sur fond crème,
  cohérent avec la palette du support) à partir de l'URL du dépôt.
- `presentation/build/generate_pptx.py` : slide « Merci » — QR code ajouté
  en haut à droite (via le helper `picture()` déjà existant), ligne de
  contact mise à jour avec la vraie URL/email ; slide « Pour aller plus
  loin » — lien du dépôt synchronisé avec la même URL réelle.
- `presentation/couverture-code-conference.pptx` régénéré (28 slides,
  aucun débordement vérifié).
- `presentation/build/README.md`, `CLAUDE.md` mis à jour (étape de
  génération du QR code, note sur les valeurs en dur dans le script).
