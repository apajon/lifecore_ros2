Sprint 17.12 — Lightweight Static Verification
===============================================

**Track.** Architecture / Research.

**Type.** Verification.

**Objective.** Run lightweight automated checks to verify Sprint 17 compliance
before formal review.

Context
-------

Automated checks catch common mistakes:

- Missing mandatory phrases
- Unwanted files
- Build configuration changes
- Terminology violations
- Scope creep

Verification Report Location
----------------------------

**File:** ``lifecore_state/rfcs/sprint_17_static_check.rst``

Required Content
-----------------

The report documents:

1. **Purpose**
   Lightweight static verification of Sprint 17 deliverables

2. **Verification method**

   Describe checks performed:
   - File/folder existence
   - File absence checks (no package.xml, no .msg, no build files)
   - Grep checks for forbidden terms
   - Grep checks for required terminology
   - Mandatory phrase presence

3. **Verification checks**

   Checklist of checks performed:

   **File structure checks:**
   - [ ] ``lifecore_state/`` exists
   - [ ] ``lifecore_state/package.xml`` does NOT exist
   - [ ] ``lifecore_state/rfcs/`` exists
   - [ ] All required .rst files exist
   - [ ] No .msg files present
   - [ ] No CMakeLists.txt in lifecore_state/
   - [ ] No build metadata added to parent

   **Terminology checks (via grep):**
   - [ ] No "SmartValue" outside explanations
   - [ ] No "CommManager" outside explanations
   - [ ] No "giant manager" outside anti-goals
   - [ ] "StateDescriptor" present in appropriate docs
   - [ ] "StateDescription" present in appropriate docs
   - [ ] "StateSample" present in appropriate docs
   - [ ] "StateUpdate" present in appropriate docs
   - [ ] "StateCommand" present in appropriate docs

   **Semantic checks:**
   - [ ] No "lifecore_state_msgs" implemented as real package
   - [ ] No "lifecore_state_core" implemented as real package
   - [ ] No "lifecore_state_ros" implemented as real package
   - [ ] No Python runtime code in lifecore_state/
   - [ ] No compilable message definitions

   **Mandatory phrase checks:**
   - [ ] sprint_17_lifecore_state_rfc.rst contains mandatory phrase
   - [ ] repository_audit.rst contains mandatory phrase
   - [ ] README.rst contains mandatory phrase
   - [ ] rfcs/README.rst contains mandatory phrase
   - [ ] rfc_001_lifecore_state_architecture.rst contains mandatory phrase
   - [ ] terminology.rst contains mandatory phrase
   - [ ] message_semantics.rst contains mandatory phrase
   - [ ] lifecycle_state_separation.rst contains mandatory phrase
   - [ ] anti_goals.rst contains mandatory phrase
   - [ ] package_boundaries.rst contains mandatory phrase

4. **Verification results**

   For each check:
   - Result (PASS / FAIL / WARNING)
   - Details if not PASS
   - Files involved
   - Command/method used

5. **Anomalies found**

   If any verification fails:
   - Anomaly description
   - Severity (CRITICAL / HIGH / MEDIUM / LOW)
   - Files affected
   - Recommended action

6. **Recommendations**

   - Which anomalies require immediate fixing
   - Which can be deferred
   - Which need human review

7. **Build integrity**

   Document:
   - Sphinx build succeeded (if applicable)
   - RST syntax valid
   - No broken references
   - No .gitignore violations

Acceptance Criteria
-------------------

- [ ] Verification report complete
- [ ] All checks documented
- [ ] Results clear (PASS/FAIL/WARNING)
- [ ] Anomalies clearly identified
- [ ] No critical issues outstanding
- [ ] Recommendations actionable
- [ ] Mandatory phrase included

Example Verification Commands
------------------------------

(Not code, just documentation of what was checked):

.. code-block:: bash

    # Check forbidden files
    find lifecore_state/ -name package.xml
    find lifecore_state/ -name "*.msg"
    find lifecore_state/ -name CMakeLists.txt

    # Check for weak terminology
    grep -r "SmartValue" lifecore_state/
    grep -r "CommManager" lifecore_state/

    # Check for required terminology
    grep -r "StateDescriptor" lifecore_state/rfcs/rfc_001*
    grep -r "lifecycle.state.separation" lifecore_state/

    # Check mandatory phrases
    grep -r "ChatGPT ou Codex relira" lifecore_state/

Success Criteria
----------------

All checks pass or have documented rationale for non-compliance.

No critical anomalies remain before formal review.

Build is clean and documentation is valid RST.
