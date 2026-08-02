# Material/Inventory native dev release evidence

This evidence verifies the M1R Material/Inventory projection after publication to the
canonical OS development branch. OS and FE were started as independent native
processes; the browser consumed the real OS Material API without route mocks or the
retired Inventory endpoint.

## Exact revisions

| Component | Branch | Tested revision |
| --- | --- | --- |
| OS | `deepmodeling/Uni-Lab-OS:dev` | `5cd7913a4b6a2dbbd85c8e055e7851a6e5c60773` |
| FE | `Uni-Lab-OS/uni-lab-fe:integration/fe-os-migration` | `65588b75272747a48bc260dc28ddf799ef229280` |
| SZLab | `Uni-Lab-OS/Uni-Lab-SZLab:main` | `305b0cf2baacb24a6d34d4ec306ef6ba2177e513` |

The OS release commit is a non-squash merge with parents
`1331701f9681e2aa71f706e74f746b5a04b74a70` (canonical `dev`) and
`de95b9965ed551ed2ed1581fe2bd3100e1b93672` (WorkflowTask integration).

## Native startup

OS was launched through the public `unilab` CLI with the SZLab workspace and graph,
ROS backend, FastAPI bridge, Edge Scheduler, isolated `inventory.db`, and test mode:

```text
PYTHONPATH=$OS_ROOT:$SZLAB_ROOT unilab \
  --workspace $SZLAB_ROOT \
  --graph $SZLAB_ROOT/deployment/graphs/szlab-ideawit-sim.json \
  --config $SZLAB_ROOT/deployment/local_config.py \
  --working_dir $RUNTIME_ROOT \
  --backend ros --app_bridges fastapi --edge_scheduler \
  --visual disable --port 18148 --disable_browser \
  --skip_env_check --ros_domain_id 148 --test_mode
```

FE was launched separately from its exact integration revision:

```text
pnpm --filter @unilab/kernel-web dev --host 127.0.0.1 --port 14176
```

The visual check ran in Xvfb headed Chromium with SwiftShader WebGL so the real Pascal
3D canvas, rather than the no-WebGL capability fallback, was exercised.

## Result

- OS full suite at the release merge: `2311 passed, 4 skipped`.
- Merge delta: fatal Ruff rules, scoped production compile, import smoke, and
  `git diff --check` passed.
- MaterialGraph: 21 nodes; Material shape catalog: 12 declarations.
- 2.5D: 21 material nodes, 13 spec-driven shapes, 2 vial stacks, 2 beaker stacks.
- 3D: real Pascal canvas visible at 1356×923 with `21 个物料 · 只读`.
- FE Material traffic, excluding health checks, was exactly
  `GET /api/v1/materials/graph` and `GET /api/v1/material-shapes`.
- No retired `/api/v1/inventory/*` call, failed observed API/model response,
  `console.error`, or `pageerror` occurred.

The machine-readable ledger and screenshot checksums are in
[`native-e2e-summary.json`](native-e2e-summary.json).

## Visual evidence

1. [Complete SZLab 2.5D Material projection](01-szlab-materials-2_5d.png)
2. [Complete SZLab Pascal 3D Material projection](02-szlab-materials-3d.png)

## Baseline notes

The repository-wide `compileall` remains blocked by the pre-existing
`unilabos/devices/cytomat/cytomat.py` syntax defect. Its blob is identical in both
release parents and the merge. Broad default Ruff also reports legacy style debt;
the release delta passed fatal correctness selectors and did not introduce those
baseline findings.
