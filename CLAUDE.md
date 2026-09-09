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

- `./mvnw test` : lance JUnit + Cucumber puis génère automatiquement le
  rapport Jacoco (HTML + XML + CSV) dans `target/jacoco-report/`. C'est LA
  commande de démo — pas besoin de `mvn verify` ni de profil particulier.
- `./scripts/coverage-summary.sh` : lit `target/jacoco-report/jacoco.csv` et
  affiche un récapitulatif coloré (rouge / orange / vert) de la couverture
  par classe directement dans le terminal — pensé pour être montré en direct
  pendant la conférence, en complément du rapport HTML.
- `target/jacoco-report/index.html` : le rapport détaillé, ligne par ligne.

Ne pas ajouter de règle `jacoco:check` qui ferait échouer le build sur un
seuil de couverture : le but de ce projet est de **montrer** les trous de
couverture, pas de bloquer un build dessus.

## Convention : les classes volontairement sous-testées

Certaines classes/méthodes sont **intentionnellement** moins couvertes que
les autres, pour servir d'exemple concret pendant la conférence
(`CalendarResource.createRecurrence`, la branche `MENSUELLE` de
`RecurrenceService`, le DTO `RecurrenceRequest`). Ne pas "corriger" ces trous
de couverture sans consulter l'utilisateur — ils font partie du script de la
démo. Le détail exact et son origine sont documentés dans `DESCRIPTION.md`.

## Documentation attendue dans ce dépôt

Quatre livrables doivent rester à jour au fur et à mesure des évolutions :

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
4. **`presentation/couverture-code-conference.pptx`** — le support de
   présentation pour la conférence, généré via `python-pptx` (script source :
   voir historique de session ; à régénérer plutôt qu'à éditer les slides à
   la main si des changements structurels sont nécessaires). Contraintes de
   design à respecter strictement :
   - palette **bleu marine** + tons **doux pour les yeux** (fond crème/écru,
     pas de blanc pur ni de noir pur, accents or/terracotta/sauge en petites
     touches) ;
   - **pas d'"AI slop"** : pas d'icônes stock génériques, pas de dégradés
     criards, pas de robot/IA en illustration, pas de listes à puces
     génériques — préférer des diagrammes construits à partir de vraies
     formes géométriques et des données réelles du projet (ex. les
     pourcentages de couverture mesurés, pas des chiffres inventés) ;
   - contenu original et spécifique à ce projet, pas de texte de remplissage
     générique.

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
