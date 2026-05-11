# CHANGELOG

<!-- version list -->

## v0.9.0 (2026-05-11)

### Bug Fixes

- **testing**: Correct fixture return type annotation for cleanup_policy test
  ([`23d1ce1`](https://github.com/apajon/lifecore_ros2/commit/23d1ce1a566c6f6e4d692cb63d998c89e2c88140))

### Chores

- **changelog**: Add v0.10.0 entry
  ([`a5f8488`](https://github.com/apajon/lifecore_ros2/commit/a5f8488aaf5658ecedb980a906feddcc64479dfd))

- **changelog**: Remove unreleased entries ahead of git tags
  ([`48004f6`](https://github.com/apajon/lifecore_ros2/commit/48004f650d70e159f1ab72c654578ea0a8326cc6))

- **copilot**: Make frontmatter hook command portable
  ([`e032cb0`](https://github.com/apajon/lifecore_ros2/commit/e032cb027983ef05b2e28b57a4636173c5748733))

- **prompts**: Replace logical commits with smart session flow
  ([`2b56227`](https://github.com/apajon/lifecore_ros2/commit/2b56227b4a34c9d1a0b9c790445a581b1055dbf3))

### Documentation

- **api**: Add core.health autodoc entry
  ([`e1db951`](https://github.com/apajon/lifecore_ros2/commit/e1db951dc4702bbccd6cd45aa87de61099a7b827))

- **api,examples,patterns**: Sync sphinx docs for watchdog
  ([`0bbcdd8`](https://github.com/apajon/lifecore_ros2/commit/0bbcdd899d556338f7da453c2be4f64d46cce942))

- **architecture**: Document Sprint 8 concurrency contract
  ([`087e892`](https://github.com/apajon/lifecore_ros2/commit/087e892eb093f3db2fd0d8aa70a93560b415593c))

- **architecture**: Document structured lifecycle logging contract
  ([`187d458`](https://github.com/apajon/lifecore_ros2/commit/187d4589b0dec1f23dd4510c53727bdd0c82ce25))

- **changelog**: Add v0.9.0 entry
  ([`581f93e`](https://github.com/apajon/lifecore_ros2/commit/581f93ec274672a536f8733c735a7e1d245c88cf))

- **examples**: Add minimal watchdog example
  ([`84fcfd8`](https://github.com/apajon/lifecore_ros2/commit/84fcfd815ce441fa782ce7d9800fefd260bece75))

- **planning**: Close sprint 9 and update sprint 10 scope
  ([`1fda0ad`](https://github.com/apajon/lifecore_ros2/commit/1fda0ad0a178a728d0ac498f9a1f88d0ba5f673c))

- **planning**: Mark Sprint 10 health status as delivered
  ([`25e2803`](https://github.com/apajon/lifecore_ros2/commit/25e28033000ec6e175497ffff469d80dc051da76))

- **planning**: Mark sprint 11 watchdog component as shipped
  ([`1eeb130`](https://github.com/apajon/lifecore_ros2/commit/1eeb13042262ce35c477bad0373eaded1ad8f82d))

- **planning**: Mark Sprint 8 as shipped (2026-05-08)
  ([`5aa2ee4`](https://github.com/apajon/lifecore_ros2/commit/5aa2ee4da57412ccba43add1473e06055760aeaf))

- **readme**: Add watchdog and health symbols
  ([`bbbbee1`](https://github.com/apajon/lifecore_ros2/commit/bbbbee16be94dd872867e154bb64c8ae01dab3ca))

### Features

- **components**: Add LifecycleWatchdogComponent
  ([`de2619f`](https://github.com/apajon/lifecore_ros2/commit/de2619f1f7bd6faa0a15fd24c456d3b8c3db1c1b))

- **core**: Add callback group registry and _active_lock thread safety
  ([`ca4518b`](https://github.com/apajon/lifecore_ros2/commit/ca4518bd4a5ce22acb07cda5d405a2ff91bfcc64))

- **core**: Add HealthStatus and HealthLevel API
  ([`34bffc8`](https://github.com/apajon/lifecore_ros2/commit/34bffc869b078289260cb4c1125aade452329d20))

- **core**: Add structured lifecycle logging
  ([`fcbe979`](https://github.com/apajon/lifecore_ros2/commit/fcbe979ec3617b0ec43e818b5d929694905a771e))

- **examples**: Add minimal_health_status example
  ([`e8c95a2`](https://github.com/apajon/lifecore_ros2/commit/e8c95a236307dfeed0f4875c4dbb75281403f56f))

### Testing

- **components**: Cover lifecycle watchdog behavior
  ([`f1f726f`](https://github.com/apajon/lifecore_ros2/commit/f1f726fbedd3c21fcf31cfe29b42766b94b5dce2))

- **core**: Add HealthStatus regression tests
  ([`7e22754`](https://github.com/apajon/lifecore_ros2/commit/7e22754cb3e6794c83bd67547f985e76057e01ea))

- **core**: Add regression tests for callback group helper and _active_lock
  ([`a8adbf7`](https://github.com/apajon/lifecore_ros2/commit/a8adbf7c63b1c4aa48856849c3101d3e85d439ac))

- **core**: Add regression tests for structured lifecycle log fields
  ([`83ffc50`](https://github.com/apajon/lifecore_ros2/commit/83ffc50378828a03c162678a027ec95d39ab7b56))


## v0.8.1 (2026-05-07)

### Bug Fixes

- **testing**: Remove redundant isinstance check in assert_activation_gated
  ([`008ab11`](https://github.com/apajon/lifecore_ros2/commit/008ab11b696c0595e3d9c07450ccee3ec880f577))

### Chores

- **prompts**: Add logical-commits prompt for conventional commits workflow
  ([`746c97a`](https://github.com/apajon/lifecore_ros2/commit/746c97af51ea2e2fa66c242e0e6e0458367ad991))

### Documentation

- **architecture**: Clarify _needs_cleanup reset and borrowed callback_group ownership
  ([`72f5bfb`](https://github.com/apajon/lifecore_ros2/commit/72f5bfb2732b2a2f93b654692cc2872c4694b3e8))

- **backlog**: Move Sprint 7 cleanup/ownership to shipped
  ([`1428a67`](https://github.com/apajon/lifecore_ros2/commit/1428a672b80ee61f874335cd07ed79619ba73f93))

- **components**: Align docstrings with cleanup/shutdown/error semantics
  ([`a2cb2a4`](https://github.com/apajon/lifecore_ros2/commit/a2cb2a465a6efe1c4e39ceff1d1cf193064fb8e6))

- **planning**: Replace "framework" with "library" in planning notes and meta files
  ([`d0debe6`](https://github.com/apajon/lifecore_ros2/commit/d0debe6d43774591a4bc4277326f3939c3e49a53))

- **readme**: Add hook sentence, 30-second view, and non-goals
  ([`d8eb9b8`](https://github.com/apajon/lifecore_ros2/commit/d8eb9b873fb0088da4332f1d331b242dd1249a0f))

- **sphinx**: Replace "framework" with "library" across public Sphinx docs
  ([`8960b6b`](https://github.com/apajon/lifecore_ros2/commit/8960b6b6e0eb0fe1640c46c9ffcab92b86df2322))

- **sprint**: Mark Sprint 7 cleanup/ownership API complete
  ([`c983368`](https://github.com/apajon/lifecore_ros2/commit/c9833683b5b45acfc601b3d8c068c6dd91835531))

- **sprint**: Mark Sprint 7 cleanup/ownership API shipped (2026-05-06)
  ([`6598c46`](https://github.com/apajon/lifecore_ros2/commit/6598c4634676c2181839737476a3cd9e8645ddbc))

### Testing

- **components**: Add cleanup ownership semantics regression tests
  ([`81bdd80`](https://github.com/apajon/lifecore_ros2/commit/81bdd806b8f80aac76e7bda5fb8cc40048d7ca30))

- **core**: Add _needs_cleanup reset policy regression tests
  ([`352ffa2`](https://github.com/apajon/lifecore_ros2/commit/352ffa257320208659f92dd7fd7c8265c38b599a))


## v0.8.0 (2026-05-06)

### Chores

- Add numpy to dev dependencies
  ([`53a15a3`](https://github.com/apajon/lifecore_ros2/commit/53a15a316460b3c79f411838db66ed39753014ee))

- **sprint**: Mark Sprint 6 activation-gating as complete
  ([`3030f63`](https://github.com/apajon/lifecore_ros2/commit/3030f637718f3a966b4bd9b9816995d62887536e))

### Continuous Integration

- Remove redundant numpy install step
  ([`7584301`](https://github.com/apajon/lifecore_ros2/commit/75843019cf2fbcb7143c2cb6890fb1c78b300c68))

### Documentation

- Add activation_gating to API reference and Sprint 6 changelog
  ([`c8bcb5c`](https://github.com/apajon/lifecore_ros2/commit/c8bcb5c30184589ba8607f43d94fd14b7f6ef042))

- Capture library-first ergonomic benefit — no override required for standard ROS resources
  ([`eb8ba60`](https://github.com/apajon/lifecore_ros2/commit/eb8ba6040ca9f3c65a56363f2c99d67e05dbea13))

- Extend Rule C to document shared activation-gating primitive
  ([`274eceb`](https://github.com/apajon/lifecore_ros2/commit/274eceb29dafbbf39813a61c89220b191a2b123d))

- Prefer library activation-gating primitives in user guides
  ([`f06fcf9`](https://github.com/apajon/lifecore_ros2/commit/f06fcf9c3937b91ca8b26c5c07f76f9c139d2fb8))

- Update examples.rst, patterns.rst, and api_friction_audit.rst for library-first
  ([`ed97ba9`](https://github.com/apajon/lifecore_ros2/commit/ed97ba98192b13dd24dd3239ab2e5f369c1862f1))

- **composition**: Align documentation with registration-site metadata feature
  ([`ebaaedb`](https://github.com/apajon/lifecore_ros2/commit/ebaaedb504640599f929205281290dd6c22bddf8))

- **example**: Refactor composed_ordered_pipeline to use registration-site dependencies
  ([`4b7faea`](https://github.com/apajon/lifecore_ros2/commit/4b7faea14b755a0fff54132cae3843dbd633e276))

- **planning**: Close Sprint 5 and add Sprint 5.1 to backlog
  ([`8f5c937`](https://github.com/apajon/lifecore_ros2/commit/8f5c93724c5857d63c9d1db1d4a31255d4fe7dc6))

- **planning**: Sprint 5 deliverable note and Sprint 5.1 spec
  ([`55cc40b`](https://github.com/apajon/lifecore_ros2/commit/55cc40bee4d1b4f93dc5814a2f49b20d5bdf9867))

### Features

- **components**: Propagate dependencies and priority through component hierarchy
  ([`a1e4feb`](https://github.com/apajon/lifecore_ros2/commit/a1e4febac6b4161c171fb43d99bb4ff3a47f5081))

- **composition**: Add registration-site metadata for add_component
  ([`84a392b`](https://github.com/apajon/lifecore_ros2/commit/84a392bfc97fae073e04df2ae32cd404d60dfa92))

- **core**: Add shared activation-gating primitive
  ([`d5314b0`](https://github.com/apajon/lifecore_ros2/commit/d5314b0494529b1487cba83ffcce270f6e928df4))

- **core**: Sprint 5 — dependency-resolved transition ordering
  ([`59d7dd5`](https://github.com/apajon/lifecore_ros2/commit/59d7dd5aa8b0b8725780eaed48e136d9546a2a44))

### Refactoring

- **components**: Service server uses shared activation-gating
  ([`26e580b`](https://github.com/apajon/lifecore_ros2/commit/26e580b351334bb3b386e5827639e4f6c51061e2))

- **core**: Unify activation-gating to shared primitive
  ([`269432f`](https://github.com/apajon/lifecore_ros2/commit/269432faed2ff0843b5c4fb6d961fffb594a3491))

### Testing

- Sprint 5 cascade ordering, regression updates, component pass-through
  ([`88813d2`](https://github.com/apajon/lifecore_ros2/commit/88813d29a791e87de47661f813fa73e4bdab3069))

- **composition**: Add regression tests for registration-site metadata
  ([`4fa17a1`](https://github.com/apajon/lifecore_ros2/commit/4fa17a182b4887de10794d1716429491bf88a795))

- **core**: Add activation-gating primitive and facade tests
  ([`9e0c50b`](https://github.com/apajon/lifecore_ros2/commit/9e0c50b6f62af8e23d2ff45c3760b735b458c876))


## v0.7.0 (2026-05-04)

### Bug Fixes

- **examples**: Add _on_configure to reset note in minimal_state_component docstring
  ([`b7c1aff`](https://github.com/apajon/lifecore_ros2/commit/b7c1affbf3b9cbcfb43fb5ea97d4ec4ed968e4a5))

### Chores

- Add twine dev dependency
  ([`f0af8e5`](https://github.com/apajon/lifecore_ros2/commit/f0af8e58dd55e0434f208f85be9bd68d34447eb4))

### Code Style

- Format PyPI publish workflow
  ([`b9ca5b7`](https://github.com/apajon/lifecore_ros2/commit/b9ca5b794594d09227569319a540ab2dadf77478))

### Continuous Integration

- Add TestPyPI publish workflow
  ([`b859f3b`](https://github.com/apajon/lifecore_ros2/commit/b859f3b1bd1e999c4eabae581bc77bc192670d5e))

- Default PyPI publish to latest release
  ([`560cdce`](https://github.com/apajon/lifecore_ros2/commit/560cdce4e98e6e98e4845122954725b965952502))

- Make TestPyPI preview versions unique
  ([`f5c1046`](https://github.com/apajon/lifecore_ros2/commit/f5c10464bfda2e753197a98b47e969589ff1359d))

- Publish PyPI releases manually after TestPyPI
  ([`55a5ecb`](https://github.com/apajon/lifecore_ros2/commit/55a5ecb307f88bc44b4553842259d2674ec08a19))

- Publish to PyPI from tag-release workflow
  ([`8ed4809`](https://github.com/apajon/lifecore_ros2/commit/8ed4809e4f7c08f63f48d8fee33813ccd8759510))

- Resolve latest release without checkout
  ([`528a088`](https://github.com/apajon/lifecore_ros2/commit/528a088d8bf369b7713d4e029d14a346d96f0808))

- Strip local version for TestPyPI builds
  ([`a049a1c`](https://github.com/apajon/lifecore_ros2/commit/a049a1cf166e9236770fea466e82000601a87795))

- Trigger TestPyPI publish on workflow_dispatch only
  ([`a00390d`](https://github.com/apajon/lifecore_ros2/commit/a00390dcf1166ce114d1800dbb84773792cddeac))

- Use real setuptools-scm version for TestPyPI (strip local segment)
  ([`7520cd3`](https://github.com/apajon/lifecore_ros2/commit/7520cd385d3410cfba26fc29983e232b8eb6301a))

### Documentation

- Add Sprint 4.5 for core state-only LifecycleComponent example
  ([`4fe4825`](https://github.com/apajon/lifecore_ros2/commit/4fe4825ce0fa025bc9643beb8957d06cb9e3c304))

- Add strategic planning roadmap
  ([`6a80d89`](https://github.com/apajon/lifecore_ros2/commit/6a80d892e9ed1b6c69c31102ffd1fa69264ce54f))

- Clarify core vs companion repo example strategy
  ([`3cffb56`](https://github.com/apajon/lifecore_ros2/commit/3cffb561ac2a7988937490a4bf80c5e076a6ec80))

- Document PyPI install path
  ([`f21926d`](https://github.com/apajon/lifecore_ros2/commit/f21926d9260582323db9cbf92c2f21712b392931))

- Expand Sprint 4 with detailed execution plan and acceptance criteria
  ([`2abfa2b`](https://github.com/apajon/lifecore_ros2/commit/2abfa2b2c16feac2cdc3d2d4169c995e9facec10))

- Normalize runtime introspection terminology
  ([`deeaf00`](https://github.com/apajon/lifecore_ros2/commit/deeaf0069c1feeba6ad7097475b93db338500fa4))

- Register minimal_state_component in examples index; close sprint 4.5
  ([`713afba`](https://github.com/apajon/lifecore_ros2/commit/713afba998d575ee721310524e4556cc0a4de7cf))

- Reprioritize sprint planning cards
  ([`af6e720`](https://github.com/apajon/lifecore_ros2/commit/af6e72097c0ef8d9e0e7ff32536254b452062364))

- **sprint-4.5**: Fix decisions and mark success signal as delivered
  ([`20b1145`](https://github.com/apajon/lifecore_ros2/commit/20b114579ba9d5f4bda3c139f4c511fa1cf82d0b))

### Features

- **examples**: Add minimal_state_component example
  ([`c2e788c`](https://github.com/apajon/lifecore_ros2/commit/c2e788c3abf7225532c2a534c51135d174f361ac))

### Testing

- **smoke**: Add parametrized import-safety test for core examples
  ([`04122c3`](https://github.com/apajon/lifecore_ros2/commit/04122c3b3698a1d9a29e5ffd18a302384f497f02))


## v0.6.1 (2026-05-02)

### Bug Fixes

- **ci**: Update docs trigger on PR
  ([`1a30bc0`](https://github.com/apajon/lifecore_ros2/commit/1a30bc0d9e8e46a757ca280502c5119c82e06902))

### Documentation

- Add latest release badge
  ([`1a663e1`](https://github.com/apajon/lifecore_ros2/commit/1a663e1b6702db0ef286d3eea1dce04b1b5ae323))

- Align alpha maturity status
  ([`6d7f39d`](https://github.com/apajon/lifecore_ros2/commit/6d7f39d542f9064af54f25d290d3fac37fa3a03d))

- Fix PyPI README image rendering
  ([`fc7185f`](https://github.com/apajon/lifecore_ros2/commit/fc7185fe25916b193230eca783efea900784b679))

- Highlight ROS installation requirement
  ([`4627728`](https://github.com/apajon/lifecore_ros2/commit/4627728cdbab9725c50e293195f05a0fa39a6a03))

- Update companion examples planning
  ([`15bda8d`](https://github.com/apajon/lifecore_ros2/commit/15bda8df372d911817247fd947d0b82bb31beff8))

- Use uv install command in README
  ([`df66542`](https://github.com/apajon/lifecore_ros2/commit/df665420be779dde87d3e86acc902f925ae9e10c))


## v0.6.0 (2026-05-01)

### Chores

- Remove old root-level test files
  ([`86b244d`](https://github.com/apajon/lifecore_ros2/commit/86b244da71ba3abc3bbec93bce422f5ae0b6ed68))

### Documentation

- Add 9 sprints for post-1.0 development
  ([`5d67a12`](https://github.com/apajon/lifecore_ros2/commit/5d67a1243949a6bb3cc0f07b7876c17e0a9cc3e2))

- Add HD PNG logo assets for Sphinx branding
  ([`a31e4e0`](https://github.com/apajon/lifecore_ros2/commit/a31e4e0c8a385c5ace343495e8e4d8aa857d742d))

- Add lifecycle branding CSS system
  ([`9452121`](https://github.com/apajon/lifecore_ros2/commit/945212139bbe308d3da943d2f896c82ed338e509))

- Add lifecycle branding to documentation pages
  ([`a45fb3a`](https://github.com/apajon/lifecore_ros2/commit/a45fb3a42314b87afab1fdce0495fc2ed95d0dd7))

- Add light/dark logo switching to README
  ([`c4f9253`](https://github.com/apajon/lifecore_ros2/commit/c4f925363bba9958fe6e6ce1448284dd2a6c5f7d))

- Add Real examples v1 sprint (S4), renumber S5-S10
  ([`576f350`](https://github.com/apajon/lifecore_ros2/commit/576f350a2ae00f05d712d336872513a16f792719))

- Add service component API references
  ([`a74cb4f`](https://github.com/apajon/lifecore_ros2/commit/a74cb4fe0e731c2a6b343ba0cfd6257145c19832))

- Add service component examples
  ([`79adadb`](https://github.com/apajon/lifecore_ros2/commit/79adadbcabb028856c14173f8c81dc1212a30ddf))

- Add SVG placeholder assets for icon and logos
  ([`ad34fd2`](https://github.com/apajon/lifecore_ros2/commit/ad34fd219b4129ada1a733a4227645bde70d1a30))

- Configure Furo theme with lifecycle branding
  ([`b8962f3`](https://github.com/apajon/lifecore_ros2/commit/b8962f3fce2a7fda9ed42170dbf2c340f93dace7))

- Create planning/ section and lifecycle design notes
  ([`8e039f2`](https://github.com/apajon/lifecore_ros2/commit/8e039f2c91bba64f51d3af6901f631e50ccc9f4d))

- Document service component gating and naming
  ([`4f11249`](https://github.com/apajon/lifecore_ros2/commit/4f11249e34fa850cb5d2f1183aa8e65c5696d2df))

- Document testing utilities and split API reference
  ([`4ea7c9f`](https://github.com/apajon/lifecore_ros2/commit/4ea7c9f188ce65aef0a24e93f7f5ee1a56921d13))

- Generalize interface-type inference pattern to services
  ([`92719c7`](https://github.com/apajon/lifecore_ros2/commit/92719c758d045b5afd5776695b5a578541efd66e))

- Mark LifecycleTimerComponent as shipped in TODO backlog
  ([`d5d468b`](https://github.com/apajon/lifecore_ros2/commit/d5d468b9ca113d868b8ff38d1ac061a0ec0b0242))

- Move ServiceComponent from backlog to shipped
  ([`f2f42ec`](https://github.com/apajon/lifecore_ros2/commit/f2f42ecb414f359779a6d85ce519864e5d76f5b2))

- Refactor ROADMAP.md to strategic overview
  ([`efe4890`](https://github.com/apajon/lifecore_ros2/commit/efe4890502dd0d247989894889556c36d7f5f1c4))

- Remove consolidated files from root
  ([`df5cbd6`](https://github.com/apajon/lifecore_ros2/commit/df5cbd6cb1d218f9a75f3fb5e7757e3173f4eb10))

- Switch banner icon to light/dark theme variants
  ([`5437aab`](https://github.com/apajon/lifecore_ros2/commit/5437aab81dd03b51634a26685805f1bd330d6d53))

- Uncheck sprint checklists, renumber S5-S10 after S4 insertion
  ([`0e7a569`](https://github.com/apajon/lifecore_ros2/commit/0e7a569495fedea9af64c349644a6af259bfbea2))

- Update api_friction_audit to reflect ServiceComponent shipped
  ([`6a799f1`](https://github.com/apajon/lifecore_ros2/commit/6a799f1894b4c146c8c5a681125af0af282d3980))

- Update links to point to new planning/ location
  ([`4a3bdaf`](https://github.com/apajon/lifecore_ros2/commit/4a3bdaf4e893c34033ee3ba9b48423718229389b))

- Update mental model and FAQ for services
  ([`d6585e5`](https://github.com/apajon/lifecore_ros2/commit/d6585e5ff367f5dafe43e95275bd48111532b9bc))

- Update README with tagline and lifecycle reading path
  ([`9501e96`](https://github.com/apajon/lifecore_ros2/commit/9501e961e66868613bea5e969702982859cccd36))

- Wire planning section into Sphinx index
  ([`cd29401`](https://github.com/apajon/lifecore_ros2/commit/cd29401b23138349d3299b071d3d03f99b0357d9))

### Features

- **sprint-1**: Add service component primitives
  ([`bc2d631`](https://github.com/apajon/lifecore_ros2/commit/bc2d6317492635e0c1bd0f25c2eabf586e6b7bd8))

### Refactoring

- Reorganize tests/ into sub-folders (smoke, core, components, integration)
  ([`3a697f5`](https://github.com/apajon/lifecore_ros2/commit/3a697f5c577f53a5e3192c0e1e09e10f95b1c327))

### Testing

- Add lifecycle testing utilities
  ([`62f0b4f`](https://github.com/apajon/lifecore_ros2/commit/62f0b4f80dbb73b83cfb09b3a6c7e444866e6756))

- Reuse lifecycle testing fakes
  ([`cb52c89`](https://github.com/apajon/lifecore_ros2/commit/cb52c899e4a93aefd59f64eff8903111c07263e1))


## v0.5.2 (2026-04-28)

### Bug Fixes

- **ci**: Merge tag-release and publish into single workflow to bypass GITHUB_TOKEN trigger
  restriction
  ([`d3aa25e`](https://github.com/apajon/lifecore_ros2/commit/d3aa25e59d88ed96836b889128ff3d37a041a6c0))


## v0.5.1 (2026-04-28)

### Bug Fixes

- **ci**: Disable PSR GHA integration to fix commit_sha output error
  ([`c1dbddc`](https://github.com/apajon/lifecore_ros2/commit/c1dbddc5d2e20e22c32cad99fa9c6c67772deaea))

- **ci**: Unset GITHUB_ACTIONS before PSR to prevent commit_sha output error
  ([`4e13270`](https://github.com/apajon/lifecore_ros2/commit/4e1327094ba50c3d3771bb4ef10f98ce51cbe41c))

- **ci**: Use env -u GITHUB_ACTIONS to scope PSR GHA isolation to subprocess
  ([`f042686`](https://github.com/apajon/lifecore_ros2/commit/f042686e702737bef072660bfbf8e0fce123be0c))

- **ci**: Use heredoc for PR body and force-with-lease for branch push
  ([`be1600f`](https://github.com/apajon/lifecore_ros2/commit/be1600f7cf811050de6e6d5fbb66ff5dd9d0e52f))

- **ci**: Use semantic-release version --no-push --no-tag for proper versioned changelog header
  ([`2732e14`](https://github.com/apajon/lifecore_ros2/commit/2732e14dcb210d3a66df1d536a0333f2cf182f4b))

- **deps**: Pin python-semantic-release <10.3.0 to avoid commit_sha output bug
  ([`bd3118a`](https://github.com/apajon/lifecore_ros2/commit/bd3118acb1cf8c7a61a8dfbb7b5cab3236467211))

### Documentation

- **changelog**: Clean up permanent v0.4.0 header and orphan Unreleased section
  ([`76ba234`](https://github.com/apajon/lifecore_ros2/commit/76ba234933a39ef81593b14e603694891544f8f3))


## v0.5.0 (2026-04-28)

### Bug Fixes

- **agents**: Add non-deferred tools to MemPalace-only agents
  ([`a6ec916`](https://github.com/apajon/lifecore_ros2/commit/a6ec916566a633cf135f76b3aefa84c250657901))

- **ci**: Avoid semantic-release version in release mode to fix commit_sha error
  ([`3b5becb`](https://github.com/apajon/lifecore_ros2/commit/3b5becbe59458392118c18e6a1c8b62e501c01fe))

- **ci**: Force-push release bump branch to handle re-runs
  ([`c4867ee`](https://github.com/apajon/lifecore_ros2/commit/c4867eec4abcab8a9c121922c1a1199956d94aaf))

- **ci**: Replace PSR Docker action with uv run to fix uv not found
  ([`66ba96f`](https://github.com/apajon/lifecore_ros2/commit/66ba96faa300579c52932a9389d56fa4a7e8eda1))

- **ci**: Replace semantic-release publish with gh release create in publish workflow
  ([`e19ca43`](https://github.com/apajon/lifecore_ros2/commit/e19ca438c645f9650c7b7d09b1d608e91d5d636e))

- **ci**: Sync release dependency group to make semantic-release available
  ([`c2cb82e`](https://github.com/apajon/lifecore_ros2/commit/c2cb82e3688d88ff68ed1fc45f8cebf45bf7a386))

### Chores

- Add callback_group management to post-release backlog
  ([`a94df68`](https://github.com/apajon/lifecore_ros2/commit/a94df6896446ce7ae3d6e4a87a684dff03e3ec37))

- Add naming convention review checklist item to CONTRIBUTING.md
  ([`5867213`](https://github.com/apajon/lifecore_ros2/commit/586721341985a77555a5a505648e821f1e005605))

- Mark §2 adoption hardening items complete
  ([`9865d78`](https://github.com/apajon/lifecore_ros2/commit/9865d78d0aa967da36bc1bccd5b46ad77823b1a5))

- **agents**: Pin model per role for non-orchestrator subagents
  ([`1c7a47d`](https://github.com/apajon/lifecore_ros2/commit/1c7a47d0bdf22b33aa72fdbf380f8a889aa59009))

- **github**: Normalize template and workflow formatting
  ([`0d1e8af`](https://github.com/apajon/lifecore_ros2/commit/0d1e8afacb0bdb655ff11308458fad0e9e4a7acc))

- **orchestrators**: Switch tool alias from gitkraken/* to github/*
  ([`63f2fe8`](https://github.com/apajon/lifecore_ros2/commit/63f2fe8864dd07d683fc59016795cf71e78ed564))

- **publication**: Clean public-facing metadata
  ([`f621db4`](https://github.com/apajon/lifecore_ros2/commit/f621db469b16b3b48d18ab564983061e25198d9a))

### Code Style

- Format _iface_type.py with ruff
  ([`f0131d3`](https://github.com/apajon/lifecore_ros2/commit/f0131d3b0b908e3cc2344a105920f4d8b031a0bb))

### Continuous Integration

- Add GitHub Pages deploy job to docs workflow
  ([`a07c343`](https://github.com/apajon/lifecore_ros2/commit/a07c3434bd815035c000edda8c6e626804e6431c))

- Replace direct push with bump PR flow and add publish workflow
  ([`683be5c`](https://github.com/apajon/lifecore_ros2/commit/683be5c04750cf45726b1d09183e6688a6cdd285))

- Skip docs deploy on pull requests
  ([`11daf7c`](https://github.com/apajon/lifecore_ros2/commit/11daf7caa90ff4ed6a010d9d2fbedaacbaed6177))

- Update docs workflow actions for Node 24
  ([`1856ab4`](https://github.com/apajon/lifecore_ros2/commit/1856ab48bdc4d3f8f07d603897cd80ff8a8a74bc))

- **docs**: Opt into Node.js 24 for JavaScript actions
  ([`b01e6c4`](https://github.com/apajon/lifecore_ros2/commit/b01e6c4103858ee8ce070e66a30764ddfe53e2ab))

### Documentation

- Add adoption hardening roadmap and actionable TODO checklist
  ([`b70402a`](https://github.com/apajon/lifecore_ros2/commit/b70402a71f26378fee059e0b7ca57a43da22dd70))

- Add API friction audit note (§2 adoption hardening)
  ([`5bc366b`](https://github.com/apajon/lifecore_ros2/commit/5bc366bac2130b4f9f354de2de616df61dc46447))

- Add concurrency contract ADR and tick §4 todos
  ([`77895d7`](https://github.com/apajon/lifecore_ros2/commit/77895d7942890a2138b5a947ae6a0ded141a73bb))

- Add GitHub Pages documentation badge to README
  ([`c431ba4`](https://github.com/apajon/lifecore_ros2/commit/c431ba474a51cf577c5c6095752f94edd4b70eea))

- Add lightweight Furo branding
  ([`a7abe20`](https://github.com/apajon/lifecore_ros2/commit/a7abe2018c8800fbc0fdeb9fae89ca790fc9c2e2))

- Add mental model page
  ([`82f26a7`](https://github.com/apajon/lifecore_ros2/commit/82f26a7f39f20cd430644a1a4440269cdbdc09d2))

- Add quickstart guide
  ([`b117829`](https://github.com/apajon/lifecore_ros2/commit/b117829ae4bcad205ac4d86507b9bbea08321974))

- Align iface-type inference guidance with shipped behavior
  ([`df9d16c`](https://github.com/apajon/lifecore_ros2/commit/df9d16cba05afb0a0b4afb69cde284bf79b18468))

- Align README quickstart
  ([`9e947ef`](https://github.com/apajon/lifecore_ros2/commit/9e947ef9452c78321ace2b7425341001247fe986))

- Clean up Sphinx warnings (orphan paragraph + audit orphan)
  ([`8f6fa4d`](https://github.com/apajon/lifecore_ros2/commit/8f6fa4dbdf52c88c9ecd03564fa1ef5f290e7949))

- Document interface-type inference pattern (generic-only form)
  ([`9b99867`](https://github.com/apajon/lifecore_ros2/commit/9b998678f67e0834eabfdea0de24ae5677e9575e))

- Improve examples discovery guide
  ([`18a34d3`](https://github.com/apajon/lifecore_ros2/commit/18a34d310c5c47038f98e04031d0629b9432fa41))

- Link mental model from onboarding pages
  ([`86e07ef`](https://github.com/apajon/lifecore_ros2/commit/86e07ef2e011a618c1e5959d808cf1f1e162b780))

- Load custom Sphinx stylesheet
  ([`b7fbf58`](https://github.com/apajon/lifecore_ros2/commit/b7fbf582f4d54aaab970c37a3ac1eb67dc1385a2))

- Make design notes public-facing
  ([`6f53651`](https://github.com/apajon/lifecore_ros2/commit/6f53651649bb13f0ef33312480c4a825b4dcd7ce))

- Point documentation URLs to GitHub Pages
  ([`5e6ca7f`](https://github.com/apajon/lifecore_ros2/commit/5e6ca7fcf113e0bcddb0e56dff2088521498a706))

- Promote naming conventions to architecture docs
  ([`b9feb88`](https://github.com/apajon/lifecore_ros2/commit/b9feb8823167e0f3e8619878a94bb80585421062))

- Record PR #4 in changelog and TODO tracking
  ([`728bf71`](https://github.com/apajon/lifecore_ros2/commit/728bf71f921706d7a3488c9336f9294ab41eb7b7))

- Remove internal-only wording from Copilot assets
  ([`2d1726e`](https://github.com/apajon/lifecore_ros2/commit/2d1726edb7e3cbf46ee74755efcf58a857c2f6b0))

- Restore LifecycleTimerComponent documentation
  ([`2a15993`](https://github.com/apajon/lifecore_ros2/commit/2a15993c30065e13862f254f0e13290e5035e1fe))

- Rewrite documentation homepage
  ([`5ba48c3`](https://github.com/apajon/lifecore_ros2/commit/5ba48c3de479e4bc7a1cdf7c017c9894be600026))

- Separate guides from API reference in Sphinx nav
  ([`17fd8dc`](https://github.com/apajon/lifecore_ros2/commit/17fd8dc7d73acebbe8413dfc17149ee3511593e7))

- Streamline README onboarding path
  ([`36f9d40`](https://github.com/apajon/lifecore_ros2/commit/36f9d4031c7a366912a78bfa76e292397f9196b2))

- Switch Sphinx docs to Furo theme
  ([`cd69072`](https://github.com/apajon/lifecore_ros2/commit/cd69072bff18470e5f9f7b7cd7736a4dd346c1f5))

- Tick §6 test coverage checklist and add regression discipline rule
  ([`8f9db21`](https://github.com/apajon/lifecore_ros2/commit/8f9db2121463077ac58b249905307d9afceced8e))

- Update adoption hardening checklist
  ([`aa5546e`](https://github.com/apajon/lifecore_ros2/commit/aa5546ecb6648bda8b39cde424934de72b4dc821))

- **adr**: Record R-IfaceTypeInference verdict (issue #1)
  ([`e9de44f`](https://github.com/apajon/lifecore_ros2/commit/e9de44f7f904e5a4b81b9264296e0fd798c65b3a))

- **architecture**: Document strict lifecycle contract
  ([`ab8f8f4`](https://github.com/apajon/lifecore_ros2/commit/ab8f8f4d4de0ddcdb623e9705f0619cd9faea4bd))

- **community**: Add minimal governance files
  ([`eddfa30`](https://github.com/apajon/lifecore_ros2/commit/eddfa30addd021cd645739775fdd33da19fc8cfb))

- **community**: Clarify human contact paths
  ([`5a7b800`](https://github.com/apajon/lifecore_ros2/commit/5a7b80057f34e925bdce80ded1fb501220391cdb))

- **community**: Simplify governance wording
  ([`be535bd`](https://github.com/apajon/lifecore_ros2/commit/be535bd73efd375aff18f9739619c798e7fe7231))

- **components**: Document callback_group borrow-only contract in Args docstrings
  ([`c38d290`](https://github.com/apajon/lifecore_ros2/commit/c38d290d2019b114b88b524bddd447198ec06a5d))

- **copilot**: Add behavioral guidelines
  ([`43b13e0`](https://github.com/apajon/lifecore_ros2/commit/43b13e08351e8e326ddb0db0f09dc8dd6cd42f0a))

- **design-notes**: Add dynamic components design note (§7)
  ([`eb50dca`](https://github.com/apajon/lifecore_ros2/commit/eb50dca46a5793a3d59280eada4c10e1a5f9f8db))

- **design-notes**: Add observability design note (§7)
  ([`0e6fc9c`](https://github.com/apajon/lifecore_ros2/commit/0e6fc9cba1af5e7a0e8ead10bbecb4a3b4658772))

- **design-notes**: Add runtime introspection design note (§7)
  ([`be4229a`](https://github.com/apajon/lifecore_ros2/commit/be4229a26aa27f041e2c7769ed2a9f2be2500a5a))

- **examples**: Add minimal_timer and refactor telemetry to compose timer + publisher
  ([`1b77fe4`](https://github.com/apajon/lifecore_ros2/commit/1b77fe42af331ef19db516672795d3e9f1d4a91d))

- **examples**: Add minimal_timer example and guidance
  ([`675fb26`](https://github.com/apajon/lifecore_ros2/commit/675fb26b3066d4ab197436eeba399f2dea87b80b))

- **patterns**: Add borrow-only contract pattern and anti-pattern
  ([`5d4b8ea`](https://github.com/apajon/lifecore_ros2/commit/5d4b8ead7ad8f8fed0336bb38a8d4b1e71abcb58))

- **readme**: Add positioning section, audience framing, and architecture diagram
  ([`2d89741`](https://github.com/apajon/lifecore_ros2/commit/2d897418e6beb3cc581b8a049221b8b945506653))

- **readme**: Add shortest-path subscriber example section (§2 adoption hardening)
  ([`f35afa1`](https://github.com/apajon/lifecore_ros2/commit/f35afa11c0798b3e22cadf8c14236fca40376e74))

- **release**: Record v0.4.0 public release state
  ([`8d3557b`](https://github.com/apajon/lifecore_ros2/commit/8d3557bed9321e78be550fb2dff8abfacbfb728c))

### Features

- Add callback_group support to lifecycle components
  ([`06741c6`](https://github.com/apajon/lifecore_ros2/commit/06741c69f659736ccb752a0c30a0051ee05429f1))

- **agents**: Split Sphinx documentation into technical and narrative agents
  ([`2a9e0c7`](https://github.com/apajon/lifecore_ros2/commit/2a9e0c7cfd0098a7b94014e2d0d1b845bab855e2))

- **components**: Add LifecycleTimerComponent with activation gating
  ([`ec4397d`](https://github.com/apajon/lifecore_ros2/commit/ec4397d9ee602a3219649c7b16c53d0b5166ecfb))

- **components**: Make LifecyclePublisherComponent msg_type optional
  ([`d89814d`](https://github.com/apajon/lifecore_ros2/commit/d89814d6eae9ea63db07e672d4341479d557eb72))

- **components**: Make LifecycleSubscriberComponent msg_type optional
  ([`eaa1fb5`](https://github.com/apajon/lifecore_ros2/commit/eaa1fb5a3ab55fd6d2f32c06958fdabdf4d60fb4))

- **components**: Make msg_type optional via interface inference
  ([`aacdd68`](https://github.com/apajon/lifecore_ros2/commit/aacdd68c3e4d985ed867e4fb98e5677a2605fbf4))

- **core**: Add _InterfaceTypeNotResolvedError (part 1/3 — addendum)
  ([`fa721b1`](https://github.com/apajon/lifecore_ros2/commit/fa721b1fa3ab4ae0be67a635b5469b9f19c4ca4f))

- **core**: Add ConcurrentTransitionError and transition guard
  ([`7f3136c`](https://github.com/apajon/lifecore_ros2/commit/7f3136c1f026e07935643d7f2de5afc10a151749))

- **core**: Add InvalidLifecycleTransitionError for strict lifecycle contract
  ([`2773b5d`](https://github.com/apajon/lifecore_ros2/commit/2773b5d300576b89330594b568f924f7ae4151e0))

- **core**: Add InvalidLifecycleTransitionError to exception hierarchy
  ([`62eea4a`](https://github.com/apajon/lifecore_ros2/commit/62eea4aaf46819d7b665d7b61407804d7fda6817))

- **core**: Add remove_component with _withdrawn silencing guard
  ([`54ce78c`](https://github.com/apajon/lifecore_ros2/commit/54ce78cf307e0fea8e58cade459b209d0ef3375a))

- **core**: Create _iface_type.py resolver module
  ([`d981207`](https://github.com/apajon/lifecore_ros2/commit/d98120750d9503c9e05493db02cdbc44314ae513))

- **core**: Enforce strict lifecycle contract
  ([`696fdeb`](https://github.com/apajon/lifecore_ros2/commit/696fdeb98669c13d787c5082e9a5766cc793b663))

- **orchestrators**: Integrate MemPalace Knowledge Writer in docs sync
  ([`70b8614`](https://github.com/apajon/lifecore_ros2/commit/70b8614c1fe407b3a1211fd32f02f82b2277188d))

### Refactoring

- **orchestrators**: Adopt cost-aware adaptive delegation
  ([`5623155`](https://github.com/apajon/lifecore_ros2/commit/56231558b87797d7ff7c77f2bc921e056564d937))

### Testing

- Add callback_group propagation and persistence tests
  ([`c16e4d3`](https://github.com/apajon/lifecore_ros2/commit/c16e4d36f7f0e40e93145df9ad53656ad73b21e1))

- Add interface-type inference test coverage
  ([`f215b5e`](https://github.com/apajon/lifecore_ros2/commit/f215b5e26f57959253f28629c8bcebd54a5f6838))

- **components**: Cover LifecycleTimerComponent transitions and controls
  ([`8402733`](https://github.com/apajon/lifecore_ros2/commit/84027331586dff666469f712652d6d7a42678ef9))

- **integration**: Cover shutdown from active and heterogeneous component sets
  ([`ba62dc9`](https://github.com/apajon/lifecore_ros2/commit/ba62dc9d4c73744e57b91f015a18f6c647f63b87))

- **regression**: Concurrent transition guard and flag lifecycle
  ([`0b529b9`](https://github.com/apajon/lifecore_ros2/commit/0b529b9f697e95a82d3e6732bc16d146f3526939))

- **regression**: Cover reentrant transitions and teardown resource release
  ([`6b2d058`](https://github.com/apajon/lifecore_ros2/commit/6b2d0588135aaf4e2ba17d2ab7eaefb3667ff5f4))

- **iface-type-inference**: Mark issue [#1](https://github.com/apajon/lifecore_ros2/issues/1)
  as shipped in the API friction audit, document the generic-only topic-component
  form in `docs/patterns.rst`, and close adoption hardening §2
  for PR [#4](https://github.com/apajon/lifecore_ros2/pull/4).


## v0.4.0 (2026-04-22)

### Bug Fixes

- **docs**: Correct stale automodule paths in api.rst
  ([`a2d9e51`](https://github.com/apajon/lifecore_ros2/commit/a2d9e5199cbdcb9dcce3499da1e18375d0a5e244))

- **typing**: Resolve 82 pyright errors blocking CI
  ([`0d49a82`](https://github.com/apajon/lifecore_ros2/commit/0d49a827e4858ba7719952e80341ab90dea25168))

- **typing**: Suppress remaining 8 pyright errors on mock publisher attributes
  ([`4ebb1a3`](https://github.com/apajon/lifecore_ros2/commit/4ebb1a36ba37ed2dacdbe1bcbda29245ef6b2211))

### Chores

- Mark release workflow rehearsal as done in TODO
  ([`5d0f6dd`](https://github.com/apajon/lifecore_ros2/commit/5d0f6dd3e8edf11152b1b6c7b0e19ab676f0f4de))

- Mark TODO_2 sections 5.1 and 5.2 as done with decision records
  ([`4bb431d`](https://github.com/apajon/lifecore_ros2/commit/4bb431d772a1e91b6909359518ffd4734684fe14))

- Mark §7.3 visual asset complete in TODO_2.md
  ([`13e86c6`](https://github.com/apajon/lifecore_ros2/commit/13e86c6348f2b17ac2144b9671964d57cdd961e3))

- **copilot**: Add MemPalace and architecture guard agents
  ([`fe1c3cd`](https://github.com/apajon/lifecore_ros2/commit/fe1c3cde82a7699f784cad87418c2d54e49a183f))

- **github**: Add structured issue templates
  ([`96fb65c`](https://github.com/apajon/lifecore_ros2/commit/96fb65cf5f37a51b5ffb1d7a7a81b3fd94a0f74f))

- **gitignore**: Ignore local ros2 jazzy interface dumps
  ([`9884539`](https://github.com/apajon/lifecore_ros2/commit/9884539273db75909ad9a4abf29cfe6f6e2a7a7c))

- **packaging**: Drop unused deps, PEP 639 license, add classifiers and URLs
  ([`a6280fd`](https://github.com/apajon/lifecore_ros2/commit/a6280fd9b530ad370d7afd350cafca1781de4ad3))

- **release**: Record 3.3 decision in TODO_2.md
  ([`397c3e3`](https://github.com/apajon/lifecore_ros2/commit/397c3e327a9ca271dff6a6a3b2ca1d7eaba3354e))

- **todo**: Align release flow notes with v0.3.0 shipped and v0.4.0 upcoming
  ([`7a0b3fa`](https://github.com/apajon/lifecore_ros2/commit/7a0b3fa212f46f17d5e0479ba0a726b344501cee))

- **todo**: Fix semantic-release dry-run command in §6.7
