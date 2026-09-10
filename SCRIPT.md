# Script de présentation — « La couverture de code, sans blabla »

Script à suivre pour une conférence d'environ **60 minutes** (+ questions),
support : `presentation/couverture-code-conference.pptx` (28 slides).
Ton : technique mais décontracté, jeux de mots assumés, on se moque
gentiment des situations que tout développeur reconnaît.

> Ce script est un guide, pas un texte à réciter mot pour mot. Les blagues
> entre « » sont des propositions — gardez celles qui vous ressemblent,
> jetez les autres sans remords. C'est comme la couverture de code : viser
> 100 % d'un script figé serait raté.

## Minutage indicatif

| Bloc | Slides | Durée | Cumulé |
|---|---|---|---|
| Accroche + agenda | 1–4 | 7 min | 7 min |
| Le problème | 5 | 3 min | 10 min |
| La stack | 6–7 | 7 min | 17 min |
| JUnit | 8–9 | 6 min | 23 min |
| Cucumber | 10–11 | 6 min | 29 min |
| Le match + bascule | 12–13 | 3 min | 32 min |
| **Live demo #1** — `mvn test` | (terminal) | 5 min | 37 min |
| Jacoco (théorie + captures) | 14–18 | 12 min | 49 min |
| **Live demo #2** — récap + rapport HTML | (terminal) | 4 min | 53 min |
| En direct (recap 3 commandes) | 19 | 1.5 min | 54.5 min |
| Bonus SonarQube | 20–23 | 8 min | 62.5 min |
| Excuses + retour d'expérience | 24–25 | 7 min | 69.5 min |
| Conclusion | 26–28 | 4.5 min | 74 min |

74 minutes de contenu pour un créneau d'1h : deux soupapes de sécurité sont
identifiées ci-dessous (⏱️ **coupable si en retard**) — les couper ramène
pile à l'heure.

---

## Slide 1 — Titre (1 min)

*(Rideau. Enfin, vidéoprojecteur.)*

« Bonsoir tout le monde. Le titre annonce "sans blabla" — je vais donc
essayer de ne pas commencer par 45 minutes de blabla pour vous dire qu'il
n'y aura pas de blabla. Raté.

Ce soir, on va parler de **couverture de code**. Pas celle de votre lit —
quoique, les deux ont la même vocation : vous éviter d'avoir froid dans le
dos quand quelque chose part en vrille au milieu de la nuit.

Stack du jour : Quarkus, JUnit, Cucumber, Jacoco — et un bonus SonarQube
pour ceux qui tiennent jusqu'au bout. »

---

## Slide 2 — Qui suis-je (2 min)

*(Personnalisez avec votre vraie bio. Gardez la structure : fait crédible →
fait drôle → pourquoi vous êtes légitime.)*

« [X années] à écrire du Java, [contexte pro]. J'ai un ratio tests/code que
je ne montrerai à personne ici — certains d'entre vous ont peut-être le
même, on ne juge pas, on est entre adultes consentants qui ont tous une
classe `Utils.java` de 2000 lignes non testée quelque part.

Je suis là ce soir pour une raison précise : vous convaincre de regarder
votre VRAI rapport de couverture. Pas celui que vous imaginez avoir. »

---

## Slide 3 — Icebreaker (2 min)

« Petit sondage à main levée, sans conséquence juridique :

Levez la main si vous avez déjà écrit un test **juste pour faire plaisir à
la CI**. *(pause, comptez les mains, commentez le nombre)*

Toujours levée si vous avez déjà vu **100 % de couverture** sur un fichier
qui, on le sait tous, est plein de bugs.

Et gardez la main levée — ou plutôt, ne la levez surtout pas, parce que
personne ne veut l'admettre publiquement — si vous ne savez pas, là,
maintenant, ce que couvrent vos tests.

Pas de jugement. Enfin... un peu. »

---

## Slide 4 — Agenda (1.5 min)

« Le programme : le problème, la stack en quatre outils, une démo qu'on va
vraiment lancer en direct — pas des captures d'écran PowerPoint qui ont
"marché une fois avant la conf" — et un rapport de couverture qu'on va
scinder en deux pour voir qui, de JUnit ou de Cucumber, fait vraiment le
travail. Spoiler tout de suite : c'est un peu les deux, et c'est tout
l'intérêt. »

---

## Slide 5 — Le constat (3 min)

« On a des tests. Ça, tout le monde ici en a. La question n'est pas "avez-
vous des tests", c'est "savez-vous ce qu'ils font vraiment".

Trois symptômes classiques : on écrit des tests — bien. On ne sait pas ce
qu'ils couvrent — moins bien. Et les angles morts restent invisibles
jusqu'au jour où un utilisateur les découvre à votre place, généralement un
vendredi à 17h58.

*(ton complice)* Alerte spoiler : ce jour-là, "ça marche sur ma machine" ne
sauve personne. »

---

## Slide 6 — La stack technique (4 min)

« Quatre outils, quatre questions différentes — et c'est important, parce
que la confusion classique c'est de croire qu'ils font tous la même chose.

- JUnit répond à : **la fonction fait-elle ce qu'elle doit ?**
- Cucumber répond à : **le comportement observable est-il le bon ?**
- Quarkus, c'est le chef d'orchestre qui fait tourner tout ce petit monde.
- Jacoco, c'est celui qui note sur son carnet ce qui a vraiment été joué.

Aucun de ces outils ne remplace les autres. Un JUnit qui teste une méthode
isolée ne vous dit RIEN sur si votre API répond correctement. Et un
Cucumber qui passe ne vous dit rien sur les cas limites internes. »

---

## Slide 7 — Le terrain de jeu : un agenda malin (3 min)

« Pour illustrer tout ça sans vous perdre dans un vrai projet d'entreprise
à 40 modules, j'ai construit un projet volontairement simple : un agenda
d'événements. Il détecte les conflits d'horaire, gère des récurrences,
signale les jours fériés, et — parce qu'un projet de démo a le droit d'être
un peu sympa — sort une citation du jour sur les tests.

Pas de base de données. Le sujet du jour c'est la couverture, pas
Hibernate. On se recentre. »

---

## Slide 8 — Zoom JUnit : le microscope (3 min)

« JUnit, c'est le microscope. On isole une classe, on isole une méthode, on
vérifie qu'elle fait EXACTEMENT ce qu'elle doit, sans lancer toute
l'application autour.

Rapide, isolé, technique — pensé par des devs, pour des devs. Personne
d'autre dans l'entreprise ne va relire un `assertEquals`. Et c'est très bien
comme ça. »

---

## Slide 9 — JUnit en action (3 min)

« Voici `ConflictDetectorTest` — quatre tests, quatre cas limites :
chevauchement, contact exact, séparation nette, et un événement comparé à
lui-même *(petit temps)* — oui, on a testé qu'un événement n'est pas en
conflit avec lui-même. Si ce test échoue un jour, on a un problème
existentiel plus grave qu'un bug.

Zéro Quarkus démarré, zéro I/O. Quelques millisecondes. C'est ça, la
promesse de JUnit : vous ne devriez jamais avoir d'excuse pour ne pas
lancer ces tests-là en boucle toute la journée. »

---

## Slide 10 — Zoom Cucumber : le grand angle (3 min)

« Cucumber, c'est le grand angle. On ne regarde plus une méthode, on
regarde le comportement du point de vue de quelqu'un qui utilise l'API.

Et le texte que vous voyez dans le `.feature` n'est pas un commentaire
décoratif : c'est littéralement ce qui s'exécute. Si un product owner sait
lire du français, il peut relire — et parfois corriger — vos scénarios de
test. Ça change des tickets Jira écrits en une phrase énigmatique un
vendredi soir. »

---

## Slide 11 — Cucumber en action (3 min)

« "Étant donné que j'ai déjà l'événement Comité de pilotage... quand je
crée Revue de code au même horaire... alors la création est refusée." Vous
remarquerez que même le scénario de test sait qu'un comité de pilotage
prend toute la place dans l'agenda. Ça, c'est du réalisme métier.

Ce texte passe par la vraie API REST, via RestAssured. Pas de mock, pas de
simulation : c'est un vrai appel HTTP, comme le ferait un vrai client. »

---

## Slide 12 — Le match : JUnit vs Cucumber (2 min)

« Alors, qui gagne ? *(pause)* Personne. Et c'est le point important : ce
n'est pas un combat, c'est un tandem. JUnit sans Cucumber, vous validez la
mécanique interne sans jamais vérifier que l'API répond bien. Cucumber sans
JUnit, vous validez le comportement extérieur sans jamais tester les cas
limites internes.

Le seul vrai gagnant, c'est le code — testé sous deux angles différents. Et
dans deux minutes, on va voir EXACTEMENT ce que ça change dans le rapport de
couverture. C'est là que ça devient intéressant. »

---

## Slide 13 — Bascule live demo (0.5 min)

« On arrête PowerPoint. Direction le terminal, pour de vrai. »

### 🎬 LIVE DEMO #1 (5 min)

Ouvrir un terminal sur le projet, lancer :

```bash
./mvnw test
```

Pendant que ça tourne (Quarkus qui démarre, JUnit, puis Cucumber) :

« Pendant que ça compile, petite anecdote : ce projet a un fichier
`RunCucumberTest.java` — remarquez le nom, il se termine par "Test", pas par
"IT". C'est volontaire : Maven a des conventions de nommage strictes, et si
vous les ignorez, vos tests d'intégration ne se lancent tout simplement
jamais. Personne ne vous préviendra. Vous découvrirez ça... vous savez
quand. Un vendredi. »

Quand les tests passent (17 tests, 0 échec) :

« Et voilà. JUnit et Cucumber, dans le même build, sans drame. La partie
intéressante arrive maintenant : `mvn test` vient AUSSI de générer trois
rapports de couverture, en silence, sans qu'on lui demande deux fois. »

---

## Slide 14 — Zoom Jacoco : comment ça marche (3 min)

« Jacoco, en trois étapes : au démarrage de la JVM, un agent Java
s'attache et instrumente chaque classe chargée — au sens propre, il modifie
le bytecode à la volée pour y glisser des compteurs. Pendant les tests,
chaque ligne et chaque branche exécutée est comptée. Et à l'arrêt de la
JVM, tout est vidé dans un fichier `.exec`, transformé ensuite en rapport
HTML par `jacoco-maven-plugin`.

Non, ce n'est pas de l'espionnage industriel. C'est juste un agent Java très
curieux, payé en aucune façon, qui note tout ce qu'il voit. »

---

## Slide 15 — Jacoco, vue d'ensemble (2 min)

*(Montrer la capture d'écran — préciser que c'est un vrai export, pas une
maquette)*

« Ça, ce n'est pas un mockup Figma pour faire joli sur une slide bleu
marine. C'est un `index.html` généré il y a quelques heures, sur ce projet,
par cette commande qu'on vient de lancer. Vous pouvez le vérifier vous-même
en clonant le repo — le lien arrive en fin de conf. »

---

## Slide 16 — Jacoco, la preuve dans le code (3 min)

*(LE moment fort visuel — laisser la slide respirer quelques secondes avant
de parler)*

« Regardez cette classe : `RecurrenceService`. En vert : quotidien,
hebdomadaire — testés. En rouge : mensuel. Pas testé du tout.

Et ce n'est pas un hasard malheureux : la récurrence mensuelle est
justement le cas le plus piégeux — `plusMonths()` en Java "écrête"
automatiquement les jours qui n'existent pas dans le mois suivant. 31
janvier plus un mois, ça donne 28 ou 29 février selon l'année. Bissextile
ou pas. Et devinez quoi : personne n'a testé ce cas précis.

C'est exactement le genre de ligne rouge que votre suite de tests, verte à
100 %, ne vous montrera JAMAIS. Sauf si vous ouvrez ce rapport. »

---

## Slide 17 — JUnit vs Cucumber dans Jacoco (3 min)

« Et voilà où ça devient franchement amusant : on a scindé le rapport par
type de test. `CalendarResource`, la couche REST : 0 % en JUnit, 58 % en
Cucumber — logique, JUnit ne parle jamais à l'API. `RecurrenceService` :
l'inverse, 78 % en JUnit, 4 % en Cucumber.

Ces deux suites de tests, prises séparément, mentent chacune par omission.
Prises ensemble, elles racontent enfin la vérité. C'est le seul intérêt
réel de scinder ce rapport : arrêter de croire qu'"on a des tests" veut dire
"on a TOUT testé". »

---

## Slide 18 — Le terminal, récap coloré (2 min)

« Et si vous n'avez pas envie d'ouvrir un navigateur à chaque commit,
`coverage-summary.sh` fait le café à votre place : rouge, orange, vert,
directement dans le terminal, classe par classe, pour les trois vues. »

---

### 🎬 LIVE DEMO #2 (4 min)

```bash
./scripts/coverage-summary.sh
```

« Regardez la ligne `RecurrenceRequest` — 0 % partout, JUnit ET Cucumber.
Ça, c'est LE cas qui devrait vous faire lever un sourcil : même en croisant
les deux types de test, personne n'a jamais touché cette classe. »

```bash
open target/jacoco-report/index.html
```

Naviguer en direct jusqu'à `RecurrenceService.java` pour retrouver le rouge
vu sur la slide 16 — « vous voyez, ce n'était pas une capture triée sur le
volet, c'est vraiment là. »

---

## Slide 19 — En direct : trois commandes (1.5 min)

« Pour résumer ce qu'on vient de faire, en vrai, sans trucage : trois
commandes. `mvn test`, le script de récap, et le rapport HTML. C'est tout.
Rien d'exotique, rien à installer de plus que ce qu'on a déjà dans le
`pom.xml`. »

---

## Slide 20 — Bonus SonarQube (2 min)

« Le terminal et le HTML brut, c'est très bien pour un développeur seul
face à son clavier à 23h. Mais si vous voulez que toute l'équipe — y compris
les gens qui n'ouvrent jamais un terminal — voie la même information, il
faut un vrai dashboard. C'est là qu'entre SonarQube.

Et attention, petite confession publique : au départ, on m'a demandé une
intégration "SOAR" pour ces données. SOAR, comme dans "orchestration
d'incidents de sécurité". J'ai cherché un connecteur Jacoco dans un SOAR
pendant de looongues minutes avant de comprendre qu'on voulait dire
"Sonar". Une lettre de différence, et j'étais prêt à câbler un playbook de
réponse à incident pour... un pourcentage de couverture de code. Bref, même
en préparant une conf sur la rigueur des tests, on peut se planter sur
l'évidence. »

---

## Slide 21 — SonarQube, dashboard (2 min)

« 77,7 % de couverture, "Quality Gate: Passed", en vrai, dans l'interface —
générée à partir des deux mêmes rapports Jacoco XML qu'on vient de montrer
en direct. Sonar ne fait pas sa propre mesure : il relit ce que Jacoco a
déjà produit et recalcule l'union tout seul. »

---

## Slide 22 — SonarQube, mesures par fichier (2 min)

« Et là, le détail fichier par fichier — vous reconnaissez les mêmes
pourcentages que dans notre terminal, `CalendarResource` à 56-58 %,
`RecurrenceService` autour de 78-80 %. Même donnée, deux vitrines. »

---

## Slide 23 — SonarQube, la preuve encore (2 min)

« Et la même branche MENSUELLE, en rouge, dans une interface complètement
différente. Ça devrait vous rassurer plutôt que vous ennuyer : ce n'est pas
un artefact d'un outil bizarre, c'est un fait sur votre code, que deux
outils indépendants confirment. »

⏱️ **Soupape #1 si en retard : sauter les slides 21-23 et ne montrer que
la 20 (les chiffres), en disant "les captures sont dans le support, je vous
laisse les admirer après".**

---

## Slide 24 — Les excuses classiques (3 min)

*(LE moment humour assumé — jouer le ton "je les ai toutes dites un jour")*

« Petit best-of, en cinq actes, de ce qu'on se dit à soi-même pour ne pas
écrire de test :

Un : "Ça marche sur ma machine." — Votre machine n'ira pas en prod avec
vous, elle ne peut pas témoigner.

Deux : "On testera après le sprint." — Le sprint suivant aussi. Et celui
d'après. À ce rythme, on teste au moment du démantèlement de l'entreprise.

Trois : "C'est trop simple pour bugger." — Cette phrase précède
statistiquement neuf incidents de prod sur dix. Je n'ai pas la source, mais
vous me croyez, hein ?

Quatre : "Le stagiaire a dit que ça passait." — Le stagiaire a testé une
fois, à la main, un mardi après-midi ensoleillé.

Cinq, mon préféré : "100 % de couverture, on n'a plus besoin de relire." —
On vient littéralement de montrer une classe à 100 % de couverture des
MÉTHODES qui rate complètement le cas bissextile. La couverture mesure ce
qui a été EXÉCUTÉ, pas ce qui a été VÉRIFIÉ.

Spoiler final : aucune de ces cinq phrases n'a jamais empêché un incendie
en prod. Pas une seule. J'ai vérifié. Enfin... je crois. »

---

## Slide 25 — Retour d'expérience : deux pièges qu'on a vraiment eus (4 min)

« Et pour finir sur une note d'humilité : même en préparant CETTE conf, on
s'est fait avoir. Deux fois.

Piège un : le QuarkusClassLoader fantôme. En scindant le rapport par type
de test, tout retombait mystérieusement à 0 %. La cause : l'extension
`quarkus-jacoco` mesure, toute seule dans son coin, le code qui tourne via
CDI — indépendamment de l'agent Jacoco classique. Personne ne vous le dit
dans la doc en gros caractères. Il a fallu fusionner deux sources de
données différentes pour récupérer une mesure cohérente.

Piège deux, plus bête, plus douloureux : un fichier `.feature` en français
qui commençait par "Fonctionnalite" — sans accent. Résultat : le parseur
Gherkin ne reconnaissait littéralement rien du fichier. Un `é` manquant,
et Cucumber devient aussi utile qu'un GPS sans signal.

La morale n'est pas "n'utilisez pas ces outils" — la morale, c'est que même
les gens qui construisent des demos sur les tests se prennent les pieds
dans le tapis. Le seul vrai avantage qu'on a eu sur vous : un rapport de
couverture pour nous le prouver noir sur blanc. »

⏱️ **Soupape #2 si en retard : réduire ce bloc à un seul piège (le
QuarkusClassLoader, le plus instructif) et enchaîner.**

---

## Slide 26 — Ce qu'il faut retenir (2 min)

« Quatre points, et je vous laisse partir :

Un, un test vert ne dit pas ce qu'il a vérifié — la couverture, si.

Deux, JUnit et Cucumber répondent à deux questions différentes. Ce n'est
pas redondant, c'est complémentaire.

Trois, le rapport de couverture n'est pas un objectif à atteindre, c'est un
radar. Il ne vous dit pas "vous avez fini", il vous dit "regardez par ici
d'abord".

Quatre — et celui-là est valable pour Jacoco, pour Sonar, et pour n'importe
quel outil qu'on inventera l'année prochaine : un outil ne remplace jamais
la question qu'on ne s'est pas posée. »

---

## Slide 27 — Pour aller plus loin (1.5 min)

« Le dépôt complet est public : code, scripts, et même le journal de tous
les prompts utilisés pour le construire, si ça vous amuse de voir les
coulisses. Plus les guides officiels Quarkus, Cucumber et SonarQube pour
creuser sans moi. »

---

## Slide 28 — Merci / Questions

« Merci de votre attention. Et si quelqu'un me dit "chez nous on a 100 % de
couverture", je réponds déjà : sur quelle branche ? »

*(Q&A — garder 10-15 minutes si le planning le permet)*

---

## Notes de régie

- **Répétition conseillée** avec le live demo réel avant le jour J : lancer
  `./mvnw test` une fois à froid pour connaître le temps de build exact sur
  la machine de la salle (Wi-Fi de conférence + Maven qui télécharge une
  dépendance oubliée = angoisse).
- **Avant de partir** : `docker compose -f sonarqube/docker-compose.yml down
  -v` puis `up -d` pour repartir d'une instance Sonar propre (voir
  `CLAUDE.md`), sinon vous devrez justifier en direct pourquoi le mot de
  passe admin par défaut ne fonctionne plus.
- **Si la salle rit peu** : les blagues sur "couverture" (lit/code) peuvent
  être filées en transition entre plusieurs slides plutôt que concentrées —
  ne pas insister si une vanne tombe à plat, enchaîner sur le fond.
- **Si le temps déborde** : utiliser les deux soupapes identifiées
  (slides 21-23 et slide 25) avant de couper la partie technique.
