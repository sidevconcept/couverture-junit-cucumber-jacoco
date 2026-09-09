# couverture-code — Description du projet

## Objectif

Support de démonstration pour une conférence sur les tests des applications
Java. La stack **Quarkus + JUnit + Cucumber + Jacoco** est illustrée par un
projet volontairement simple — un agenda d'événements — afin de montrer,
lors d'un build (`./mvnw test`), un **rapport de couverture de code** qui met
en évidence quelles classes (et quelles branches) ont besoin d'être mieux
testées.

Ce n'est pas un produit : c'est un terrain d'exemple. La logique métier
contient volontairement des branches et des chemins de code non couverts,
pour donner à la conférence un exemple concret et mesuré (pas inventé) de
« trou de couverture ».

## Le projet de démo : un agenda malin

Une API REST Quarkus qui permet de :

- créer un événement et **refuser automatiquement** ceux qui chevauchent un
  événement déjà planifié (`ConflictDetector`) ;
- consulter les événements d'une journée, avec en bonus le signalement d'un
  **jour férié** (`HolidayService`) et une **citation du jour** sur les
  tests (`QuoteOfTheDayService`) ;
- générer des **occurrences récurrentes** d'un événement (quotidien,
  hebdomadaire, mensuel) via `RecurrenceService`.

Aucune base de données : le stockage est un simple `ConcurrentHashMap` en
mémoire (`EventService`). Le sujet du jour est la couverture de tests, pas la
persistance.

## Architecture

```mermaid
flowchart TB
    subgraph REST["Couche REST"]
        CR["CalendarResource<br/>POST /evenements · GET /evenements · POST /evenements/id/recurrence"]
    end

    subgraph SERVICES["Couche service"]
        ES["EventService<br/>création + recherche"]
        RS["RecurrenceService<br/>quotidien / hebdo / mensuel"]
        HS["HolidayService<br/>jours fériés fixes"]
        QS["QuoteOfTheDayService<br/>citation du jour"]
    end

    subgraph DOMAINE["Logique pure"]
        CD["ConflictDetector<br/>chevauchement d'horaires"]
        EV["Event (record)"]
    end

    CR --> ES
    CR --> RS
    CR --> HS
    CR --> QS
    ES --> CD
    ES --> EV
    RS --> EV

    classDef rest fill:#0B1D36,color:#EFECE3,stroke:none;
    classDef service fill:#183359,color:#EFECE3,stroke:none;
    classDef pure fill:#5C8C86,color:#0B1D36,stroke:none;
    class CR rest;
    class ES,RS,HS,QS service;
    class CD,EV pure;
```

## Modèle de domaine

```mermaid
classDiagram
    class Event {
        +UUID id
        +String title
        +LocalDateTime start
        +LocalDateTime end
        +EventCategory category
        +withId(UUID) Event
    }

    class EventCategory {
        <<enumeration>>
        TRAVAIL
        PERSONNEL
        FERIE
    }

    class RecurrenceFrequency {
        <<enumeration>>
        QUOTIDIENNE
        HEBDOMADAIRE
        MENSUELLE
    }

    class ConflictDetector {
        +isConflicting(Event, Event) boolean
    }

    class EventService {
        -Map~UUID, Event~ events
        +create(Event) Event
        +findByDate(LocalDate) List~Event~
        +findAll() List~Event~
        +delete(UUID) boolean
    }

    class RecurrenceService {
        +generate(Event, RecurrenceFrequency, int) List~Event~
    }

    class EventConflictException {
        +String message
    }

    Event --> EventCategory
    EventService --> ConflictDetector : utilise
    EventService --> EventConflictException : lève
    EventService --> Event
    RecurrenceService --> RecurrenceFrequency
    RecurrenceService --> Event
```

## Scénario clé : refus d'un événement en conflit

```mermaid
sequenceDiagram
    participant Client
    participant CalendarResource
    participant EventService
    participant ConflictDetector

    Client->>CalendarResource: POST /api/calendrier/evenements
    CalendarResource->>EventService: create(event)
    EventService->>ConflictDetector: isConflicting(existant, nouveau)
    ConflictDetector-->>EventService: true (chevauchement)
    EventService-->>CalendarResource: EventConflictException
    CalendarResource-->>Client: 409 Conflict
```

Ce même scénario existe sous deux formes dans le projet : un test **JUnit**
unitaire sur `ConflictDetector` (logique pure, aucune dépendance), et un
scénario **Cucumber** de bout en bout qui passe par l'API REST — les deux
répondent à des questions différentes (« la fonction est-elle correcte ? »
contre « le comportement observable est-il le bon ? »).

## De `mvn test` au rapport de couverture — scindé par type de test

`./mvnw test` lance **deux exécutions Surefire distinctes** (une pour les
classes JUnit, une pour `RunCucumberTest`), chacune avec son propre agent
Jacoco. Une subtilité à connaître : le code qui tourne à travers CDI/Quarkus
(un bean injecté dans un `@QuarkusTest`, ou tout l'aller-retour REST d'un
scénario Cucumber) est mesuré **séparément** par l'extension
`quarkus-jacoco`, pas par l'agent `-javaagent` du `jacoco-maven-plugin` — les
deux sources doivent donc être fusionnées avant de générer un rapport
exploitable pour chaque type de test.

```mermaid
flowchart TB
    A["./mvnw test"] --> J1["Exécution Surefire « JUnit »\n(exclut le package cucumber)"]
    A --> C1["Exécution Surefire « Cucumber »\n(RunCucumberTest uniquement)"]

    J1 --> JA["Agent Jacoco (-javaagent)\njacoco-junit.exec\ncode hors QuarkusClassLoader"]
    J1 --> JQ["Extension quarkus-jacoco\njacoco-junit-quarkus.exec\ncode CDI/Quarkus"]
    C1 --> CA["Agent Jacoco (-javaagent)\njacoco-cucumber.exec"]
    C1 --> CQ["Extension quarkus-jacoco\njacoco-cucumber-quarkus.exec"]

    JA --> MJ["jacoco:merge\njacoco-junit-all.exec"]
    JQ --> MJ
    CA --> MC["jacoco:merge\njacoco-cucumber-all.exec"]
    CQ --> MC

    MJ --> RJ["target/jacoco-report-junit/"]
    MC --> RC["target/jacoco-report-cucumber/"]
    MJ --> MG["jacoco:merge\njacoco-merged.exec"]
    MC --> MG
    MG --> RG["target/jacoco-report/\n(vue globale)"]

    RJ --> SUM["scripts/coverage-summary.sh\n3 tableaux côte à côte"]
    RC --> SUM
    RG --> SUM

    classDef step fill:#EAE6DA,color:#16283E,stroke:none;
    class A,J1,C1,JA,JQ,CA,CQ,MJ,MC,RJ,RC,MG,RG,SUM step;
```

## Ce que le rapport montre (mesures réelles)

Résultat d'un run `./mvnw test` (17 tests, 0 échec) — couverture de lignes
par classe, JUnit seul contre Cucumber seul contre la vue globale :

| Classe | JUnit seul | Cucumber seul | Global | Ce que ça révèle |
|---|---|---|---|---|
| `CalendarResource` | **0 %** | 58 % | 58 % | La couche REST n'est testée que par Cucumber — JUnit ne l'appelle jamais. |
| `HolidayService` | **0 %** | 93 % | 93 % | Idem : couverte uniquement par le scénario « jour férié », par ricochet. |
| `RecurrenceService` | 78 % | **4 %** | 78 % | À l'inverse : la logique de récurrence est testée par JUnit, presque pas par Cucumber (aucun scénario n'appelle l'endpoint de récurrence). |
| `ConflictDetector` | 100 % | 75 % | 100 % | Les deux la couvrent, mais pas les mêmes branches — l'union comble les trous. |
| `EventService` | 88 % | 88 % | 88 % | Bien couverte par les deux indépendamment : un vrai signal de confiance. |
| `RecurrenceRequest` (DTO) | **0 %** | **0 %** | 0 % | Angle mort partagé : ni JUnit ni Cucumber ne l'exercent. Le seul cas où la vue globale n'aide pas. |

Le constat clé pour la conférence : **JUnit et Cucumber ne couvrent presque
pas les mêmes lignes**. JUnit valide la logique métier en isolation ; Cucumber
valide le comportement observable via l'API. Une vue de couverture qui ne
distingue pas les deux masque cette complémentarité — et masque aussi les
angles morts que les deux partagent (`RecurrenceRequest`).

Ces écarts ne sont pas fabriqués : ce sont les résultats obtenus après avoir
écrit des tests JUnit et Cucumber « normaux », sans chercher à tout couvrir.
C'est exactement le point de la conférence — le rapport de couverture révèle
des trous qu'une suite de tests « verte » ne montre pas.

## Comment lancer la démo

```bash
./mvnw test                                   # build + tests + 3 rapports Jacoco
./scripts/coverage-summary.sh                 # JUnit / Cucumber / global, côte à côte

open target/jacoco-report-junit/index.html    # couverture JUnit seule
open target/jacoco-report-cucumber/index.html # couverture Cucumber seule
open target/jacoco-report/index.html          # vue globale (union des deux)
```

## Documentation associée

- [`CLAUDE.md`](./CLAUDE.md) — conventions et instructions du projet.
- [`PROMPT.md`](./PROMPT.md) — journal des prompts utilisés pour construire
  ce projet.
- [`presentation/couverture-code-conference.pptx`](./presentation/couverture-code-conference.pptx) —
  support de la conférence (10 slides, palette bleu marine / tons doux).
