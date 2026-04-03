# Data Dictionary

All files contain **aggregate statistics only** — no individual-level ADNI data.

## pathway_info.json
Static pipeline constants. No data dependency.
- `tier_order`, `tier_names`, `tier_ranges`, `tier_colors` — MoCA tier definitions
- `domains`, `domain_labels`, `domain_max` — 7 MoCA cognitive domains
- `pathways` — 3 cascade decline pathways with subtype sequences
- `cascade_subtypes` — 11 subtypes in the cascade network
- `petersen_palette`, `modality_colors` — Color palettes
- `survival_refs` — Reference groups for Cox models

## domain_profiles.json
Per-subtype median domain profiles (normalized 0-1).
- Key: subtype label (e.g., "0A", "3D")
- Value: `{n, tier, domains: {VIS: {median, q1, q3, mean, std}, ...}}`

## demographics.json
Aggregate demographics per subtype.
- Key: subtype label
- Value: `{n, tier, age_mean, age_std, pct_female, edu_mean, edu_std, mmse_mean, mmse_std, cdr_0, cdr_05, cdr_1plus, dx_dist}`
- All cells with n < 10 are suppressed.

## figures/
Pre-rendered PNG figures from the cascade_moca pipeline output.
These are publication-quality matplotlib figures at 300 DPI.
