# Data Dictionary

| File | Grain | Description |
| --- | --- | --- |
| `data/product_segments.csv` | County, product program, occupancy type | Synthetic homeowners product profitability segments with premium, loss, capacity, readiness, rate adequacy, and recommended action. |
| `data/guideline_scenarios.csv` | Scenario | Product or underwriting guideline changes with affected segment count, premium movement, combined-ratio movement, margin movement, and implementation risk. |
| `data/implementation_plan.csv` | Workstream | Product, underwriting, pricing, compliance, distribution, operations, and analytics tasks needed to launch or monitor changes. |
| `data/product_language_reviews.csv` | Review item | Product language, policy form, underwriting guideline, and agent practice items requiring review. |
| `analysis/outputs/segment_profitability_queue.csv` | County, product program, occupancy type | Ranked queue used by the Product Profit Cockpit. |
| `analysis/outputs/guideline_scenario_summary.csv` | Scenario | Scenario outputs used by the Guideline Lab. |
| `analysis/outputs/implementation_readiness_queue.csv` | Workstream | Launch readiness queue used by the Implementation surface. |
| `analysis/outputs/product_language_review.csv` | Review item | Language review list used by the Implementation surface. |
| `analysis/outputs/summary.json` | Artifact summary | Top-line metrics loaded by the static app. |

## Key Fields

| Field | Meaning |
| --- | --- |
| `annual_premium` | Synthetic annual premium for the segment. |
| `technical_premium` | Modeled technical premium needed for rate adequacy comparison. |
| `expected_combined_ratio` | Expected loss ratio plus reinsurance load, expense ratio, and commission ratio. |
| `profit_margin` | One minus expected combined ratio. |
| `capacity_used` | Annual premium divided by segment capacity limit. |
| `agent_readiness` | Synthetic readiness score for distribution and agent execution. |
| `priority_score` | Explainable product review score for ordering the queue. |
| `decision_lane` | Advance, Watch, or Fix first. |
| `combined_ratio_delta` | Proposed scenario combined ratio minus baseline combined ratio. |
| `margin_delta` | Proposed scenario margin dollars minus baseline margin dollars. |
