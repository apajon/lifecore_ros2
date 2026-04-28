# CHANGELOG

## First public release — v0.4.0

`lifecore_ros2` v0.4.0 is the first public release of the library. It establishes a small,
predictable surface for composing lifecycle-aware ROS 2 nodes without layering a hidden state
machine on top of native ROS 2 lifecycle semantics.

This section is the project's permanent first-release statement. Subsequent versioned entries
are appended below the `version list` marker by `python-semantic-release` and are not edited
by hand. The live scope boundary is tracked in [ROADMAP.md](ROADMAP.md); this section is a
snapshot at the time of the first public release.

### What this release provides

**Public API** (re-exported from `lifecore_ros2`):

- `LifecycleComponentNode` — lifecycle node that owns and drives registered components as
  native ROS 2 managed entities.
- `LifecycleComponent` — base class for lifecycle-aware components (abstract by convention);
  propagates transitions through `_on_configure`, `_on_activate`, `_on_deactivate`,
  `_on_cleanup`, `_on_shutdown`, `_on_error`.
- `TopicComponent` — base class for topic-oriented components; allocates ROS pub/sub
  during configure, releases during cleanup.
- `LifecyclePublisherComponent` — generic publisher (`[MsgT]`) gated by activation state.
- `LifecycleSubscriberComponent` — generic subscriber (`[MsgT]`) whose `on_message` callback
  is gated by activation state.
- `when_active` — decorator that guards component methods on activation state.
- `LifecoreError` and the typed boundary-violation subclasses `RegistrationClosedError`,
  `DuplicateComponentError`, `ComponentNotAttachedError`, `ComponentNotConfiguredError`.

**Examples**: `examples/minimal_node.py`, `examples/minimal_publisher.py`,
`examples/minimal_subscriber.py`, `examples/telemetry_publisher.py`.

**Documentation**: getting-started guide, architecture overview, recommended patterns and
anti-patterns, migration notes from raw `rclpy`, and a Sphinx-buildable API reference under
[docs/](docs/).

**Quality baseline**: Ruff formatting and linting, Pyright in strict mode for the core
package, and a pytest suite covering nominal transitions, edge transitions, activation
gating, failure propagation, and resource handling.

### What this release does not provide yet

- Companion examples repository (`lifecore_ros2_examples`).
- Visual demo asset (terminal recording or GIF).
- Extended FAQ section.
- Advanced patterns beyond the recommended/anti-pattern pairs already documented.

### Supported baseline

- Python 3.12 or newer.
- ROS 2 Jazzy.
- `rclpy` is required at runtime and is expected to come from the system ROS installation;
  it is intentionally not declared as a PyPI dependency.

### Known limitations

- `composed_pipeline.py` demonstrates multi-component composition inside a single node;
  multi-node or domain-specific examples live in the planned companion repository.
- The `MsgT` type parameter on topic components is unbounded by design — no stable ROS 2
  message base class is exported by `rosidl` to constrain it without coupling.
- No companion examples repository, visual asset, or FAQ ships with this release.
- Lifecycle observability beyond standard `rclpy` logging (e.g. `/diagnostics` integration)
  is out of scope for the core library.

<!-- version list -->

## Unreleased

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


## Unreleased

### Documentation

- **iface-type-inference**: Mark issue [#1](https://github.com/apajon/lifecore_ros2/issues/1)
  as shipped in the API friction audit, document the generic-only topic-component
  form in `docs/patterns.rst`, and close `TODO_adoption_hardening.md §2`
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
