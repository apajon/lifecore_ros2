Sprint planning
===============

9 sprints structurés pour étendre lifecore_ros2 post-1.0 sans dérive architecturale.

Chaque sprint = **livrable concret + stable + testable**.

---

Principes
---------

- **Pas de mélange de sprints.** Chacun isolé, revue-able, backportable.
- **Pas de couplage prématuré.** ServiceComponent ne connaît pas Factory; Factory connaît Registry.
- **Définition de done.** Chaque sprint a une défition claire: code + tests + doc.
- **Risques nommés.** Pièges identifiés et mitigation avant de coder.

---

Roadmap des sprints
-------------------

.. toctree::
   :maxdepth: 1

   sprint_1_service_client
   sprint_2_error_handling
   sprint_3_testing_infrastructure
   sprint_4_real_examples
   sprint_5_callback_gating
   sprint_6_concurrency
   sprint_7_lifecycle_policies
   sprint_8_observability
   sprint_9_parameters
   sprint_10_factory

---

Vue condensée
-------------

::

   S1: Service/Client components (primitives ROS2)
   S2: Error handling solide (fiabilité lifecycle)
   S3: Testing infrastructure (accélération)
   S4: Real examples v1 (validation API)
   S5: Callback gating centralisé (homogénéité)
   S6: Concurrency propre (multi-thread)
   S7: Lifecycle policies (configurabilité)
   S8: Observability minimale (debug)
   S9: Parameters (config runtime)
   S10: Factory minimal (instanciation dynamique)

---

Hors roadmap immediate
----------------------

**Ne pas inclure dans ces sprints:**

- SpecModel / AppSpec
- ActionComponent (après S1)
- Binding layer (si jamais)
- Contrôle robotique avancé (hors scope core)

---

Dépendances entre sprints
--------------------------

::

   S1 (Service/Client)
   S2 (Error handling)     ← dépend de tous (appliqué rétro)
   S3 (Tests)              ← utilisé par S2+
   S4 (Callback gating)    ← appliqué à S1
   S5 (Concurrency)        ← prépare multi-thread
   S6 (Policies)           ← indépendant, mais avant S8
   S7 (Observability)      ← indépendant
   S8 (Parameters)         ← optionnellement avec S6
   S9 (Factory)            ← dernier, se repose sur S1-S8

**Recommended sequencing:**

1. S3 (tests) avant tout — fixtured et outillage
2. S1 (primitives) — surface d'API
3. S2 (error handling) — retroactively hardens S1
4. S4 (callback gating) — refactor commun
5. S5 (concurrency) — préparer scalability
6. S6 + S7 (policies + observability) — configurabilité
7. S8 (parameters) — config runtime
8. S9 (factory) — dynamique

---

Definition of Done (toutes sprints)
-----------------------------------

Chaque sprint doit satisfaire:

- ✓ Code avec docstrings Google
- ✓ Tests unitaires (nominal + edge cases)
- ✓ Tests d'intégration (avec autres composants si applicable)
- ✓ Regression tests si bug fix
- ✓ Linting Ruff + Pyright + Pytest ✓
- ✓ Documentation (docstrings + design notes si architecture)
- ✓ CONTRIBUTING.md updated si new patterns
- ✓ Example(s) si surface utilisateur

---

Format de chaque sprint
-----------------------

Chaque fichier sprint contient:

- **Objectif** — ce qui se vend à la fin
- **Contenu** — listes de classes, méthodes, comportements
- **Tests à écrire** — checklist
- **Risques** — pièges nommés + mitigation
- **Dépendances** — ce qui doit être fait avant
- **Scope boundaries** — ce qui ne s'inclurait PAS
- **Success signal** — comment valider que c'est bon

---

Notes d'exécution
-----------------

- Chaque sprint = une branche ou un ensemble de commits logiques
- Code review par sprint, pas par ligne
- Si un sprint tire un découplage, faire un mini-refactor en parallèle (pas dans le sprint, avant ou après)
- Ne pas faire de « et au fait, améliorons l'architecture » dans un sprint — note-le pour un sprint dédié
