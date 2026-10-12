# Q&A de préparation — « La couverture de code, n'est jamais à 100% »

Questions/réponses anticipées pour le Q&A de fin de conférence (10-15 min
prévues, voir `SCRIPT.md`). Rédigé au fil de l'eau pendant la préparation.

---

## Est-ce qu'on doit vraiment atteindre 100 % de couverture ?

Non, et c'est même contre-productif de le viser comme objectif en soi.

- **100 % de couverture ne veut pas dire 0 bug.** On l'a montré en direct :
  `RecurrenceService` peut afficher un joli pourcentage global tout en
  cachant un cas jamais vérifié (la récurrence mensuelle sur un 31, ou un
   29 février). La couverture mesure ce qui a été **exécuté**, pas ce qui a
  été **vérifié**.
- **Chasser le 100 % pousse à écrire de mauvais tests.** Pour faire monter
  le chiffre vite, on finit par tester des getters/setters ou dupliquer des
  assertions triviales plutôt que les vrais cas limites métier — la
  métrique devient un objectif au lieu d'un indicateur (loi de Goodhart).
- **Certaines lignes ne valent juste pas le coût du test** : code de
  bootstrap, `main()`, mapping DTO trivial, branches défensives
  (`IllegalStateException` "ça ne devrait jamais arriver"). Les tester
  coûte du temps de maintenance pour un risque quasi nul.
- **Ce qui compte, c'est la couverture des zones à risque** : logique
  métier avec des branches (comme `RecurrenceService`), calculs, règles de
  gestion — pas la mécanique.

Le rapport de couverture n'est pas un objectif à atteindre, c'est un
**radar** : il montre où regarder en premier. Un bon seuil pragmatique
(80 % dans notre `coverage-summary.sh`, par exemple) sert à repérer les
trous béants, pas à viser un score parfait.

---

## Comment Sonar reçoit les informations de Jacoco et les interprète ?

Sonar ne mesure rien lui-même : **il importe un fichier XML déjà calculé
par Jacoco**, il ne relance jamais les tests ni ne lit le bytecode.

1. **Jacoco produit le XML, pas Sonar.** Dans notre `pom.xml`, le
   `jacoco-maven-plugin` (goal `report`, en plus du `.exec` binaire et du
   HTML) génère un rapport XML par vue :
   `jacoco-report-junit/jacoco.xml` et `jacoco-report-cucumber/jacoco.xml`.
   Ce format liste, par fichier source, chaque ligne avec son nombre
   d'instructions couvertes/manquées, et pareil pour les branches.

2. **Sonar est juste pointé vers ces fichiers.** Propriété dans le
   `pom.xml` de `quarkus-app` :
   `sonar.coverage.jacoco.xmlReportPaths=jacoco-report-junit/jacoco.xml,jacoco-report-cucumber/jacoco.xml`.
   Le plugin Java de Sonar (`sonar-maven-plugin` → sensor Jacoco XML)
   parse ces deux XML pendant `mvn sonar:sonar`, **aucune exécution Java
   n'est relancée** à ce moment-là — c'est juste de la lecture/agrégation
   de fichiers.

3. **Sonar recalcule l'union lui-même.** On lui donne deux rapports
   séparés (JUnit et Cucumber) plutôt qu'un rapport déjà fusionné : Sonar
   additionne, ligne par ligne, les instructions couvertes par l'un OU
   l'autre pour obtenir sa propre mesure de couverture globale — c'est
   pour ça qu'on n'a pas besoin de lui donner le `.exec` déjà mergé
   (`jacoco:merge`) qu'on utilise pour les rapports HTML.

4. **Sonar recroise avec sa propre analyse du code source.** Il analyse
   aussi le code Java lui-même (AST) pour son propre compte (bugs, code
   smells, duplication, security hotspots) — c'est un vrai calcul, celui-là.
   Il associe ensuite les chiffres de couverture importés aux fichiers
   qu'il vient d'analyser pour construire les vues Measures → Coverage.

**Résumé pour la conf** : Jacoco calcule, Sonar relit et présente. Sonar
« fait semblant d'avoir tout calculé » (la punchline de la slide 20) parce
que le seul vrai calcul qu'il fait lui-même, c'est tout sauf la couverture.

---

## Quelle est la différence entre couverture de lignes et de branches ?

- **Couverture de lignes** : une ligne de code source est marquée
  « couverte » dès qu'elle s'est exécutée **au moins une fois**, peu
  importe avec quelles valeurs.
- **Couverture de branches** : à chaque point de décision (`if`, `switch`,
  opérateurs `&&`/`||`, ternaire...), il y a plusieurs issues possibles.
  La couverture de branches vérifie que **chaque issue** a été exercée au
  moins une fois — pas seulement que la ligne a tourné une fois.

**Exemple concret du projet**, `ConflictDetector.isConflicting` :

```java
if (a.id() != null && a.id().equals(b.id())) {
    return false;
}
return a.start().isBefore(b.end()) && b.start().isBefore(a.end());
```

La ligne du `if` ne fait qu'une seule ligne physique, mais elle contient
**deux conditions enchaînées par `&&`**. Un seul test qui passe par cette
ligne suffit à la marquer 100 % couverte en *lignes*. Mais pour la couvrir
à 100 % en *branches*, il faut au minimum :
- un cas où `a.id()` est `null` (le `&&` s'arrête net, court-circuit),
- un cas où `a.id()` n'est pas `null` mais différent de `b.id()`,
- un cas où `a.id()` n'est pas `null` et égal à `b.id()`.

Trois chemins différents pour une seule ligne de code. C'est exactement
pour ça que Jacoco affiche les deux pourcentages séparément (visibles dans
`coverage-summary.sh` et dans le rapport HTML, en losange jaune/rouge/vert
sur la ligne concernée) : **une couverture de lignes élevée peut masquer
des branches jamais testées**, alors que la couverture de branches est un
signal plus strict — et plus honnête — sur la qualité réelle des tests.

C'est aussi pour ça que `RecurrenceService.shift` (le `switch` sur la
fréquence) est un bon exemple : chaque `case` occupe plusieurs lignes bien
distinctes, donc la couverture de lignes révèle déjà que `MENSUELLE` n'est
jamais exécuté. Mais sur du code plus compact (un seul `if` avec plusieurs
conditions, comme ci-dessus), seule la couverture de branches aurait pu
le révéler.

---

## Comment peut-on avoir 100 % de couverture sans que tous les cas soient couverts ?

Parce que la couverture mesure **si une ligne (ou une branche) a été
exécutée**, pas **si le comportement a été vérifié pour tous les cas
possibles**. Trois pièges expliquent l'écart.

**1. Pas d'assertion = ligne « verte » mais rien n'est vérifié.** Un test
qui appelle `isConflicting(a, b)` sans jamais faire `assertTrue`/
`assertFalse` sur le résultat fait grimper la couverture à 100 % sur cette
méthode, même si le résultat retourné est faux. Jacoco voit « la ligne
21 s'est exécutée », pas « le résultat était correct ».

**2. Un seul chemin peut suffire à « couvrir » une ligne entière.**
Reprenons `ConflictDetector.isConflicting` (voir aussi la question sur
lignes vs branches) :

```java
if (a.id() != null && a.id().equals(b.id())) {
    return false;
}
return a.start().isBefore(b.end()) && b.start().isBefore(a.end());
```

Un seul test avec deux événements qui se chevauchent franchement (id
différents) suffit à exécuter *toutes les lignes* : 100 % en **couverture
de lignes**. Mais ça ne teste jamais :
- le cas `id` identiques (le `return false` anticipé),
- le cas limite où les deux événements se *touchent exactement* — la
  règle métier dit explicitement que ça ne doit PAS être un conflit, et
  c'est justement la ligne la plus piégeuse du fichier,
- le cas où un seul des deux `isBefore` est vrai.

**3. Branch coverage ≠ toutes les combinaisons.** Même en passant en
**couverture de branches** (qui exige que le `if` soit pris vrai *et* faux
au moins une fois), un `&&` avec deux conditions peut être « 100 %
couvert » sans que chaque combinaison (vrai/faux, faux/vrai, faux/faux)
ait été testée individuellement — c'est la couverture MC/DC, que Jacoco ne
mesure pas.

**Pour la conf** : 100 % de couverture est une garantie minimale (« rien
n'est mort dans le code »), jamais une garantie de correction. C'est
exactement la distinction développée dans la question suivante
(coverage vs testing), et la raison pour laquelle on ne vise jamais le
100 % comme objectif en soi (voir la première question de ce document).

---

## Quelle est la différence entre coverage et testing ?

C'est LE point central de toute la conférence, résumé dans le premier
point de la slide « À retenir » : **un test vert ne dit pas ce qu'il a
vérifié — la couverture, si.** Ce sont deux choses différentes, et
confondre les deux est justement l'erreur classique.

- **Tester (testing)**, c'est écrire une assertion sur un **comportement
  attendu** : « pour cette entrée, je m'attends à ce résultat précis ».
  C'est un acte de vérification — `assertFalse(detector.isConflicting(a,
  b))`. Ça produit un verdict binaire : le comportement est correct, ou
  pas.
- **Mesurer la couverture (coverage)**, c'est observer, **après coup**,
  quelles lignes/branches du code ont été **exécutées** pendant que les
  tests tournaient. Ça ne vérifie rien du tout — Jacoco ne sait pas si le
  résultat était le bon, il sait juste que le code est passé par là.

Conséquence directe : **exécuter du code n'est pas la même chose que le
vérifier.**
- On peut avoir du code **exécuté sans être testé** : un test qui appelle
  une méthode sans faire d'assertion dessus (ou avec une assertion trop
  faible, genre `assertNotNull(resultat)`) fait grimper la couverture sans
  rien prouver sur la justesse du résultat.
- On peut avoir du code **testé sans être couvert à 100 %** — et c'est
  volontairement le cas dans ce projet : `RecurrenceService` a de vrais
  tests solides sur `QUOTIDIENNE`/`HEBDOMADAIRE`, mais `MENSUELLE` n'est
  simplement jamais exercé. Le code n'est pas mal testé, il est absent des
  tests.

La couverture est donc un **indicateur négatif fiable** (« cette ligne
n'a jamais tourné, donc elle n'a certainement pas été vérifiée ») mais un
**indicateur positif trompeur** (« cette ligne a tourné » ne dit rien sur
la qualité de ce qui a été vérifié dessus). D'où la formule de la
slide 24 : *la couverture mesure ce qui a été EXÉCUTÉ, pas ce qui a été
VÉRIFIÉ* — et d'où l'intérêt de croiser JUnit et Cucumber plutôt que de se
fier à un seul chiffre agrégé.

---

## C'est quoi un vrai bon test unitaire/intégration ?

Les deux niveaux ne répondent pas à la même question, donc « bon » ne veut
pas dire la même chose pour chacun.

### Un bon test unitaire (JUnit)

Exemple du projet, `ConflictDetectorTest` :

- **Isolé** : aucune dépendance externe, pas de Quarkus démarré, pas de
  réseau, pas d'horloge système — juste l'objet testé et ses entrées.
  Résultat : quelques millisecondes, on peut le lancer en boucle sans y
  penser.
- **Un comportement précis par test**, nommé pour ce qu'il vérifie plutôt
  que pour la méthode appelée : `deuxEvenementsQuiSeTouchentNeSontPasEnConflit`
  dit exactement ce qu'on teste, pas juste `testIsConflicting1`. Si ce
  test casse, le nom du test EST le rapport de bug.
- **Il teste les cas limites, pas juste le chemin heureux.** Les 4 tests
  de `ConflictDetectorTest` : chevauchement franc, contact exact (limite),
  séparation nette, réflexivité (un événement contre lui-même). Le cas
  limite (« ils se touchent pile ») est presque toujours celui qui révèle
  un bug — le chemin heureux, lui, passe presque toujours.
- **Déterministe et répétable** : même entrée → même résultat, toujours.
  Pas de `new Date()`, pas de nombre aléatoire non seedé, pas d'ordre de
  tests qui compte.
- **Teste le comportement, pas l'implémentation** : on vérifie que
  `isConflicting` renvoie `false`, pas qu'il appelle telle méthode interne
  dans tel ordre. Un bon test unitaire survit à un refactoring qui ne
  change pas le comportement.

### Un bon test d'intégration (Cucumber ici)

- **Passe par le vrai chemin**, pas un mock : nos scénarios appellent la
  vraie API REST via RestAssured, comme le ferait un vrai client HTTP. Un
  test d'intégration qui mocke la couche qu'il est censé intégrer ne teste
  plus rien d'intégré.
- **Décrit un comportement observable de l'extérieur**, pas un détail
  d'implémentation interne : « la création est refusée pour cause de
  conflit d'horaire », pas « la méthode `create()` lève une exception ».
- **Lisible par quelqu'un qui ne code pas** : c'est la promesse du Gherkin
  en français — le scénario sert à la fois de spec fonctionnelle et de
  test automatisé, sans traduction entre les deux.
- **Teste un scénario métier complet**, avec un vrai contexte (« j'ai déjà
  l'événement Comité de pilotage de 14h à 15h »), pas une requête isolée
  sans état préalable.

### Le point commun aux deux

**Self-validating** : le test dit lui-même s'il passe ou échoue (une
assertion claire), on n'a jamais besoin de lire un log ou une sortie
console pour savoir si ça a marché. Et surtout : un bon test peut échouer.
S'il ne peut structurellement jamais rater (assertion trop faible, ou
aucune assertion), ce n'est pas un test, c'est juste du code qui s'exécute
— on est revenu à la distinction coverage vs testing de la question
précédente.

---

## Comment fonctionne Jacoco ?

Jacoco ne lit pas le code source : il **instrumente le bytecode** pendant
l'exécution, et compte ce qui tourne réellement dans la JVM.

1. **Instrumentation par agent (`-javaagent`).** Le `jacoco-maven-plugin`
   attache un agent à la JVM au moment où Surefire la lance (goal
   `prepare-agent`, propriété `argLine` injectée dans la config Surefire).
   Cet agent intercepte chaque classe **au chargement** et réécrit son
   bytecode à la volée : il insère des compteurs (des « sondes ») à chaque
   ligne et à chaque branche possible d'un point de décision (`if`,
   `switch`, `&&`/`||`...). Aucune modification du `.java` ni du `.class`
   sur disque — tout se passe en mémoire, au chargement.
2. **Ces sondes s'incrémentent pendant les tests.** Chaque fois qu'une
   instruction passe par une sonde, un compteur monte. Jacoco ne sait rien
   du résultat du test (vert ou rouge, assertion vraie ou fausse) — il
   compte juste des passages, d'où la distinction coverage vs testing vue
   plus haut.
3. **À la fin de la JVM, les compteurs sont écrits dans un fichier
   binaire `.exec`** (format propre à Jacoco, pas du XML). C'est un
   instantané des compteurs, pas encore un rapport lisible.
4. **Le rapport est généré après coup** (goal `report` du
   `jacoco-maven-plugin`) : Jacoco relit le `.exec` **et** les `.class`
   d'origine (non instrumentés, ceux compilés par Maven), fait
   correspondre chaque sonde à sa ligne/branche source grâce aux numéros
   de ligne du bytecode (debug info), et produit HTML/XML/CSV à partir de
   cette correspondance.

**Piège spécifique à ce projet** (voir aussi `CLAUDE.md`) : avec Quarkus,
**deux** mécanismes de mesure coexistent et ne se voient pas l'un l'autre.

- L'agent `-javaagent` de `jacoco-maven-plugin` mesure tout ce qui tourne
  dans le process Surefire classique.
- L'extension `quarkus-jacoco` (dépendance de test) mesure, **séparément**,
  tout ce qui tourne dans le `QuarkusClassLoader` — c'est-à-dire les beans
  CDI appelés depuis un `@QuarkusTest` ou un scénario Cucumber, qui
  vivent dans un classloader que l'agent standard ne voit pas correctement
  dans le contexte Quarkus. Elle écrit son propre `.exec`, au chemin fixé
  par la propriété système `quarkus.jacoco.data-file` (un chemin distinct
  par exécution Surefire — JUnit et Cucumber — sinon les deux s'écrasent).

D'où l'étape `jacoco:merge` dans le `pom.xml` de `quarkus-app` avant chaque
`jacoco:report` : on fusionne le `.exec` de l'agent et celui de l'extension
(par exécution JUnit et Cucumber), puis on fusionne encore tout ensemble
pour la vue globale — trois `report` distincts à partir de trois jeux de
`.exec` fusionnés (`jacoco-report-junit/`, `jacoco-report-cucumber/`,
`jacoco-report/`). Sans ce merge, chaque rapport ne verrait que la moitié
du code réellement exécuté.

---

## Pourquoi et comment fusionne-t-on les fichiers `.exec` de Jacoco ?

Parce qu'on a **quatre** fichiers `.exec` en sortie des tests, chacun
incomplet à lui seul, et qu'un rapport a besoin de tout voir à la fois.

**D'où viennent les quatre fichiers.** Pour chaque exécution Surefire
(JUnit et Cucumber), deux mesures tournent en parallèle et écrivent
chacune leur propre `.exec` (voir la question précédente sur le
fonctionnement de Jacoco) :

- `jacoco-junit.exec` / `jacoco-cucumber.exec` — écrits par l'agent
  `-javaagent` du `jacoco-maven-plugin` (executions `prepare-agent-junit`
  / `prepare-agent-cucumber`). Sa config porte
  `<exclClassLoaders>*QuarkusClassLoader</exclClassLoaders>` : il mesure
  tout **sauf** le code qui tourne dans le conteneur CDI (par exemple
  `ConflictDetectorTest`, qui instancie directement ses classes, sans
  passer par Quarkus).
- `jacoco-junit-quarkus.exec` / `jacoco-cucumber-quarkus.exec` — écrits
  par l'extension `quarkus-jacoco`, au chemin fixé par la propriété
  système `quarkus.jacoco.data-file` dans la config Surefire. Elle mesure
  l'inverse : tout ce qui tourne **dans** le `QuarkusClassLoader` (un bean
  CDI appelé depuis un `@QuarkusTest` ou un scénario Cucumber).

Le `exclClassLoaders` de l'agent existe justement pour que les deux
mesures ne se recouvrent jamais — sans lui, le code CDI serait compté
deux fois. Résultat : **chacun des quatre fichiers ne contient qu'une
moitié du code réellement exécuté**, jamais la vue complète.

**Le merge recolle les moitiés.** Le `jacoco-maven-plugin` a trois
executions de goal `merge`, toutes en phase `test` (donc après les
Surefire, avant les `report`) :

- `merge-junit` : fusionne `jacoco-junit.exec` +
  `jacoco-junit-quarkus.exec` → `jacoco-junit-all.exec`.
- `merge-cucumber` : fusionne `jacoco-cucumber.exec` +
  `jacoco-cucumber-quarkus.exec` → `jacoco-cucumber-all.exec`.
- `merge-global` : fusionne les **quatre** fichiers d'un coup →
  `jacoco-merged.exec`.

Techniquement, `jacoco:merge` ne fait rien de subtil : il additionne les
compteurs de sondes des fichiers en entrée, sonde par sonde (même classe,
même ligne, même branche) — le résultat est identique à si un seul run
avait exécuté tout le code des fichiers d'entrée.

**Chaque `.exec` fusionné alimente un seul rapport** : `report-junit` lit
`jacoco-junit-all.exec` (→ `jacoco-report-junit/`), `report-cucumber` lit
`jacoco-cucumber-all.exec` (→ `jacoco-report-cucumber/`), `report-global`
lit `jacoco-merged.exec` (→ `jacoco-report/`, la vue "union des deux"
citée dans la question sur Sonar). Sans ce merge en amont, le rapport
JUnit par exemple ne montrerait quasiment aucune ligne de service/resource
couverte, puisque tout ce code-là tourne dans le `QuarkusClassLoader` et
ne serait visible que dans le `.exec` de l'extension, jamais fusionné
avec celui de l'agent.

---
