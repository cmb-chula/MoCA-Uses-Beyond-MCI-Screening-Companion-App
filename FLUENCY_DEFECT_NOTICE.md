# ADVISORY — subtype labels in this work carry the verbal-fluency scoring defect

**Work:** `cascade_moca_app`
**Date:** 2026-08-06
**Type:** **ADVISORY NOTICE — this is _not_ a retraction.**

> **Nothing in this work has been moved, renamed, deleted or edited.** Every existing output,
> figure, log and label file is exactly where it was and byte-identical. This file was *added*
> alongside them. If you are a scheduled validator diffing regenerated-vs-recorded output, your
> comparator is intact.

---

## 1. What is affected

The cognitive-subtype labels this work consumes descend from the `mci_moca_pipeline` derivation.
That derivation was run on a KCMH frame in which **verbal (letter) fluency was scored at
≥ 12 words**. The MoCA rule is **≥ 11**. Correcting the threshold changes **which participants fall
into which cognitive phenotype** — the membership of every phenotype moves.

**The defect is in the DATA, not in the code.** A portfolio-wide sweep
(`mci_moca_leiden_pipeline/audit/FLUENCY_DEFECT.md` §2) found **zero defective threshold sites in
live code** — every live scorer already applies the correct rule. The contamination is inherited
through the label files and through every artifact built from them. **Re-running this work against
its current inputs reproduces the defect faithfully.** No code change here fixes it; only new label
inputs do.

## 2. Replacement

⛔ **There is no replacement for this work yet — this notice deliberately does NOT say
"superseded by", because there is nothing to supersede it.**

This work sits in the **cascade lineage**, whose 27 subtypes are 11 de-novo tier-A/B/C clusters plus
a pass-through of the mci_moca phenotypes in tiers D and E. `cascade_moca_pipeline` is Wave 2 of
the migration and **has not been started**, so no corrected cascade label set exists. The cascade
lineage cannot start until the source derivation is final, which G5 and G6 currently block.

## 3. Gate status — both open

| Gate | Status | What it is |
|---|---|---|
| **G5** | ⛔ **OPEN** | The Wave 0 peer sanity check (**W0.14**) returned a verdict of **REWORK**: Wave 0 is not yet safe for the 40 dependent works. Four blockers; three still open — small-cell exposure in docs and tests, the retracted-and-unreplaced W0.10 safety gate, and the missing clean-checkout byte-identity gate (G4 must re-run at HEAD). |
| **G6** | ⛔ **OPEN** | An **unresolved contradiction** with the 2026-07-29 parameter sweep (SLURM 389697, 389724) over whether the corrected partition is a defensible eight. That sweep recorded *"no defensible eight-phenotype setting was found"* and **only five of eight strong centroid matches**; Wave 0 claims **eight of eight**. Both cannot be true. If only five phenotypes genuinely correspond, then reusing all eight published keys makes **three changed populations look unchanged** to every consumer — more dangerous than renaming them. |

Authoritative source for both: `/data/project/cuaim/dhup/Research_Pipelines/SUBTYPE_MIGRATION_GRAND_PLAN.md` §3.

## 4. What this notice does and does not mean

- ✅ It is **advisory**. It records a known defect in the provenance of this work's inputs so that
  nobody reads its outputs without that context.
- ⛔ **Results from this work should not be cited as final while G5 and G6 are open.** That includes
  manuscripts, abstracts, slides, grant text and the dashboard.
- ❌ It is **not** a retraction, and it does **not** assert the results are wrong. The corrected
  partition is **not** claimed to be clinically better than the published one — see
  `mci_moca_leiden_pipeline/MIGRATION_PLAN.md` §0 for the forbidden-claims table. The reason to
  migrate is a scoring defect, not a performance gain.
- ❌ It does **not** authorise re-pointing this work at new labels. Migration is gated: see the
  eight-step per-work procedure in `SUBTYPE_MIGRATION_GRAND_PLAN.md` §8, and this work's own
  `SUBTYPE_MIGRATION.md` if it has one.
- ⚠️ **Arity is not the issue.** Owner decision **1C** keeps the count at eight, so nothing here
  silently mis-keys. What moved is **membership** — which means every estimate, figure and table
  built on these labels is computed over a different set of people.

## 5. Where to read more

| | |
|---|---|
| Programme tracker | `/data/project/cuaim/dhup/Research_Pipelines/SUBTYPE_MIGRATION_GRAND_PLAN.md` |
| Corrected pipeline + detail plan | `/data/project/cuaim/dhup/mci_moca_leiden_pipeline/MIGRATION_PLAN.md` |
| The defect sweep | `/data/project/cuaim/dhup/mci_moca_leiden_pipeline/audit/FLUENCY_DEFECT.md` |
| Dependency inventory (corrected 2026-08-06) | `/data/project/cuaim/dhup/mci_moca_leiden_pipeline/audit/DOWNSTREAM_INVENTORY.md` §0 |
| Why nothing was archived | `/data/project/cuaim/dhup/Research_Pipelines/audit/FLUENCY_ARCHIVE_20260806.md` |
