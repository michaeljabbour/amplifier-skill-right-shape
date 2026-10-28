---
bundle:
  name: right-shape
  version: 0.2.1
  description: >-
    Decides what shape a piece of AI work should take, how much autonomy it can
    safely have, which engine it needs, and how to benchmark it: the right-shape
    skill, a /shape working mode, and a staged, human-gated audit recipe.

# Thin root: a lean host plus this bundle's behavior. Most users should add only
# the behavior to their existing host (see README).
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main#subdirectory=bundles/anchors/bundle.md
  - bundle: right-shape:behaviors/right-shape
---

@anchors:context/system.md
