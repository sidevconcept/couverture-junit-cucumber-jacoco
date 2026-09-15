# couverture-code

Support technique d'une conférence sur les tests des applications Java :
un mini agenda d'événements sert de terrain d'exemple pour montrer, lors
d'un build, **un rapport de couverture de code qui révèle quelles classes
ont besoin d'être mieux testées**.

> Ce n'est pas un produit. La logique métier contient volontairement des
> trous de couverture, mesurés et non inventés — voir
> [Convention : les classes volontairement sous-testées](#convention-les-classes-volontairement-sous-testées).

## Démarrage rapide

```bash
./mvnw test                                                # build + tests
./scripts/coverage-summary.sh                               # récap couleur dans le terminal

open quarkus-app/target/jacoco-report-junit/index.html      # couverture JUnit seule
open quarkus-app/target/jacoco-report-cucumber/index.html   # couverture Cucumber seule
open quarkus-app/target/jacoco-report/index.html            # vue globale (union des deux)
```

## Structure du dépôt

`pom.xml` racine en simple agrégateur (`packaging=pom`) avec un seul module,
`quarkus-app` : Quarkus 3.39.2 + JUnit 5 + Cucumber (FR) + Jacoco (rapport
scindé JUnit/Cucumber/global) + SonarQube en bonus.

`./mvnw test` depuis la racine construit et teste le module ; `./mvnw -pl
quarkus-app test` fait la même chose explicitement.

## Comment fonctionne l'application

Un agenda en mémoire (aucune base de données, `ConcurrentHashMap` dans
`EventService`) exposé par une API REST :

```mermaid
flowchart TB
    subgraph API["API REST — /api/calendrier/evenements"]
        P1["POST /\ncréer un événement"]
        G1["GET /?date=...\nvue d'une journée"]
        P2["POST /{id}/recurrence\ngénérer des occurrences récurrentes"]
    end

    CR["CalendarResource"]

    subgraph SERVICES["Couche service"]
        ES["EventService\ncréation + recherche"]
        RS["RecurrenceService\nquotidien / hebdo / mensuel"]
        HS["HolidayService\njours fériés fixes"]
        QS["QuoteOfTheDayService\ncitation du jour"]
    end

    subgraph DOMAINE["Logique pure"]
        CD["ConflictDetector\nchevauchement d'horaires"]
        EV["Event (record)"]
    end

    P1 --> CR
    G1 --> CR
    P2 --> CR

    CR --> ES
    CR --> RS
    CR --> HS
    CR --> QS
    ES --> CD
    ES --> EV
    RS --> EV

    classDef api fill:#183359,color:#EFECE3,stroke:none;
    classDef rest fill:#0B1D36,color:#EFECE3,stroke:none;
    classDef service fill:#EAE6DA,color:#16283E,stroke:none;
    classDef pure fill:#5C8C86,color:#0B1D36,stroke:none;
    class P1,G1,P2 api;
    class CR rest;
    class ES,RS,HS,QS service;
    class CD,EV pure;
```

### Créer un événement : détection de conflit

```mermaid
sequenceDiagram
    participant Client
    participant CalendarResource
    participant EventService
    participant ConflictDetector

    Client->>CalendarResource: POST /evenements
    CalendarResource->>EventService: create(event)
    EventService->>ConflictDetector: isConflicting(existant, nouveau)
    alt chevauchement détecté
        ConflictDetector-->>EventService: true
        EventService-->>CalendarResource: EventConflictException
        CalendarResource-->>Client: 409 Conflict
    else pas de conflit
        ConflictDetector-->>EventService: false
        EventService-->>CalendarResource: Event créé
        CalendarResource-->>Client: 201 Created
    end
```

Ce scénario existe sous deux formes dans le projet : un test **JUnit**
unitaire sur `ConflictDetector` (logique pure, sans dépendance), et un
scénario **Cucumber** de bout en bout qui passe par l'API REST — deux
questions différentes (« la fonction est-elle correcte ? » contre « le
comportement observable est-il le bon ? »).

### Consulter une journée : agrégation de trois sources

```mermaid
sequenceDiagram
    participant Client
    participant CalendarResource
    participant EventService
    participant HolidayService
    participant QuoteOfTheDayService

    Client->>CalendarResource: GET /evenements?date=2026-12-25
    CalendarResource->>EventService: findByDate(date)
    EventService-->>CalendarResource: liste d'événements
    CalendarResource->>HolidayService: greetingFor(date)
    HolidayService-->>CalendarResource: "Joyeux Noël !"
    CalendarResource->>QuoteOfTheDayService: quoteOfTheDay(date)
    QuoteOfTheDayService-->>CalendarResource: citation du jour
    CalendarResource-->>Client: DayViewResponse (événements + jour férié + citation)
```

### Générer des occurrences récurrentes — l'endpoint volontairement non testé

```mermaid
sequenceDiagram
    participant Client
    participant CalendarResource
    participant EventService
    participant RecurrenceService

    Client->>CalendarResource: POST /{id}/recurrence
    CalendarResource->>EventService: findAll() → trouve l'événement modèle
    CalendarResource->>RecurrenceService: generate(modèle, fréquence, occurrences)
    Note over RecurrenceService: QUOTIDIENNE / HEBDOMADAIRE couvertes<br/>MENSUELLE volontairement sous-testée
    RecurrenceService-->>CalendarResource: liste d'événements générés
    CalendarResource->>EventService: create(...) pour chaque occurrence
    CalendarResource-->>Client: liste des événements créés
```

`CalendarResource.createRecurrence` est l'exemple choisi pour la conférence :
une fonctionnalité livrée mais jamais vérifiée bout-en-bout par aucun test
(ni JUnit, ni Cucumber) — voir plus bas.

## De `mvn test` au rapport de couverture

```mermaid
flowchart TB
    A["./mvnw test"] --> J1["Surefire « JUnit »\n(tout sauf le package cucumber)"]
    A --> C1["Surefire « Cucumber »\n(RunCucumberTest)"]

    J1 --> MJ["fusion agent Jacoco + extension quarkus-jacoco\n(jacoco:merge)"]
    C1 --> MC["fusion agent Jacoco + extension quarkus-jacoco\n(jacoco:merge)"]

    MJ --> RJ["jacoco-report-junit/"]
    MC --> RC["jacoco-report-cucumber/"]
    MJ --> RG["jacoco-report/\n(vue globale, union des deux)"]
    MC --> RG

    RJ --> SUM["coverage-summary.sh\n3 tableaux côte à côte"]
    RC --> SUM
    RG --> SUM
    RJ -.-> SONAR["SonarQube\n(import direct des XML)"]
    RC -.-> SONAR

    classDef step fill:#EAE6DA,color:#16283E,stroke:none;
    class A,J1,C1,MJ,MC,RJ,RC,RG,SUM,SONAR step;
```

Diagramme détaillé (avec les fichiers `.exec` intermédiaires) et explication
de la subtilité `quarkus.jacoco.data-file` dans
[`DESCRIPTION.md`](./DESCRIPTION.md#de-mvn-test-au-rapport-de-couverture--scindé-par-type-de-test).

Le constat clé : **JUnit et Cucumber ne couvrent presque pas les mêmes
lignes** — JUnit valide la logique métier en isolation, Cucumber valide le
comportement observable via l'API. Voir le tableau de mesures réelles dans
`DESCRIPTION.md`.

## Convention : les classes volontairement sous-testées

`CalendarResource.createRecurrence`, la branche `MENSUELLE` de
`RecurrenceService`, et le DTO `RecurrenceRequest` sont **intentionnellement**
moins couverts, pour servir d'exemple concret pendant la conférence. Ne pas
"corriger" ces trous sans consulter l'utilisateur — ils font partie du script
de la démo.

## Documentation associée

- [`DESCRIPTION.md`](./DESCRIPTION.md) — description complète du projet,
  modèle de domaine, mesures de couverture réelles, bonus SonarQube.
- [`CLAUDE.md`](./CLAUDE.md) — conventions et instructions du projet.
- [`SCRIPT.md`](./SCRIPT.md) — script de présentation (minutage, texte, cues
  de démo en direct), ton volontairement comique.
- [`presentation/`](./presentation/) — support de la conférence (pptx +
  scripts de génération).
- [`sonarqube/docker-compose.yml`](./sonarqube/docker-compose.yml) —
  SonarQube Community local pour la démo bonus.
