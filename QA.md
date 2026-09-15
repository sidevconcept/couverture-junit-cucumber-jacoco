# Q&A de préparation — « La couverture de code, sans blabla »

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
