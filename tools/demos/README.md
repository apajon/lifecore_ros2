# Demo recordings

Maintainer-local toolchain for producing the GIF asset embedded in `README.md`
(`docs/_static/composed_pipeline_demo.gif`).

> This toolchain is intentionally **not** declared in `pyproject.toml` or any
> `uv` group: `asciinema` and `agg` are only needed by the maintainer when
> regenerating the asset, not by users or CI.

## Prerequisites

- ROS 2 Jazzy sourced in the current shell (`source /opt/ros/jazzy/setup.bash`).
- The repository's `uv` environment is **not** required: the script invokes
  `python examples/composed_pipeline.py` directly. Make sure the active
  interpreter has `lifecore_ros2` importable (e.g. `source .venv/bin/activate`
  after `uv sync --extra dev`).
- [`asciinema`](https://docs.asciinema.org/manual/cli/installation/) installed
  locally.
- [`agg`](https://github.com/asciinema/agg#installation) (asciinema GIF
  generator) installed locally. Tested with `agg` 1.7.0, which emits GIF only.

## Reproduction

From the repository root, with ROS 2 Jazzy sourced and the project venv active:

```bash
rm -f demo.cast
asciinema rec --overwrite -c ./tools/demos/record_composed_pipeline.sh demo.cast
agg --font-size 14 --theme monokai demo.cast docs/_static/composed_pipeline_demo.gif
```

The script targets ≤ 60 s of wall time and is fully deterministic: no host
paths, no secrets, stable `PS1`, and a `trap` that always reaps the background
node process.

## What the recording shows

The script walks `examples/composed_pipeline.py` through every native ROS 2
lifecycle transition and inspects the ROS graph at each step:

1. **before configure** — `ros2 lifecycle get` reports `unconfigured`;
   `/pipeline/*` topics are absent.
2. **configure** — topics appear; `timeout 3 ros2 topic echo /pipeline/avg`
   stays silent (activation gating).
3. **activate** — `timeout 4 ros2 topic echo /pipeline/avg` streams averaged
   values.
4. **deactivate** — echo goes silent again, **but `/pipeline/*` topics are
   still listed**. This is the key frame: deactivate ≠ cleanup.
5. **cleanup** — `/pipeline/*` topics disappear.
6. **shutdown** — node exits cleanly.

## Exit-gate checklist

Before committing the regenerated SVG, verify:

- [ ] `docs/_static/composed_pipeline_demo.gif` is ≤ 2 MB.
- [ ] All six transitions are visible in the rendered GIF.
- [ ] The deactivate-vs-cleanup contrast is unambiguous: after
      `deactivate`, the `ros2 topic list | grep ^/pipeline/` line still shows
      `/pipeline/raw` and `/pipeline/avg`; only after `cleanup` does it report
      `(no /pipeline/* topics)`.
- [ ] PyPI long-description renders the embedded image correctly
      (`uv build && uv run --with twine twine check dist/*`, then inspect the
      rendered HTML at https://pypi.org/project/lifecore_ros2/ after release —
      or render locally with `readme_renderer`).
