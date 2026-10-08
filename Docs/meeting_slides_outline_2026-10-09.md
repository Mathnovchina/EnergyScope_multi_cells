# Meeting 2026-10-09 — slide outline + paste-ready concept-note fixes

Companion to [meeting_prep_2026-10-09_G4M_coupling.md](./meeting_prep_2026-10-09_G4M_coupling.md).
Sources: `concept_note_G4M_forest_energy_finland_V1.docx` (downloaded copy, saved 2026-10-08 13:38),
`paper_sections_draft.md`, Blattert et al. 2022 (Zotero `SJ5WFJ39`), Mönkkönen et al. 2024 (`YQIETF2I`),
[IIASA_Forest_Models_Briefing.md](./IIASA_Forest_Models_Briefing.md).

---

## Part A — One-page slide outline (7 slides, ~30 min)

| # | Title | Content (keep to 3 bullets) | Time |
|---|---|---|---|
| 1 | **Where we are** | Paper 1 done: calibrated 2017 baseline (1.2% weighted error, CO₂ +0.1%); 2035 wood supply curves S1/S2/S3 × {unconstrained, −95%, −95% no nuclear}. | 2 |
| 2 | **Headline results** | 2035 already ~70% below 2017 unconstrained; under −95% S3 saturates its 40 TWh ceiling and is the costliest (23.56 vs 23.02 bn€/y with nuclear); without nuclear S1/S2 use ~96–100 TWh, S3 cannot expand. *Figure: `forest_scenarios_2035_*.png`.* | 3 |
| 3 | **Two gaps** | (1) Curves are static, assumption-built (S1 = +20% of S2; S3 = hand-scaled Mönkkönen chain, 74→40 TWh). (2) No forest sink: `Minimum_GWP_reduction` counts energy CO₂ only; biomass is carbon-neutral by assumption. | 4 |
| 4 | **Why the sink matters (and is not trivial)** | Blattert 2022: NFS sink up to 80 Mt/yr at end, BES 28; **BDS starts highest, then collapses and turns negative during its harvest peak.** → ranking of S1/S2/S3 on climate grounds is *time-dependent*; an energy-only model cannot see it. | 4 |
| 5 | **Proposed coupling** | G4M → (assortment volumes, ecological fractions, net forest + HWP flux) per scenario × GWL2/GWL3 → WOOD_FI2–FI4 + exogenous `S_forest(scenario, year)` in `Minimum_GWP_reduction`. FI1 (mill by-products, ~45%) kept from LUKE unless a yield bridge exists. One-way, no endogenous forest management. | 5 |
| 6 | **What we need from you (decisions D1–D8)** | G4M alone or via GLOBIOM (assortments)? Finland breakout + format? Deadwood pool explicit? Ecological fractions inside G4M? Industry/energy split? Growth model for Finland (G4M vs PREBAS)? | 8 |
| 7 | **Disturbances & BeWhere / next steps** | D3.4 treats disturbance as biomass loss only (no salvage recovery) → can IIASA/BOKU provide salvage volumes, or do we post-process? BeWhere/HWP extension scope with Schipfer/Tiwari. Next: I prototype sink term with Blattert placeholders; you confirm G4M deliverables. | 4 |

**Backup slides:** S3 scaling chain (Mönkkönen 96→58–60% → 81→49 Mm³ → residue 15–20% × collection 30–40% → 6 TWh FI2); 2017 residuals (district heat +43%, gas-CHP +37%, aggregation artefacts); supply-curve table (FI1 11, FI2 22/26, FI3 27, FI4 33, FI5 import 70 €/MWh).

**Backup slide (Rougieux / EU-CBM-HAT):** open JRC forest carbon model with FI data (CC BY 4.0, doi:10.2905/JRC.VR7ARNG); harvest is an input, sink is the output; explicit salvage logging; possible alternative or cross-check for S_forest. See prep note section 7. Add one number if asked about HWP: at EU level HWP is ~5-20% of the forest-land sink (derived from Rougieux et al. 2024 preprint, Tables 6-7; not peer reviewed), and low residue removal lowers the 2030 sink. See prep note 7.3.

**Do not say:** "conservation maximises the sink" without the BDS-collapse caveat; any Blattert sink value as a 2035 number.

---

## Part B — Where to fix the Drive version, with paste-ready text

Paragraph indices refer to the downloaded V1 copy; search for the quoted text in your Drive version.

### B1. Section 2, caveat 3 ("3. Other Gap : the forest carbon sink is absent...")
Replace the sentence *"Finnish and EU literature treat this asymmetry as first-order (e.g. Blattert's per-scenario sinks: NFS ≈ 80, BES ≈ 28 MtCO₂ yr⁻¹; BDS largest)."* with:

> Finnish and EU literature treat this asymmetry as first-order. In the policy-scenario simulations of Blattert et al. (2022), the national forest carbon sink at the end of the 100-year horizon reaches up to ~80 MtCO₂ yr⁻¹ under the National Forest Strategy (NFS) and ~28 MtCO₂ yr⁻¹ under the Bioeconomy Strategy (BES). The Biodiversity Strategy (BDS) yields the highest sink initially, but the sink collapses in the second half of the simulation and becomes negative, coinciding with its harvest peak. The climate ranking of management regimes is therefore time-dependent rather than a simple monotonic function of harvest intensity, which an energy-only constraint cannot represent. These values are end-of-horizon simulation outputs under Blattert's setup, not 2035 estimates.

*Justification:* matches Blattert Fig. 8d text; removes the unsupported "BDS largest"; adds the temporal caveat. *Note:* "MtCO₂ yr⁻¹" is as reported by Blattert; unit scope (national, per year) should be confirmed in their Fig. 8d before quoting externally.

### B2. Section 4 ("Finnish forest policy and ecological ceilings"), last sentence
Current: *"These anchor the S1/S2/S3 narratives and provide independent per-scenario sink estimates."* Replace with:

> These anchor the S1/S2/S3 narratives; Blattert et al. additionally provide simulated per-scenario forest carbon sink trajectories, whereas Mönkkönen et al. address ecological harvest limits only and report no sink estimates.

### B3. Section 6, step 2 (placeholder for the AMPL prototype)
Current: *"...using literature sink values (Blattert) as a placeholder..."* Append:

> Because Blattert's sink values are end-of-horizon (not 2035) and BDS is non-monotonic, the placeholder should be framed as an illustrative sensitivity (e.g. a range of S_forest values per scenario), not as a calibrated sink.

### B4. Other fixes already identified (same file)
- Numbering: Section 6 is followed by "8. Open questions" (no Section 7); the question table (Q1–Q7) sits below an empty heading.
- References: add Kärhä et al. 2018 (cited in text, present), di Fulvio et al. (2016/2025), Natarajan et al. 2014 / Leduc et al. for BeWhere, Booth & Giuntoli 2025 if used.
- Title/Section 4: soften "PICUS" (D3.4 uses PICUS-*derived* algorithms; for Northern Europe the growth model is PREBAS).
- Section 5.A: "BES ≈ NFS in total harvest" — I did not re-verify this against Blattert; the paper states BES could reach only ~75% of maximum possible harvest when meeting biodiversity constraints. Check before presenting.

