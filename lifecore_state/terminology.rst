Terminology
===========

Purpose
-------

Ce document fixe le vocabulaire partagé de ``lifecore_state`` pour Sprint 17.
Il sert de repère commun avant toute proposition de package, de message ROS 2
ou d'implémentation runtime.

Scope
-----

Les définitions ci-dessous sont volontairement courtes, concrètes et centrées
sur le contexte du projet. Quand un mot est ambigu, le risque de confusion est
signalé explicitement.

Glossary
--------

Documentation, packages, and repository terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RFC
  RFC signifie ``Request For Comments``. Dans ce projet, c'est un document de
  conception relu avant de coder, par exemple
  ``rfc_001_lifecore_state_architecture.rst``.

API
  Une API est le contrat visible par le code source, par exemple une méthode
  Python comme ``LifecycleComponentNode.register_component()`` et ce qu'elle
  promet d'accepter ou de renvoyer. Si la signature ou le sens change, le code
  appelant doit souvent changer aussi.

ABI
  Une ABI est un contrat plus bas niveau, surtout important quand des binaires
  ou des formats stables doivent rester compatibles. Dans ROS 2, un fichier
  ``.msg`` publié sur un topic devient vite un contrat difficile à casser sans
  impacter les autres nodes.

ROS 2 package
  Un package ROS 2 est un dossier repérable par les outils ROS 2, en pratique
  avec un ``package.xml`` et souvent un ``CMakeLists.txt`` ou une config
  Python. Par exemple, un futur ``lifecore_state_msgs`` serait un package ROS 2
  si ``colcon`` peut le découvrir dans un workspace.

Python package
  Un package Python est un module importable, généralement un dossier avec
  ``__init__.py``. Par exemple, ``src/lifecore_ros2/`` est un package Python,
  alors que ``lifecore_state/`` pendant Sprint 17 ne l'est pas.

Repository
  Un repository est un dépôt Git unique avec son historique, ses fichiers et sa
  revue de changements. Ici, ``lifecore_ros2`` est un repository distinct du
  repository compagnon ``lifecore_ros2_examples``.

Monorepo
  Un monorepo est un seul repository qui contient plusieurs packages ou projets
  liés. Par exemple, un repository qui hébergerait à la fois
  ``lifecore_state_core``, ``lifecore_state_ros`` et ``lifecore_state_msgs``
  serait un monorepo.

ROS 2 Workspace
  Un workspace ROS 2 est un dossier de travail où ``colcon`` cherche des
  packages, souvent via un sous-dossier ``src/``. Par exemple,
  ``lifecore_ros2_ws`` joue ce rôle quand on y place plusieurs packages à
  construire ensemble.

colcon
  ``colcon`` est l'outil de build et de découverte de packages le plus courant
  en ROS 2. Il sert par exemple à construire plusieurs packages d'un workspace
  et à préparer un environnement d'exécution cohérent.

rclpy
  ``rclpy`` est la bibliothèque cliente Python de ROS 2. C'est elle qui permet
  à un node Python de publier, souscrire, offrir un service ou gérer un
  lifecycle ROS 2.

Lifecycle and component terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lifecycle node
  Un lifecycle node est un node ROS 2 avec des transitions explicites comme
  ``configure``, ``activate``, ``deactivate``, ``cleanup`` et ``shutdown``.
  Exemple concret: un capteur peut créer ses publishers en ``configure`` puis
  n'envoyer des données qu'après ``activate``.

LifecycleComponent
  Dans ``lifecore_ros2``, un ``LifecycleComponent`` est un objet de comportement
  rattaché au cycle de vie d'un ``LifecycleComponentNode``. Par exemple, un
  composant publisher crée sa ressource en ``configure`` puis bloque ou autorise
  l'envoi selon l'état d'activation.

Component
  ``Component`` est un mot ambigu et il faut toujours préciser le contexte. En
  ROS 2, il peut désigner un node composable; dans ``lifecore_ros2``, il peut
  désigner un ``LifecycleComponent``; dans un ECS, il désigne souvent un paquet
  de données.

ECS
  ECS signifie ``Entity Component System``: une ``Entity`` identifie un objet,
  un ``Component`` porte des données, et un ``System`` traite des groupes
  d'entités. Ce n'est pas la direction retenue pour Sprint 17: le sprint décrit
  un modèle d'état distribué et synchronisable, pas un runtime ECS généraliste
  caché derrière ``lifecore_ros2``.

ECS Component
  Dans un ECS, un ``Component`` est surtout un paquet de données, par exemple
  une position ``x, y, z`` ou une batterie restante. Il ne faut pas le confondre
  avec un ``LifecycleComponent`` de ``lifecore_ros2``, qui porte du comportement
  lié aux transitions du node.

State model terms
~~~~~~~~~~~~~~~~~

Descriptor
  Un descriptor décrit un champ unitaire: son nom, son sens, son type attendu,
  et parfois ses contraintes. On peut le lire comme un futur ``StateDescriptor``.
  Exemple: le champ ``battery.voltage`` peut être décrit comme une tension en
  volts mesurée sur un robot.

Description
  Une description est un ensemble versionné de descriptors cohérents. On peut
  la lire comme une future ``StateDescription``. Exemple: une
  ``StateDescription`` peut dire qu'un robot publie ``battery.voltage``,
  ``battery.current`` et ``battery.temperature`` dans une même structure.

State
  ``State`` désigne l'ensemble des valeurs connues à un instant donné pour un
  périmètre précis. Par exemple, l'état d'un bras robotique peut regrouper sa
  position, sa température moteur et l'état de sa pince.

StateSample
  Un ``StateSample`` est une observation unitaire d'une valeur. Exemple: “la
  température du moteur gauche vaut 48,2 C à 10:32:01” est un sample.

StateUpdate
  Un ``StateUpdate`` est un événement de synchronisation qui transporte un ou
  plusieurs samples ou changements observés pour un même périmètre. Par
  exemple, un même message peut publier à la fois une nouvelle tension batterie
  et un nouveau courant moteur.

StateCommand
  Un ``StateCommand`` est une demande de mutation, pas une vérité observée.
  Exemple: “mettre la consigne de vitesse à 0,4 m/s” est une commande, même si
  le robot n'a pas encore réellement atteint cette vitesse.

StateOwner
  Un ``StateOwner`` désigne l'entité considérée comme faisant autorité pour
  produire un état observé, accepter une commande ou rejeter une mutation sur
  un descriptor donné. Ce n'est pas forcément le node ROS 2 qui relaie le
  message: un bridge, un relay ou une projection peut transporter l'information
  sans être la source sémantique de vérité.

Snapshot
  Un snapshot est une vue complète de l'état connu sur un périmètre donné.
  Exemple: au démarrage d'une station au sol, on peut envoyer tout l'état connu
  du robot au lieu de seulement les dernières différences.

Delta
  Un delta contient seulement les changements partiels depuis un état déjà
  connu. Exemple: si seule la température change, un delta n'a pas besoin de
  republier aussi la position, la batterie et tous les autres champs.

Registry
  Un registry est avant tout le catalogue des champs ou descriptors connus dans
  un périmètre donné. Exemple: un registry de supervision peut lister tous les
  chemins d'état autorisés pour un robot mobile. Par défaut, ce terme ne veut
  pas dire “store mutable global” ni “blackboard runtime”.

Projection
  Une projection est une vue filtrée d'un registry selon un rôle, un besoin ou
  une autorité. Exemple: un écran opérateur peut voir la batterie et les alarmes,
  alors qu'un module d'étalonnage voit aussi des champs techniques internes.

Authority
  Une authority désigne le droit reconnu d'écrire, commander ou publier une
  partie de l'état. Exemple: un module batterie peut être l'autorité pour
  ``battery.voltage``, tandis qu'une interface opérateur peut seulement lire
  cette valeur. Dans le RFC, ``StateOwner`` précise ce rôle lorsqu'il faut
  nommer l'entité sémantiquement responsable d'un descriptor.

Registry-scoped synchronization
  La synchronisation à l'échelle d'un registry veut dire que plusieurs registries
  appliquent la même intersection de topics ou de champs pertinents. Exemple:
  deux nodes de supervision peuvent partager la même tranche “alarmes + énergie”
  sans pour autant échanger tout l'état du robot.

Quality
  ``Quality`` décrit la fiabilité d'une valeur, pas l'état métier du système.
  Exemple: une distance peut être présente mais de qualité faible si le capteur
  lidar est partiellement aveuglé.

Message, schema, and transport terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

QoS
  ``QoS`` veut dire ``Quality of Service`` et décrit comment ROS 2 transporte un
  message. Exemple: ``reliable`` cherche la livraison fiable, ``best_effort``
  accepte des pertes, ``volatile`` n'envoie pas l'historique aux nouveaux
  abonnés, ``transient_local`` garde un historique local, et ``keep_last`` limite
  le nombre d'échantillons conservés.

Schema
  Un schéma est la forme attendue d'un message ou d'une structure de données.
  Exemple: un schéma peut imposer qu'un ``StateSample`` contienne un chemin, une
  valeur, une qualité et un timestamp source.

Wire format
  Le wire format est la forme réellement transportée sur le réseau ou par ROS 2.
  Exemple: un message ROS 2 ``StateUpdate.msg`` devient un contrat de transport
  même si les classes Python internes changent.

description_version
  ``description_version`` est un marqueur de version du schéma ou de la
  description utilisée. Exemple: un consommateur peut vérifier qu'il lit bien la
  version 3 de la description avant d'interpréter un update.

sequence
  ``sequence`` est un repère d'ordre pour détecter les pertes, doublons ou
  inversions de messages. Exemple: si un abonné reçoit 41 puis 43, il peut
  soupçonner que 42 a été perdu.

Identity and time terms
~~~~~~~~~~~~~~~~~~~~~~~

Canonical path
  Un canonical path est le chemin stable et normalisé utilisé comme clé logique
  d'un champ d'état. Exemple: ``battery/pack/main/voltage``. Il doit rester
  stable entre exports, redémarrages et copies partielles de registry.

deterministic identity
  Une identité déterministe est calculée à partir d'une logique stable plutôt
  que tirée au hasard. Exemple: un capteur monté sur ``robot/front/lidar`` peut
  garder la même identité calculée à chaque redémarrage.

path-derived UUID
  Un UUID dérivé d'un chemin est un identifiant calculé à partir d'une clé stable,
  comme un chemin d'état ou un nom canonique. Exemple: ``battery/pack/main`` peut
  produire toujours le même UUID tant que ce chemin ne change pas.

source timestamp
  Le ``source timestamp`` indique quand la valeur a été observée à la source,
  par exemple au moment où le capteur matériel a fait sa mesure. C'est utile pour
  distinguer une vieille mesure bien transportée d'une mesure réellement récente.

publish timestamp
  Le ``publish timestamp`` indique quand le message a été envoyé sur le transport,
  par exemple par un publisher ROS 2. Si le capteur mesure à 10:00:00 mais publie
  à 10:00:02, ces deux temps ne racontent pas la même chose.

stale
  Une valeur est ``stale`` quand elle est trop ancienne pour rester digne de
  confiance dans le contexte courant. Exemple: une position GPS vieille de 5
  secondes peut être acceptable pour un journal, mais trop vieille pour piloter.

Architecture warning terms
~~~~~~~~~~~~~~~~~~~~~~~~~~

manager
  ``Manager`` est un mot dangereux en architecture parce qu'il cache souvent une
  classe fourre-tout qui décide trop de choses. Exemple: un hypothétique
  ``StateManager`` pourrait finir par mélanger stockage, réseau, règles métier et
  lifecycle, ce que Sprint 17 veut précisément éviter.

orchestration
  L'orchestration désigne un contrôle centralisé qui pilote plusieurs étapes ou
  acteurs selon un scénario global. Exemple: un système qui dicterait à tous les
  nouds quand charger, publier, commander et se synchroniser serait une forme
  d'orchestration centrale.

plugin framework
  Un plugin framework permet de charger dynamiquement des comportements ou des
  extensions. Exemple: un système qui découvre au runtime des modules de calcul
  d'état à partir d'un dossier de plugins serait un plugin framework, ce qui n'est
  pas un objectif de Sprint 17.

code generation / codegen
  Le code generation, ou ``codegen``, est la production automatique de code à
  partir de déclarations ou de schémas. Exemple: générer automatiquement des
  classes Python et des messages ROS 2 depuis une description d'état serait du
  codegen, mais ce projet n'en veut pas à ce stade.

Review note
-----------

Ce glossaire décrit le vocabulaire de Sprint 17 sans créer de runtime, de
package ROS 2, de package Python ni de contrat ABI effectif.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
