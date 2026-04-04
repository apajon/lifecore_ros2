Oui. Voici une **todo list structurée** et exploitable par des agents de code, alignée avec ce qu’on a déjà décidé.

# TODO globale `lifecore_ros2`

## 0. État actuel déjà acquis

### Repo / tooling

* [x] Repo GitHub privé initialisé
* [x] Nom du projet fixé: `lifecore_ros2`
* [x] Tagline fixée: `A composable lifecycle framework for ROS 2`
* [x] `pyproject.toml` en place
* [x] `ruff` configuré
* [x] `pre-commit` configuré
* [x] workflow GitHub Actions de release/versionning défini
* [x] stratégie lifecycle-native fixée
* [x] pas de machine à états parallèle globale
* [x] `SubscriberComponent`, `PublisherComponent`, `TopicComponent` déplacés dans `components/`

### Core runtime

* [x] `ComposedLifecycleNode` créé
* [x] `LifecycleComponent` créé
* [x] usage de `ManagedEntity` retenu comme base lifecycle native ROS2

---

# 1. Stabiliser l’architecture du package

## 1.1 Vérifier l’arborescence finale

Objectif: éviter la dérive de structure.

Structure cible:

```text
src/lifecore_ros2/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── composed_lifecycle_node.py
│   └── lifecycle_component.py
├── components/
│   ├── __init__.py
│   ├── topic_component.py
│   ├── subscriber_component.py
│   └── publisher_component.py
└── _version.py  # généré
```

### À faire

* [x] vérifier que tous les fichiers `__init__.py` existent
* [x] vérifier que les imports internes sont cohérents après déplacement
* [x] vérifier les réexports publics dans `src/lifecore_ros2/__init__.py`
* [x] vérifier les réexports dans `core/__init__.py` et `components/__init__.py`

---

# 2. Rendre le noyau minimal réellement exécutable

## 2.1 Valider `ComposedLifecycleNode`

### À faire

* [x] vérifier que `add_component()` enregistre bien les composants comme managed entities
* [x] vérifier qu'un double enregistrement du même nom échoue proprement
* [x] vérifier que `get_component()` a un comportement propre en cas d'absence
* [x] vérifier que les logs sont propres et sobres

## 2.2 Valider `LifecycleComponent`

### À faire

* [x] vérifier qu'un component non attaché échoue proprement si `node` est utilisé
* [x] vérifier qu'un double `attach()` échoue proprement
* [x] vérifier que les hooks lifecycle retournent bien `TransitionCallbackReturn.SUCCESS` par défaut
* [x] vérifier qu'aucune logique parasite n'a été ajoutée

## 2.3 Corriger les overrides lifecycle dans les composants

### À faire

* [x] `SubscriberComponent` et `PublisherComponent` overrident `_on_*` (points d'extension) au lieu de `on_*` (méthodes gardées)
* [x] les appels `super()` pointent vers `_on_*` parents
* [x] le décorateur `lifecycle_guard_component` n'est plus bypassé
* [x] renommer `publisher_componenet.py` → `publisher_component.py` (typo corrigée)

---

# 3. Finaliser les composants topic

## 3.1 `TopicComponent`

### À faire

* [ ] vérifier que `topic_name`, `msg_type`, `qos_profile` sont bien stockés proprement
* [ ] vérifier le typage minimal correct
* [ ] vérifier que la classe reste légère et abstraite conceptuellement
* [ ] éviter toute logique ROS active dedans

## 3.2 `SubscriberComponent`

### À faire

* [ ] vérifier que la subscription est créée uniquement au `on_configure`
* [ ] vérifier que les messages sont ignorés tant que le composant n’est pas actif
* [ ] vérifier que le cleanup détruit bien la subscription
* [ ] vérifier que `_is_active` est correctement géré sur activate/deactivate/cleanup
* [ ] vérifier que la méthode abstraite `on_message()` est bien le point d’entrée métier
* [ ] vérifier qu’aucun message n’est traité hors activation

## 3.3 `PublisherComponent`

### À faire

* [ ] vérifier que le publisher est créé uniquement au `on_configure`
* [ ] vérifier que le cleanup détruit bien le publisher
* [ ] vérifier que `publish()` échoue proprement si non configuré
* [ ] vérifier que `publish()` échoue proprement si inactif
* [ ] vérifier que `_is_active` est correctement géré sur activate/deactivate/cleanup

---

# 4. Ajouter un exemple runnable minimal

## 4.1 Exemple simple de node lifecycle composé

But: prouver que l’architecture marche réellement.

### À faire

* [x] créer `examples/minimal_node.py`
* [x] y définir un `ComposedLifecycleNode`
* [x] y enregistrer au moins un `LifecycleComponent`
* [x] loguer les transitions `configure`, `activate`, `deactivate`, `cleanup`

## 4.2 Exemple subscriber concret

### À faire

* [x] créer un exemple `SubscriberComponent` avec `std_msgs/msg/String`
* [x] loguer les messages reçus
* [ ] démontrer que les messages sont ignorés hors activation

## 4.3 Exemple publisher concret

### À faire

* [ ] créer un exemple `PublisherComponent`
* [ ] publier périodiquement ou via méthode explicite
* [ ] démontrer l’échec contrôlé si publication hors activation

---

# 5. Ajouter des tests minimaux

## 5.1 Tests du core

### À faire

* [x] tester `add_component()`
* [x] tester le refus des noms dupliqués
* [x] tester `get_component()`
* [x] tester le comportement d’un component non attaché
* [x] tester le double `attach()`

## 5.2 Tests lifecycle

### À faire

* [x] tester que les hooks lifecycle des composants sont bien appelés
* [x] tester qu’un composant qui échoue au `configure` provoque un échec global
* [x] tester activate/deactivate/cleanup sur un composant instrumenté

## 5.3 Tests components topic

### À faire

* [x] tester que `SubscriberComponent` n’appelle pas `on_message()` si inactif
* [x] tester que `SubscriberComponent` appelle `on_message()` si actif
* [x] tester que `PublisherComponent.publish()` échoue si non configuré
* [x] tester que `PublisherComponent.publish()` échoue si inactif

Note:

* [x] décider si ces tests sont de vrais tests ROS2 ou des tests unitaires avec doubles/mocks minimaux → tests unitaires avec `rclpy.init()` réel, mocks minimaux pour les ressources ROS internes
* [x] commencer simple, ne pas partir sur une usine à tests d'intégration

---

# 6. Nettoyer l’API publique

## À faire

* [x] décider ce qui est public depuis `lifecore_ros2`
* [x] réexporter seulement les classes utiles:

  * [x] `ComposedLifecycleNode`
  * [x] `LifecycleComponent`
  * [x] `TopicComponent`
  * [x] `SubscriberComponent`
  * [x] `PublisherComponent`
* [x] éviter d'exposer des symboles internes inutiles

---

# 7. Documenter la V0 minimale

## 7.1 README

### À faire

* [ ] ajouter une section “What is lifecore_ros2?”
* [ ] ajouter une section “Design principles”
* [ ] ajouter une section “Minimal example”
* [ ] ajouter une section “Current status”
* [ ] ajouter une section “Roadmap”

## 7.2 Principes à documenter explicitement

### À écrire

* [ ] ROS2 lifecycle est le centre du design
* [ ] aucune machine à états parallèle globale
* [ ] le node orchestre, les components exécutent
* [ ] les subscriptions peuvent exister avant activation, mais le traitement métier est gate par l’activation
* [ ] `TopicComponent` est une base commune, pas un mega composant

---

# 8. Finaliser le versionning/release

## À faire

* [ ] vérifier que `setuptools-scm` génère correctement `_version.py`
* [ ] vérifier que `python-semantic-release` est cohérent avec le workflow GitHub Action
* [ ] vérifier que le workflow release ne se déclenche que selon la stratégie retenue
* [ ] créer le premier tag `v0.0.1` si ce n’est pas déjà fait
* [ ] vérifier qu’un futur bump automatique produit bien des tags au format `vX.Y.Z`

---

# 9. Préparer la suite V1, sans encore l’implémenter

## À garder en backlog, pas maintenant

### Config / specs

* [ ] introduire `SpecModel`
* [ ] introduire `AppSpec`
* [ ] introduire `ComponentSpec`
* [ ] introduire les specs de composants topic

### Factory / registry

* [ ] introduire `ComponentRegistry`
* [ ] introduire `ComponentFactory`
* [ ] introduire `SpecLoader`

### Components supplémentaires

* [ ] `TimerComponent`
* [ ] `ServiceComponent`
* [ ] `ActionComponent`

### Binding plus avancé

* [ ] décider si un niveau “binding” dédié est nécessaire
* [ ] ne l’ajouter que si les components deviennent trop chargés

---

# 10. Règles à ne pas violer

## Contraintes de conception

* [ ] ne pas recréer une machine à états applicative parallèle
* [ ] ne pas réintroduire un “manager” flou
* [ ] ne pas transformer `TopicComponent` en classe fourre-tout
* [ ] ne pas introduire trop tôt de config magique
* [ ] ne pas introduire trop tôt de plugin loading dynamique
* [ ] rester lifecycle-native ROS2
* [ ] garder le node léger
* [ ] garder les composants spécialisés et bornés

---

# Priorité recommandée

## Priorité 1

* [x] stabiliser l'arborescence et les imports
* [x] rendre le core exécutable
* [x] créer un exemple runnable minimal

## Priorité 2

* [x] ajouter les tests minimaux
* [x] nettoyer l'API publique
* [ ] améliorer le README

## Priorité 3

* [ ] préparer les specs Pydantic
* [ ] préparer registry/factory
* [ ] ajouter d’autres types de components

---
