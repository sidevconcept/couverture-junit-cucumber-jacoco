# vidocq-app

Le même agenda que `quarkus-app`, porté sur [Vidocq](https://vidocq.dev/) —
un runtime Jakarta EE Core Profile / MicroProfile récent (v0.3.0), zéro
réflexion, JPMS strict. **L'API REST tourne vraiment** (Vauban pour le CDI,
Cassini pour REST, sur le serveur HTTP Chappe) — voir « Lancer le serveur »
ci-dessous.

## Ce qui est fait

- Domaine identique à `quarkus-app` : `ConflictDetector`, `RecurrenceService`,
  `EventService`, `HolidayService`, `QuoteOfTheDayService` — mêmes
  annotations CDI (`@ApplicationScoped`, `@Inject`, `jakarta.enterprise.*`),
  Vauban étant lui aussi un conteneur CDI standard.
- `CalendarResource` : même API REST que `quarkus-app`
  (`POST /api/calendrier/evenements`, `GET .../evenements?date=...`,
  `POST .../evenements/{id}/recurrence`), sur Cassini (Jakarta REST 4.0).
  Différence : le conflit d'horaire est intercepté directement dans la
  méthode (`try/catch` → 409) plutôt que via un `ExceptionMapper` — pas
  vérifié si Cassini honore la découverte automatique des providers
  `@Provider` comme RESTEasy.
- Tests JUnit 5 sur la logique pure (`ConflictDetectorTest`,
  `RecurrenceServiceTest`), `jacoco-maven-plugin` en configuration simple
  (un seul agent — pas de classloader spécial à contourner ici).
- `AgendaApp` (`@VidocqMain`) + `module-info.java` (JPMS strict).
- Packaging `jlink` : `./mvnw -pl vidocq-app package` produit une image
  d'exécution autonome dans `vidocq-app/target/dist/`.

## Lancer le serveur

```bash
./mvnw -pl vidocq-app package -DskipTests
./vidocq-app/target/dist/bin/vidocq-app
# Chappe listener 'default' started on http://localhost:8081/
```

Dans un autre terminal :

```bash
curl -X POST http://localhost:8081/api/calendrier/evenements \
  -H "Content-Type: application/json" \
  -d '{"title":"Atelier Vidocq","start":"2026-09-15T09:00:00","end":"2026-09-15T10:30:00","category":"TRAVAIL"}'

curl "http://localhost:8081/api/calendrier/evenements?date=2026-09-15"
```

Port **8081** (pas 8080) pour pouvoir lancer `quarkus-app` en même temps
pendant la démo.

## Trois pièges rencontrés (et corrigés) pour en arriver là

Vidocq est très jeune (v0.3.0, fin août 2026) ; la doc officielle
(`doc.vidocq.dev`, `vidocq.dev`) bloque le fetch automatisé, tout ce qui
suit a été vérifié en lisant le code source réel du projet (tag `v0.3.0`,
miroir Forgejo `codefloe.com/Vidocq/*`) et en testant empiriquement.

1. **`AgendaApp` doit être exporté.** `io.vidocq.runtime.core.Vidocq`
   instancie la classe `@VidocqMain` par réflexion au démarrage —
   sans `exports com.sidev.vidocqapp;` dans `module-info.java`,
   `IllegalAccessException` immédiate.

2. **Deux modes de lancement, pas interchangeables.** Le trampoline
   `@VidocqMain` (`Vidocq.run(AgendaApp.class, args)`) est documenté pour
   l'usage IDE/dev-mode : il crée un « layer » applicatif dynamique qui
   accorde un accès réflexif large et promeut les `META-INF/services`
   générés en `provides` synthétiques. Pour une **distribution packagée**
   (notre cas, jlink), la javadoc de `Vidocq.java` recommande un point
   d'entrée différent : `java -m io.vidocq.runtime.core/io.vidocq.runtime.core.Vidocq`
   (voir `mainClass` dans `pom.xml`). Ce mode ne crée pas de layer : le
   module est un module nommé « normal », donc il faut déclarer soi-même
   les `opens`/`provides` nécessaires (voir `module-info.java`).

3. **Le plugin manquant qui cause des 404 silencieux partout.** Sans
   `io.vidocq.vauban:vauban-maven-plugin` (goal `generate`, **distinct** de
   `vidocq-runtime-maven-plugin`), le conteneur Vauban ne connaît **aucun**
   bean CDI au démarrage en lancement runtime-first — `CalendarResource`
   n'est jamais reconnu comme une ressource REST. Résultat : toutes les
   routes répondent 404, sans la moindre exception ni log d'erreur. Ce
   plugin scanne les classes du module et écrit `META-INF/vauban-beans.list`
   — la pièce manquante.
   - Effet de bord : ce même plugin scanne *toutes* les dépendances
     résolues (y compris `jakarta.ws.rs-api`) et génère par erreur un
     client-proxy pour `jakarta.ws.rs.core.Application` (la classe de la
     spec elle-même) dans le même package que l'original → conflit de
     « split package » qui fait échouer `jlink`/`jdeps`. Contournement en
     place dans `pom.xml` (exécution `maven-antrun-plugin` qui supprime le
     proxy en trop juste après le scan) — voir le commentaire dans le pom
     pour le détail.

## Ce qui reste à faire

- Tests d'intégration REST : Vidocq n'a pas d'équivalent connu à
  RestAssured/`@QuarkusTest` — leur propre suite utilise **Arquillian**
  (`vidocq-runtime-arquillian` + `arquillian-junit5-container` +
  `shrinkwrap-api`), pas encore tenté ici.
- Aucune intégration Cucumber connue pour Vidocq à ce jour — probablement
  hors de portée pour ce module.
- SonarQube n'est câblé que sur `quarkus-app` pour l'instant.

Voir `PROMPT.md` (racine du dépôt) pour le journal complet de cette
exploration, et `CLAUDE.md` pour les conventions du projet.
