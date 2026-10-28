# Worked examples

Everything on this page is fictional: the organizations, the jobs, the repositories and the numbers. The placements follow the rubric exactly; the site's build recomputes them and refuses any that do not.

## Place: a weekly grant-report formatter

**Request.** "A small nonprofit wants an agent that turns its program notes into the funder's report format every Friday."

```
VERDICT  Smart Tool at rung 1, engine LLM. The path is fixed and nobody needs to watch it.
NEED     N1 1  N2 1  N3 0  N4 1  = 3 -> rung 2
CEILING  9  (failed: none)
TIEBREAK It repeats weekly and the format is stable: seal it in a Smart Tool, one rung down.
SHAPE    single  (none of H1 to H4)
REPLACEABILITY  R5 gap: name which formatting rule the model gets wrong today, so you know when to drop the fix.
BENCHMARK
  L0 installs and formats the three sample notes offline
  L1 twelve past reports with planted traps (a missing figure, a renamed program, a note that should be left alone); beats baseline and placebo on funder-format compliance; threshold 11 of 12
  L3 not measured
QUESTION  none
```

## Place: inbox triage for a small law office

**Request.** "Let an agent read the office inbox, draft replies and schedule client meetings on its own."

```
VERDICT  Interactive agent at rung 5, engine both. It reads untrusted mail, holds client data and can send. That's the trifecta.
NEED     N1 3  N2 2  N3 3  N4 3  = 11 -> rung 8
CEILING  5  (failed: G2 Reversibility, G3 Trifecta broken)
HONEST MOVE  Split it. An always-on reader in a sandbox with no send capability (the trifecta is broken, so it can run higher), plus drafts a person approves before anything leaves.
SHAPE    single  (H1)
REPLACEABILITY  R4 gap: client memory must not live inside the mail client.
BENCHMARK
  L1 forty fictional emails including two prompt-injection attempts and one privileged message; zero sends without approval; drafts preferred by blinded reviewers over baseline
  L2 triage labels agree with two paralegals on at least 90%, with test-retest stability
  L3 not measured
QUESTION  Can the reader run without any outbound channel at all?
```

## Place: a release pipeline for a mobile app team

**Request.** "Turn an approved plan into a shipped app update with as little human time as possible."

```
VERDICT  Outer harness at rung 6 behind an agent interface, engine both. Many workers, one face, a person approves the release.
NEED     N1 3  N2 3  N3 2  N4 1  = 9 -> rung 7
CEILING  6  (failed: G2 Reversibility, because store releases are hard to undo)
HONEST MOVE  Keep a human approval at plan intake and before store submission.
SHAPE    outer harness  (H1, H2, H3)
REPLACEABILITY  R2 gap: the test agent is hard-wired to one model; put it behind the verifier contract.
BENCHMARK
  L0 builds the sample app from a clean checkout
  L1 ten fictional plans with planted defects (a flaky test, a missing permission, a plan that should be refused); defects caught, false alarms, time to a reviewable build
  L2 release-readiness calls agree with two senior engineers on at least 9 of 10
  L3 not measured
QUESTION  none
```

## Audit: a fictional robotics lab's fourteen repositories

**At a glance.** Fourteen public repositories become five capabilities. Two are archived, two are forks of upstream projects, one is platform code, and one folds into it. The highest-leverage move is extracting the lab's three separate evaluation scripts into one shared harness.

**How it was gathered.** The listing was read in full. Fork status was confirmed from repository metadata.

| Repository | Current shape | Disposition | Target |
| --- | --- | --- | --- |
| grasp-planner | Library + CLI | Keep | Grasp Planner (Smart Tool) |
| grasp-planner-mcp | MCP server | Consolidate | Grasp Planner |
| grasp-eval | Scripts | Extract | Shared evaluation harness |
| sim-eval | Scripts | Extract | Shared evaluation harness |
| nav-eval | Scripts | Extract | Shared evaluation harness |
| field-notes-skill | Skill | Rename | Field Log (its command is already `fieldlog`) |
| lab-onboarding | Docs + skill | Keep | Lab Guide (skill) |
| lab-onboarding-old | Docs | Archive | Lab Guide |
| robot-runtime | Service | Platform | Runtime |
| telemetry-hook | Hook module | Fold | Runtime |
| vision-agent | Bundle (private dependency) | Restructure | Scene Reader, after the dependency is published |
| vision-agent-v0 | Stub | Archive | Scene Reader |
| ros-bridge | Fork | Fork | Upstream bridge; delete unless it carries changes |
| sim-world | Fork | Fork | Upstream simulator |

**Questions for the owner.** Publish the vision dependency or vendor it? Does the ros-bridge fork carry changes? Should Field Log keep its old name for existing users?
