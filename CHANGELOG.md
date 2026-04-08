# CHANGELOG

<!-- version list -->

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

- **components**: Add SubscriberComponent and PublisherComponent with correct _on_* overrides
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
