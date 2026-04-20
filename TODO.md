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
* [x] `LifecycleSubscriberComponent`, `LifecyclePublisherComponent`, `TopicComponent` déplacés dans `components/`

### Core runtime

* [x] `LifecycleComponentNode` créé (anciennement `ComposedLifecycleNode`)
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

## 2.1 Valider `LifecycleComponentNode`

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

* [x] `LifecycleSubscriberComponent` et `LifecyclePublisherComponent` overrident `_on_*` (points d'extension) au lieu de `on_*` (méthodes gardées)
* [x] les appels `super()` pointent vers `_on_*` parents
* [x] le décorateur `lifecycle_guard_component` n'est plus bypassé
* [x] renommer `publisher_componenet.py` → `publisher_component.py` (typo corrigée)

---

# 3. Finaliser les composants topic

## 3.1 `TopicComponent`

### À faire

* [x] vérifier que `topic_name`, `msg_type`, `qos_profile` sont bien stockés proprement
* [x] vérifier le typage minimal correct
* [x] vérifier que la classe reste légère et abstraite conceptuellement
* [x] éviter toute logique ROS active dedans

## 3.2 `LifecycleSubscriberComponent`

### À faire

* [x] vérifier que la subscription est créée uniquement au `_on_configure`
* [x] vérifier que les messages sont ignorés tant que le composant n’est pas actif
* [x] vérifier que le cleanup détruit bien la subscription
* [x] vérifier que `_is_active` est correctement géré sur activate/deactivate/cleanup
* [x] vérifier que la méthode abstraite `on_message()` est bien le point d’entrée métier
* [x] vérifier qu’aucun message n’est traité hors activation

## 3.3 `LifecyclePublisherComponent`

### À faire

* [x] vérifier que le publisher est créé uniquement au `_on_configure`
* [x] vérifier que le cleanup détruit bien le publisher
* [x] vérifier que `publish()` échoue proprement si non configuré
* [x] vérifier que `publish()` échoue proprement si inactif
* [x] vérifier que `_is_active` est correctement géré sur activate/deactivate/cleanup

---

# 4. Ajouter un exemple runnable minimal

## 4.1 Exemple simple de node lifecycle composé

But: prouver que l’architecture marche réellement.

### À faire

* [x] créer `examples/minimal_node.py`
* [x] y définir un `LifecycleComponentNode`
* [x] y enregistrer au moins un `LifecycleComponent`
* [x] loguer les transitions `configure`, `activate`, `deactivate`, `cleanup`

## 4.2 Exemple subscriber concret

### À faire

* [x] créer un exemple `LifecycleSubscriberComponent` avec `std_msgs/msg/String`
* [x] loguer les messages reçus
* [x] démontrer que les messages sont ignorés hors activation

## 4.3 Exemple publisher concret

### À faire

* [x] créer un exemple `LifecyclePublisherComponent`
* [x] publier périodiquement ou via méthode explicite
* [x] démontrer l’échec contrôlé si publication hors activation

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

* [x] tester que `LifecycleSubscriberComponent` n'appelle pas `on_message()` si inactif
* [x] tester que `LifecycleSubscriberComponent` appelle `on_message()` si actif
* [x] tester que `LifecyclePublisherComponent.publish()` échoue si non configuré
* [x] tester que `LifecyclePublisherComponent.publish()` échoue si inactif

Note:

* [x] décider si ces tests sont de vrais tests ROS2 ou des tests unitaires avec doubles/mocks minimaux → tests unitaires avec `rclpy.init()` réel, mocks minimaux pour les ressources ROS internes
* [x] commencer simple, ne pas partir sur une usine à tests d'intégration

---

# 6. Nettoyer l’API publique

## À faire

* [x] décider ce qui est public depuis `lifecore_ros2`
* [x] réexporter seulement les classes utiles:

  * [x] `LifecycleComponentNode`
  * [x] `LifecycleComponent`
  * [x] `TopicComponent`
  * [x] `LifecycleSubscriberComponent`
  * [x] `LifecyclePublisherComponent`
* [x] éviter d'exposer des symboles internes inutiles

---

# 7. Documenter la V0 minimale

## 7.1 README

### À faire

* [x] ajouter une section “What is lifecore_ros2?”
* [x] ajouter une section “Design principles”
* [x] ajouter une section “Minimal example”
* [x] ajouter une section “Current status”
* [x] ajouter une section “Roadmap”

## 7.2 Principes à documenter explicitement

### À écrire

* [x] ROS2 lifecycle est le centre du design
* [x] aucune machine à états parallèle globale
* [x] le node orchestre, les components exécutent
* [x] les subscriptions peuvent exister avant activation, mais le traitement métier est gate par l’activation
* [x] `TopicComponent` est une base commune, pas un mega composant

---

# 8. Finaliser le versionning/release

## À faire

* [x] vérifier que `setuptools-scm` génère correctement `_version.py`
* [x] vérifier que `python-semantic-release` est cohérent avec le workflow GitHub Action
* [x] vérifier que le workflow release ne se déclenche que selon la stratégie retenue
* [x] créer le premier tag `v0.0.1` si ce n’est pas déjà fait
* [x] vérifier qu’un futur bump automatique produit bien des tags au format `vX.Y.Z`

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
* [ ] `ParameterComponent`

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
* [x] améliorer le README

## Priorité 3

* [ ] préparer les specs Pydantic
* [ ] préparer registry/factory
* [ ] ajouter d’autres types de components

---
# 11. 0.1.0 Release messaging and assets (backlog)

## 7.4 Draft GitHub release text (0.1.0)

**Status**: Backlog. To be executed after CI validation (§6.6) and release flow rehearsal (§6.7) confirm green.

**Context**: This is the public announcement vehicle for the first release. Messaging must be coherent, anchored to the canonical positioning, and immediately convey the value and scope of `lifecore_ros2 v0.1.0`.

### Goal

Draft a GitHub release page text (`.github/RELEASE_NOTES_v0.1.0.md` or equivalent) that:
- Opens with the canonical positioning sentence (99 chars, quoted verbatim from `pyproject.toml`)
- Explains what this 0.1.0 provides in clear, scannable sections
- States supported Python and ROS 2 versions explicitly
- Lists known limitations and what is intentionally deferred
- Provides links to README, docs, and contributing guidelines
- Sets tone as a **beta-ready, lifecycle-correct foundation**, not a "production-ready framework"

### Messaging Architecture

**Messaging layers** (top to bottom):
1. **Headline** (1 line): Canonical sentence verbatim
2. **Quick summary** (2–3 sentences): What problem this solves, what you can do now
3. **Key features** (bullet list, 4–6 items): Concrete behaviors provided (node composition, component lifecycle, pub/sub gating, error handling, typing)
4. **What's included** (section): Core library, minimal examples, full lifecycle tests, API stability promise
5. **Supported platforms** (table or inline): Python 3.12+, ROS 2 Jazzy
6. **Known limitations** (bullet list): No dynamic plugin loading, no app framework, no hidden state machine (not a limitation, a feature—rephrase as a promise)
7. **Next steps** (section): Links to README, docs, contributing, companion examples roadmap
8. **Acknowledgments** (optional): Any open-source or community inspiration (minimal for v0.1.0)

**Tone rules**:
- Technical, direct, no hyperbole ("reliable" not "revolutionary")
- Honest about stability ("0.1.0 beta" implications)
- Lifecycle-first language (configure, activate, deactivate, cleanup)
- No marketing jargon; no "game-changer" or "powerful abstraction"

### Lifecycle Behavior Contract

**N/A** — release messaging is not lifecycle code. However, messaging itself must follow these rules:
- **Consistency** (config phase): all links and version strings must be verified before publishing
- **Gating** (activation phase): messaging review must be completed before semantic-release is triggered
- **Cleanup** (post-release): any stale positioning statements in docs/README must be updated to reflect 0.1.0 publicly available

### Impacted Modules

| Module | Impact | Why |
|--------|--------|-----|
| `.github/RELEASE_NOTES_v0.1.0.md` (new) | **primary** | GitHub release text lives here or is rendered directly into release page |
| `README.md` | read-only reference | release text links to README; must not contradict |
| `docs/architecture.rst` | read-only reference | release text may link to architecture docs |
| `CHANGELOG.md` | read-only reference | semantic-release generates changes from commits; release text summarizes |
| `CONTRIBUTING.md` | read-only reference | release text links to contributing guide |
| `.github/workflows/release.yml` | no change | release flow itself unchanged |
| `pyproject.toml` | read-only reference | canonical sentence sourced here; version auto-incremented by semantic-release |

**Validation surfaces**:
- Local Markdown linting (`markdownlint` or similar, if available)
- Link validation (README, docs links must resolve)
- Tone review (human, not automated)
- Cross-reference check (all version strings, supported versions, links must align)

### Acceptance Criteria

**Messaging criteria** (testable):
1. [ ] Release text opens with canonical sentence **verbatim** from `pyproject.toml` `project.description`
2. [ ] Supported Python version matches `pyproject.toml` `requires-python = ">=3.12"`
3. [ ] Supported ROS 2 version explicitly states "ROS 2 Jazzy"
4. [ ] All internal links (README, docs, CONTRIBUTING) resolve without broken anchors
5. [ ] Tone is technical and honest (no hyperbole; β-version framing explicit)
6. [ ] "What's included" section lists exactly: core library, 5 examples, full lifecycle tests, public API
7. [ ] "Known limitations" section references the 3 explicit non-goals from README (no app framework, no dynamic plugins, no parallel state machine)
8. [ ] No version numbers are hardcoded except "0.1.0" (all other versions sourced from `pyproject.toml` or docs)
9. [ ] Text is 500–800 words (scannable, not overwhelming)
10. [ ] Links to companion examples roadmap (with "planned — not yet published" marker)

**Structural criteria** (testable):
1. [ ] File location and naming follow GitHub conventions (e.g., release page auto-populated, or `RELEASE_NOTES_v0.1.0.md` in `.github/`)
2. [ ] No local file paths; all links are to public URLs (GitHub, Read the Docs, etc.)
3. [ ] Markdown renders cleanly on GitHub (no broken tables, code blocks, or emphasis)

**No-contradiction criteria** (automated check possible):
1. [ ] Canonical sentence matches exactly in README, docs, CHANGELOG, and release text
2. [ ] Python version claim matches `requires-python`
3. [ ] ROS 2 version claim matches docs (`docs/getting_started.rst`, `docs/requirements.txt`)
4. [ ] Supported platforms list is consistent across all release-related files

### Validation Plan

**Exit gates before publishing**:
1. **Gate 1 — CI green** (§6.6 prerequisite):
   - `uv run ruff check .` and `uv run ruff format --check .` pass
   - `uv run pyright` has zero errors
   - `uv run pytest` passes 100%
   - Docs build clean: `uv run --group docs python -m sphinx -b html docs docs/_build/html`

2. **Gate 2 — Release flow dry-run** (§6.7 prerequisite):
   - `uv run --group release semantic-release version --print --no-push` computes `0.1.0` without errors
   - Tag naming verified: next release would be `v0.1.0`
   - Build succeeds: `python -m build`
   - Tarball valid: `twine check dist/*`

3. **Gate 3 — Messaging consistency**:
   - [ ] Run `grep -F "minimal lifecycle composition library for ROS 2 Jazzy" README.md docs/architecture.rst docs/index.rst CHANGELOG.md` — all occurrences must be identical (canonical sentence)
   - [ ] Run `grep -F "Python 3.12" docs/getting_started.rst pyproject.toml` — version claims consistent
   - [ ] Run `grep -F "ROS 2 Jazzy" docs/getting_started.rst CONTRIBUTING.md` — all references consistent
   - [ ] Manual link check: click every URL in release text; verify no 404s or stale anchors

4. **Gate 4 — Tone and readability review**:
   - [ ] Read release text aloud or have someone else read it — verify tone is direct and honest, not overselling
   - [ ] Verify no hyperbole ("powerful", "revolutionary", "game-changer")
   - [ ] Verify β-version status explicit ("0.1.0 beta", "early release", "API may evolve")
   - [ ] Verify acknowledgment of what is NOT included (no app framework, no magic)

5. **Gate 5 — Word count and structure**:
   - [ ] Release text is 500–800 words (use `wc -w` on the `.md` file)
   - [ ] All sections present: headline, summary, features, what's included, supported platforms, limitations, next steps
   - [ ] Bulleted lists are 4–6 items each (scannable, not overwhelming)

### Failure Modes and Mitigations

| Failure Mode | Impact | Mitigation |
|--------------|--------|-----------|
| **Inconsistent positioning** — canonical sentence differs in release vs README | High (confuses users) | Gate 3: automated grep validation |
| **Broken links** — docs or examples links 404 | High (credibility loss) | Gate 3: manual link validation before publish |
| **Unsupported version claims** — release says "Python 3.11 supported" but `pyproject.toml` says "3.12+" | High (setup failures, support chaos) | Gate 3: version consistency check |
| **Overselling stability** — tone implies production-ready when 0.1.0 is beta | Medium (scope creep, broken promises) | Gate 4: tone review; add explicit "beta" marker |
| **Too long** — release text >1000 words | Medium (users don't read, boring) | Gate 5: word-count check |
| **Missing non-goals** — release doesn't clarify what is NOT included | Medium (expectations mismatch) | Acceptance criterion #7; gate 4 review |
| **Stale companion-repo reference** — release links to `lifecore_ros2_examples` as if it's public when it's not | Medium (404 or confusion) | Acceptance criterion #10; explicit "planned" marker required |
| **Version string hardcoded** — release says "v0.1.0" in multiple places, making it hard to copy-paste for v0.2.0 | Low (maintenance burden) | Acceptance criterion #8; use semantic-release template variables if available |

### Non-Goals

- **LinkedIn, Discourse, Reddit, or direct messages**: User explicitly deferred these. This brief covers GitHub release only.
- **Video or animated demo**: Out of scope for this task.
- **Detailed API reference**: Release text is a landing page, not API docs (docs and README handle that).
- **Full changelog generation**: Semantic-release auto-generates commits-to-changelog; release text is a curated summary layer on top.
- **External platform coordination**: No scheduling, no embargo coordination, no press releases.
- **Localization**: Release text is English only for 0.1.0.

### Clarifications / Decisions Locked

1. **Release notes storage**: Compose directly in the GitHub release UI (simpler, no version history burden).
   - **Decision**: Store text in GitHub release body directly; do not create `.github/RELEASE_NOTES_v0.1.0.md`.

2. **Changelog and release notes relationship**: Semantic-release generates a CHANGELOG from commits. Release text is a curated summary layer.
   - **Decision**: CHANGELOG.md is auto-generated (commits → features/fixes). Release text is human-curated (strategic messaging). Both coexist; release text may link to CHANGELOG.

3. **Companion examples repo status in release text**: Include explicit "planned — not yet published" marker.
   - **Decision**: Keep the marker. Users will ask; better to acknowledge than stay silent. Links to `ROADMAP_lifecore_ros2_examples.md` for clarity.

4. **Tone calibration**: Use "beta" frame for 0.1.0.
   - **Decision**: Explicitly frame as "0.1.0 beta". Avoids "experimental" (too tentative) and "production-ready" (false). Lifecycle tests are robust; API may evolve.

5. **Code examples in release text**: No code snippets.
   - **Decision**: Release text is messaging layer only. README has examples; release text is the landing page. Keep them separate.

### Exit Gate Summary

**Release text is ready to publish when**:
- [ ] All 5 validation gates pass
- [ ] All 10 acceptance criteria verified
- [ ] No failure modes active
- [ ] Clarifications #1–#5 resolved and documented (as a comment in the `.md` file or in a separate decision log)
- [ ] Semantic-release dry-run confirms 0.1.0 will be applied
- [ ] Human tone review completed (2+ reviewers if possible)
- [ ] Backup plan ready: if release text is published and an error is found, can we fix it in a v0.1.1 correction release?

---
