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
  ([`58cf315`](https://github.com/apajon/lifecore_ros2/commit/58cf3159ea02f85a05519395bb3861631dd9ffc3))

- **todo**: Mark first green CI run as done
  ([`3ed89ca`](https://github.com/apajon/lifecore_ros2/commit/3ed89ca13317f53f3ed52756d7420d3c575d7775))

- **todo**: Mark section 4 documentation tasks as completed
  ([`0f0ec2c`](https://github.com/apajon/lifecore_ros2/commit/0f0ec2c19c7874cbf32ba0bff28666c0bd9fb633))

- **todo**: Mark section 6 complete in TODO_2.md
  ([`250b47a`](https://github.com/apajon/lifecore_ros2/commit/250b47a523295e7e376914d10aba80d79b0d76b1))

- **todo**: Mark TODO 5.4 sub-items complete
  ([`a3e2d64`](https://github.com/apajon/lifecore_ros2/commit/a3e2d648b4316b38777e8c6fdb2b1b68ad8b49da))

- **todo**: Mark TODO 7.1 complete
  ([`979a322`](https://github.com/apajon/lifecore_ros2/commit/979a3220647e98d4c612301932e8d96167fb5237))

- **todo**: Mark TODO_2.md §5.3 complete with decision record
  ([`aa6273d`](https://github.com/apajon/lifecore_ros2/commit/aa6273df45eaf10ac8ffdd312d45326a1d61881d))

- **todo**: Note pydantic to add when spec_model is implemented
  ([`c824555`](https://github.com/apajon/lifecore_ros2/commit/c8245552f63b3900547d6587c3e75c22166c20fe))

- **todo**: Replace verbose planning notes with concise pre-release and backlog sections
  ([`2dee894`](https://github.com/apajon/lifecore_ros2/commit/2dee89457126d2313ab1463547ab4b0388a720c1))

- **todo**: Track post-release README badges in backlog
  ([`5dd480f`](https://github.com/apajon/lifecore_ros2/commit/5dd480f6d025305c1af6895650c20d1056d7807b))

### Continuous Integration

- Add CI workflow (pull_request + dispatch only)
  ([`ae87b0c`](https://github.com/apajon/lifecore_ros2/commit/ae87b0c784e52956d7ef127cbf50ba072b1ca87f))

- Bump astral-sh/setup-uv from v6 to v8.1.0
  ([`b3df510`](https://github.com/apajon/lifecore_ros2/commit/b3df510638366af0835c86f1b5c0bfb608cf2fab))

- Fix git safe.directory for ros:jazzy container job
  ([`12f20e2`](https://github.com/apajon/lifecore_ros2/commit/12f20e208305f2423c25401ee2480c8057ea1837))

- Install numpy into uv venv instead of system apt
  ([`e74b733`](https://github.com/apajon/lifecore_ros2/commit/e74b733708cd061d7e9f5ab4ef6b2fa8559f6f3b))

- Install python3-numpy missing from ros:jazzy base image
  ([`f17fda4`](https://github.com/apajon/lifecore_ros2/commit/f17fda43ddaec4126d0d79ee9fdbaab527be9a11))

- Restore missing setup-uv step in validate job
  ([`429841f`](https://github.com/apajon/lifecore_ros2/commit/429841f3185bd66f6b1aefc8c39d3530127af9a9))

- Use ros:jazzy container image instead of setup-ros action
  ([`4af6eba`](https://github.com/apajon/lifecore_ros2/commit/4af6eba886023fca98dc834547f8b250fe5f608c))

- **release**: Remove cron schedule, add lint gate before semantic-release
  ([`aaa8a66`](https://github.com/apajon/lifecore_ros2/commit/aaa8a666f5f8739f5aed9c4413b776f0fd20a258))

### Documentation

- Add CONTRIBUTING.md
  ([`08f066d`](https://github.com/apajon/lifecore_ros2/commit/08f066d553689b1305921e0f8ea74aa7cc0821ed))

- Add member convention and autodoc skip hook
  ([`221f004`](https://github.com/apajon/lifecore_ros2/commit/221f0045c1feff5bbf05400b7de031a34601fea0))

- Add patterns, anti-patterns, and migration-from-rclpy pages
  ([`3a10935`](https://github.com/apajon/lifecore_ros2/commit/3a10935c4bde067ac19c17a8b999ded7d8ff62cb))

- Add recording script and infrastructure for composed_pipeline demo
  ([`7dbc11b`](https://github.com/apajon/lifecore_ros2/commit/7dbc11b28d8cde4277f1773b43f3e9684eb62f58))

- Adopt canonical positioning sentence across public surfaces
  ([`0fb2cb3`](https://github.com/apajon/lifecore_ros2/commit/0fb2cb3b19a610171b9d0496954a6038e9ec2019))

- **5.5**: Wire companion repo signposts and mark TODO 5.5 complete
  ([`e96000c`](https://github.com/apajon/lifecore_ros2/commit/e96000ce47b524aa1647bee4b92f2a004ab66bb9))

- **architecture**: Add ownership, transition sequence, and resource lifecycle sections
  ([`8a19898`](https://github.com/apajon/lifecore_ros2/commit/8a198984bc4c55b2f5d8f8535d5b6dac09b44d70))

- **architecture**: Correct _is_active invariants and document three missing guarantees
  ([`aa17a11`](https://github.com/apajon/lifecore_ros2/commit/aa17a1115b757e95e23084c812730734b37acf38))

- **architecture**: Document the four error policy rules
  ([`765d423`](https://github.com/apajon/lifecore_ros2/commit/765d423753cf29607d70696c1ae0f6875258ff9e))

- **changelog**: Add curated first-release v0.4.0 entry
  ([`c2625de`](https://github.com/apajon/lifecore_ros2/commit/c2625de7ca636d45e1c58189ff4e3b9df1307ba1))

- **changelog**: Align preamble with version list; update shipped state and base class wording
  ([`643e4af`](https://github.com/apajon/lifecore_ros2/commit/643e4af0824eb7bd48f66034adedf957dba995d6))

- **examples**: Add full observability contracts to all example docstrings
  ([`2f369d9`](https://github.com/apajon/lifecore_ros2/commit/2f369d969e0ca371133cc68f67a83fc096c238d0))

- **examples**: Add telemetry_publisher and composed_pipeline sections
  ([`3132e42`](https://github.com/apajon/lifecore_ros2/commit/3132e429e3a3170dc014decf9f4d75ed7a52455d))

- **examples**: Fix Composed Pipeline structure and add Reactivation Cycles section
  ([`382b82a`](https://github.com/apajon/lifecore_ros2/commit/382b82aee8372fafdbaf11004b3b1cee9d8b9b73))

- **examples**: Update minimal examples with explicit MsgT parameterization
  ([`ecb40f4`](https://github.com/apajon/lifecore_ros2/commit/ecb40f4d88ee7e7d0072167d70142f7dc9d02b2c))

- **examples.rst**: Add Observability Format convention section
  ([`629ed65`](https://github.com/apajon/lifecore_ros2/commit/629ed65c9f5826e85d146f559f00ab2a4b8dd160))

- **faq**: Add FAQ page covering positioning and API stability
  ([`f10a12c`](https://github.com/apajon/lifecore_ros2/commit/f10a12cf7d7c2ee0040910ba298b1cad25cb5887))

- **guides**: Normalize validation commands to bare uv run form
  ([`cbf6b24`](https://github.com/apajon/lifecore_ros2/commit/cbf6b240990eddf6756aee356acdffda6a1210b1))

- **patterns**: Add super()._on_configure seealso and on_message exception anti-pattern
  ([`c6853cf`](https://github.com/apajon/lifecore_ros2/commit/c6853cf38378af9db1cf1b8b14c14fc767ee5846))

- **readme**: Add CI workflow status badge
  ([`6169a70`](https://github.com/apajon/lifecore_ros2/commit/6169a7071ae773790ca68368450dcdda7045973d))

- **readme**: Add Docs and Release workflow status badges
  ([`71f1e47`](https://github.com/apajon/lifecore_ros2/commit/71f1e47b7949d10a3b51bb0d192ac114e19a468c))

- **readme**: Add license badge and link to GitHub Releases
  ([`9ad085a`](https://github.com/apajon/lifecore_ros2/commit/9ad085a0d1379141980d763a7b3bbe0dc685b562))

- **README**: Align minimal example, normalize commands, remove stale claims
  ([`33b9cee`](https://github.com/apajon/lifecore_ros2/commit/33b9cee50d070eb9bfdead19fcc7569937e98d08))

- **readme**: Rewrite as problem-first landing page
  ([`48679bb`](https://github.com/apajon/lifecore_ros2/commit/48679bb8148b366e7cc4229026b2a2ca9f870fc4))

- **release**: Draft v0.4.0 GitHub release notes
  ([`02ab28a`](https://github.com/apajon/lifecore_ros2/commit/02ab28afd6f2f4302eb6a1755a25bd87b37abbe9))

- **roadmap**: Close TODO 3.5 and update public API surface
  ([`9855776`](https://github.com/apajon/lifecore_ros2/commit/9855776629fd709255737d03457091fd731a57e6))

- **sphinx**: Add changelog page and integrate into toctree
  ([`ffddf7f`](https://github.com/apajon/lifecore_ros2/commit/ffddf7fb966cf92b5c87b4c46cd7e9592b1ed705))

- **sphinx**: Move mempalace_strategy to Contributing toctree; document autodoc filter
  ([`2b84552`](https://github.com/apajon/lifecore_ros2/commit/2b8455281870a50433eb8e54902b9945fd550e35))

- **todo**: Add 7.4 GitHub release text implementation strategy
  ([`e0f3102`](https://github.com/apajon/lifecore_ros2/commit/e0f31028d2869b9c7f86b4bb59b75b54955e8937))

- **todo**: Mark §7.2 complete and record positioning-sentence decision
  ([`588af60`](https://github.com/apajon/lifecore_ros2/commit/588af604f7c035c69a7fb9d5a103cff95b46989a))

### Features

- **5.5**: Add planning artifacts for lifecore_ros2_examples companion repo
  ([`55a7227`](https://github.com/apajon/lifecore_ros2/commit/55a72271252e29e5ba75049e7ca672f792f1fc5f))

- **components**: Tag extension points and seal _on_message_wrapper
  ([`058260f`](https://github.com/apajon/lifecore_ros2/commit/058260fd219d2b5d29b8799423207792f36d2a49))

- **core**: Add LifecoreError exception hierarchy
  ([`222fe59`](https://github.com/apajon/lifecore_ros2/commit/222fe5949425e69ea00810b88d2ed20b8a456631))

- **core**: Apply error policy to lifecycle components
  ([`9155ce8`](https://github.com/apajon/lifecore_ros2/commit/9155ce853637903eeacb428877443a7d38b565ea))

- **core**: Seal lifecycle entry points with @final
  ([`69a5d1e`](https://github.com/apajon/lifecore_ros2/commit/69a5d1e1eeb9eccbcd11c17cef743c0cf4e81044))

- **examples**: Add composed_pipeline.py multi-component example
  ([`a360ada`](https://github.com/apajon/lifecore_ros2/commit/a360adab3d301f8eadc0ffb40c3a988e57e8f22c))

### Testing

- Add error policy regression matrix
  ([`a69843c`](https://github.com/apajon/lifecore_ros2/commit/a69843c0caaa05eaebe7a5fa3760d133b9b89fa8))

- **typing**: Pin LifecoreError MRO via static smoke check
  ([`58381fe`](https://github.com/apajon/lifecore_ros2/commit/58381fe035c86eccc01f2b8900d3ccc94474e1a7))


## [Unreleased]

### Chores

- **typing**: Topic components are now generic in the message type (`LifecyclePublisherComponent[MsgT]`,
  `LifecycleSubscriberComponent[MsgT]`, `TopicComponent[MsgT]`); `publish` and `on_message` carry
  concrete message-type constraints instead of `Any`. `LifecycleComponent.get_logger()` return type
  narrowed from `Any` to the private `_LoggerLike` Protocol. Pyright strict mode enabled for the
  core package via `[tool.pyright]` in `pyproject.toml`.

## v0.3.0 (2026-04-20)

### Bug Fixes

- **release**: Replace uv build_command with pip-based fallback for PSR Docker env\n\nuv is not
  available in the python-semantic-release Docker container.\nReplace `uv run --extra dev python -m
  build` with\n`python -m pip install build && python -m build`, which works in any\nstandard Python
  environment. The build frontend still uses PEP 517\nisolated builds, so no dev extras are needed.
  ([`9f7670f`](https://github.com/apajon/lifecore_ros2/commit/9f7670f9c49f9bb327201fdc003061c0c63001e7))

### Chores

- Mark TODO 2.2–2.5 as complete
  ([`d88fcb5`](https://github.com/apajon/lifecore_ros2/commit/d88fcb548dd1c624e867bc812443db0bc213e11c))

- **copilot**: Add naming conventions section to copilot-instructions and naming-conventions
  instruction file
  ([`d58981d`](https://github.com/apajon/lifecore_ros2/commit/d58981d05672130ff53ca14d868fb8ab98f0cd84))

- **copilot**: Relocate ROS2 architecture instruction and add historize prompt
  ([`b4e8cf0`](https://github.com/apajon/lifecore_ros2/commit/b4e8cf0856404c8fa728b0a6b92e8dc986ea4272))

- **examples**: Align with framework-managed lifecycle
  ([`763e7e1`](https://github.com/apajon/lifecore_ros2/commit/763e7e118b0e13444b68e2224c72daaffd88fbf0))

- **mempalace**: Add similarity threshold
  ([`994cd2e`](https://github.com/apajon/lifecore_ros2/commit/994cd2e3e11fce617a25f7e68d4e61f69157f6a2))

- **todo**: Mark §3.2 complete in TODO_2.md
  ([`3cca5e1`](https://github.com/apajon/lifecore_ros2/commit/3cca5e14659f89dcd99a3b54ee0d884c49be5c30))

### Documentation

- Add ROADMAP.md and close TODO_2.md 1.1
  ([`5ec22cc`](https://github.com/apajon/lifecore_ros2/commit/5ec22ccb2f054f9ec14a5cd51a86f59b7c2d887f))

- Align guides and planning docs with renamed lifecycle API
  ([`e7f5687`](https://github.com/apajon/lifecore_ros2/commit/e7f5687404c504bfa702da9618718ac0b61f5ede))

- Document automatic semantic-release versioning flow
  ([`3622206`](https://github.com/apajon/lifecore_ros2/commit/362220602604aaa0ed7ec83f559b5e1019b2ad68))

- Document public API, extension hooks, and internal helpers in ROADMAP.md
  ([`dee4b9a`](https://github.com/apajon/lifecore_ros2/commit/dee4b9a68a50b527c568ee6bef3372b68e258c4d))

- Document versioning strategy and close TODO_2.md 1.2
  ([`3008bc4`](https://github.com/apajon/lifecore_ros2/commit/3008bc4371c439f11435adfeee65e55adf422ba9))

- Formalize lifecycle invariants in docstrings and architecture docs\n\nDocument
  configure/activate/deactivate/cleanup/shutdown/error contracts\nin LifecycleComponent class
  docstring and hook docstrings.\nAdd Lifecycle Invariants section to docs/architecture.rst.\nCovers
  TODO 2.1.
  ([`71e0251`](https://github.com/apajon/lifecore_ros2/commit/71e02513247a13d1f4460f35417631590a147f0a))

- Update copilot instructions for lifecycle renames
  ([`d72ca8d`](https://github.com/apajon/lifecore_ros2/commit/d72ca8d4ec1dcad8f185ca1246f162aeac07efe8))

- **components**: Add Owns/Does not own/Override points to TopicComponent, Publisher, and Subscriber
  docstrings
  ([`04f7877`](https://github.com/apajon/lifecore_ros2/commit/04f7877e11d2d31beba6a83898eb4155082bd24d))

- **core**: Add Owns/Does not own/Override points to LifecycleComponent and LifecycleComponentNode
  docstrings
  ([`5382beb`](https://github.com/apajon/lifecore_ros2/commit/5382beb059f1e3a23413af9bd3e4bc092539c272))

- **instructions**: Strengthen engineering and ops guidance
  ([`5dc70a3`](https://github.com/apajon/lifecore_ros2/commit/5dc70a32354c2b9c499c70e9eff70b04635291cf))

- **mempalace**: Extend standard room taxonomy
  ([`ecb2488`](https://github.com/apajon/lifecore_ros2/commit/ecb2488ae5c44ccd057e93560d9eac11640b4f23))

### Features

- Add ROS 2 architecture context instructions with mempalace fallback
  ([`625f2d0`](https://github.com/apajon/lifecore_ros2/commit/625f2d02589c395db418ca404652c3e8ee4e1f34))

- Consolidate mempalace strategy — unified naming, taxonomy, dedup, and persistence policies
  ([`4ba4c63`](https://github.com/apajon/lifecore_ros2/commit/4ba4c63c2afa8752ff532526718f53be0bc84f60))

- Rename lifecycle core and component public classes
  ([`8e6128b`](https://github.com/apajon/lifecore_ros2/commit/8e6128b1e3289999f1ddd16ceb0a07d1414cd20d))

- **core**: Add when_active decorator and activation state to LifecycleComponent\n\nInspired by
  rclpy SimpleManagedEntity.when_enabled, add a when_active\ndecorator that gates methods on
  component activation state:\n- @when_active → raises RuntimeError (default)\n-
  @when_active(when_not_active=None) → silent no-op\n- @when_active(when_not_active=fn) → calls fn
  instead of raising\n\nAlso centralizes _is_active flag and is_active property in the base\nclass,
  with _on_activate/_on_deactivate managing the flag via super().\nMakes _release_resources abstract
  to enforce override in subclasses."
  ([`30ee3c4`](https://github.com/apajon/lifecore_ros2/commit/30ee3c48b22c5b49c69cbb565cee9abe26e9c579))

### Refactoring

- Rename module files to match class names
  ([`a5efcbb`](https://github.com/apajon/lifecore_ros2/commit/a5efcbb48c042529089547da4a2b420562db5ac1))

- **components**: Simplify to framework-managed lifecycle
  ([`4f49e2c`](https://github.com/apajon/lifecore_ros2/commit/4f49e2c9f05fb60320edf0853fba41828d5230bd))

- **components**: Use when_active decorator and delegate state to base\n\nRemove duplicated
  _is_active flag, is_active property, and manual\nactivation gating from PublisherComponent and
  SubscriberComponent.\n\n- publish() now uses @when_active (raises RuntimeError by default)\n-
  _on_message_wrapper() uses @when_active(when_not_active=None) (no-op)\n-
  _on_activate/_on_deactivate delegate to super() for flag management\n- _release_resources calls
  super()._release_resources() for flag reset"
  ([`c17380a`](https://github.com/apajon/lifecore_ros2/commit/c17380a3182b20e9717fdb269cbbee400d44e059))

- **core**: Enforce framework-managed lifecycle invariants
  ([`50307b5`](https://github.com/apajon/lifecore_ros2/commit/50307b50bd24433d7b1aa3e7a9c57d6cb617fe35))

### Testing

- Adapt stubs and assertions for abstractmethod and when_active changes
  ([`9a81a0d`](https://github.com/apajon/lifecore_ros2/commit/9a81a0d59afe6d417c447e20b2b4eed7121767b2))

- Add threaded registration and double-transition regression tests
  ([`3201c14`](https://github.com/apajon/lifecore_ros2/commit/3201c1430140ddfc6fc1e2176d1be6ac13e6b1ff))

- Update existing tests for framework-managed lifecycle
  ([`22c5b5d`](https://github.com/apajon/lifecore_ros2/commit/22c5b5d35d8117b2e3c845626a5268767bc98203))

- **2.2**: Add happy-path coverage for all component types
  ([`3bb9da9`](https://github.com/apajon/lifecore_ros2/commit/3bb9da9ac4224774bf0d0274d6039218f3621bab))

- **2.3**: Add edge and invalid lifecycle transition tests
  ([`ec138bb`](https://github.com/apajon/lifecore_ros2/commit/ec138bbc92f7aef56fb7c66031399051b01de3f6))

- **2.4**: Add failure propagation and exception guard tests
  ([`4350e98`](https://github.com/apajon/lifecore_ros2/commit/4350e988f180e9757039fa70351a96464d5d24b0))

- **2.5**: Add strict publisher and subscriber activation gating tests
  ([`aa6fc88`](https://github.com/apajon/lifecore_ros2/commit/aa6fc88170f1b6581bae3e74a4e165613458b0e4))


## v0.2.0 (2026-04-08)

### Bug Fixes

- **components**: Align QoS typing and implement _release_resources
  ([`8f73b7d`](https://github.com/apajon/lifecore_ros2/commit/8f73b7d1b7cf64bd8f2d026fac4ab885743a507d))

- **release**: Ensure build is available in semantic-release container
  ([`9716aca`](https://github.com/apajon/lifecore_ros2/commit/9716acab63453e322171538320a8f627373d9dcc))

- **types**: Add PEP 561 typing markers for package and core
  ([`082546c`](https://github.com/apajon/lifecore_ros2/commit/082546cdff65bb3f3726005edf15a5aa5a9ccb68))

### Chores

- Organize copilot agents into tools/copilot
  ([`075e677`](https://github.com/apajon/lifecore_ros2/commit/075e6775db2b75283339f2d4761848615c40dba1))

- Update publisher example log format and check off TODO items 4.3
  ([`504d161`](https://github.com/apajon/lifecore_ros2/commit/504d161f4fe2674288e17bb587c950911ab7bc96))

- Update pyproject.toml license, deps, and py.typed marker
  ([`a044fe9`](https://github.com/apajon/lifecore_ros2/commit/a044fe974b0f8d0254ce924573afec645271a71f))

- **instructions**: Enforce uv run instead of python/python3
  ([`52f6664`](https://github.com/apajon/lifecore_ros2/commit/52f66647186ff25c721ebf2c2f30cbb4fade85a4))

- **instructions**: Enforce uv run policy and forbid direct pip usage
  ([`1dfc7c6`](https://github.com/apajon/lifecore_ros2/commit/1dfc7c613d7acb3d13eaf7142a2c19e98c9e2772))

- **pytest**: Disable ROS launch_testing plugins and configure testpaths
  ([`2eac26c`](https://github.com/apajon/lifecore_ros2/commit/2eac26cd5cebd6212e03ac2e6ee0ed498165f0a8))

- **release**: Align semantic-release build and workflow for v0.0.1 readiness
  ([`0e5646a`](https://github.com/apajon/lifecore_ros2/commit/0e5646a2cf8dc41f72a8ad60547e0aded4431e9e))

- **version**: Stop tracking generated _version.py
  ([`03a9da0`](https://github.com/apajon/lifecore_ros2/commit/03a9da027727b1c1c0875fc7d7cd3ba2495bd72a))

### Continuous Integration

- **docs**: Reduce runs and align local docs workflow
  ([`651ca39`](https://github.com/apajon/lifecore_ros2/commit/651ca39f5a325294a59e331448557e64981c1d09))

### Documentation

- Add Sphinx baseline, docs CI, and docstring instruction
  ([`fd59ae6`](https://github.com/apajon/lifecore_ros2/commit/fd59ae65a3123263f25c4b5d0daa56a3a5c48391))

- Align documentation with current V0 state
  ([`f68d277`](https://github.com/apajon/lifecore_ros2/commit/f68d277049430e8b6c1c4f1e7364ae896747d3e2))

- **copilot**: Add copilot-instructions with lifecycle design rules and conventions
  ([`2b7d9b5`](https://github.com/apajon/lifecore_ros2/commit/2b7d9b5d3ec511c51b1eecfa38a6ab6c200acc8f))

- **examples**: Close step 4 with explicit subscriber activation walkthrough
  ([`3370900`](https://github.com/apajon/lifecore_ros2/commit/3370900a50cc76506a22e45b9a28e147cdab2828))

- **readme**: Add ROS setup and lifecycle transition walkthrough
  ([`0c0efa5`](https://github.com/apajon/lifecore_ros2/commit/0c0efa5cfd190fde71d195a2c92b833464c4a3de))

- **readme,todo**: Finalize V0 docs and mark phase 3 complete
  ([`06a1908`](https://github.com/apajon/lifecore_ros2/commit/06a19084ded7da4b5a808faf70e6024959c19a97))

- **todo**: Check off completed steps 2, 3, 4, 5, 6
  ([`e07bf28`](https://github.com/apajon/lifecore_ros2/commit/e07bf2878698a01e7b6c0b81aff50102599b7541))

- **todo**: Mark release/versioning v0 checklist complete
  ([`ad4491d`](https://github.com/apajon/lifecore_ros2/commit/ad4491d9eb6bef58a4c099f8e5d0ab49b7dee938))

### Features

- **components**: Add LifecycleSubscriberComponent and LifecyclePublisherComponent with correct _on_* overrides
  ([`ed2a907`](https://github.com/apajon/lifecore_ros2/commit/ed2a907ac72e0d5a9f60fbbdafddfd61c677eda7))

- **components**: Add TopicComponent base class for topic-aware lifecycle components
  ([`e6448ba`](https://github.com/apajon/lifecore_ros2/commit/e6448bad0e4b208940e0f096b0c77db7097342b8))

- **core**: Registration guard, atomic add_component, typed decorator, and resource cleanup pattern
  ([`e0db1ee`](https://github.com/apajon/lifecore_ros2/commit/e0db1ee1f49500f3d12c641140c2788ad1e0f9fc))

- **examples**: Add minimal_publisher with periodic String publishing
  ([`ff922bc`](https://github.com/apajon/lifecore_ros2/commit/ff922bcc1a52ed92cf88184924e655a578ad8f1e))

- **examples**: Add minimal_subscriber example with EchoSubscriber
  ([`effa272`](https://github.com/apajon/lifecore_ros2/commit/effa272cb85063e7c141bd0ca31b6312c5836d5c))

### Refactoring

- **examples**: Move rclpy imports inside main() in minimal_node
  ([`05b2736`](https://github.com/apajon/lifecore_ros2/commit/05b2736dd3824c3b8e993daa5546720592a83ff3))

- **exports**: Re-export all components and core classes from package root
  ([`0566228`](https://github.com/apajon/lifecore_ros2/commit/05662283677356acc566319e4f2918f9d54f0f17))

### Testing

- Add minimal test suite for core, lifecycle, and topic components
  ([`4e668ca`](https://github.com/apajon/lifecore_ros2/commit/4e668ca67c6937df884018cb601607a612e33416))

- Add regression, integration, and smoke tests
  ([`a303636`](https://github.com/apajon/lifecore_ros2/commit/a3036369ebdfc4dde4f14ad061c55ec88d194524))


## v0.1.0 (2026-04-03)

### Bug Fixes

- **version**: Align generated version file with v0.1.0 tag
  ([`dbe0002`](https://github.com/apajon/lifecore_ros2/commit/dbe00025fdc5724930cac27d3e90c4e2b750a892))

### Chores

- **deps**: Add numpy runtime dependency
  ([`a87935b`](https://github.com/apajon/lifecore_ros2/commit/a87935b4ddfd0fd006190c1e705b57e91d92c6bd))

- **version**: Refresh scm version metadata
  ([`cec4c7d`](https://github.com/apajon/lifecore_ros2/commit/cec4c7db5da7c7f7b5c188fdceef3a37b7df9381))

### Features

- **core**: Add composed lifecycle node and component base
  ([`a540053`](https://github.com/apajon/lifecore_ros2/commit/a5400530f71ca78cafe2fc7da87ffe59e9f01c82))

- **example**: Add minimal composed lifecycle node sample
  ([`a1f88f3`](https://github.com/apajon/lifecore_ros2/commit/a1f88f33a3725a4513d6c3a32d97313327c3d663))


## v0.0.1 (2026-04-03)

- Initial Release
