# Methodology

## Synthetic Data Design

The data is synthetic and intentionally labeled. It is modeled on the structure of catastrophe-exposed homeowners product management: county-level wildfire tiers, homeowners product forms, admitted and E&S lanes, occupancy types, mitigation credits, expected loss ratios, reinsurance load, expense load, capacity guardrails, and agent rollout readiness.

## Profitability Logic

Expected combined ratio equals expected loss ratio plus reinsurance load, expense ratio, and commission ratio. Profit margin is one minus expected combined ratio. Technical premium is generated separately so rate adequacy can be evaluated as technical premium divided by actual annual premium.

## Priority Logic

The priority score rewards premium scale, profit, capacity headroom, agent readiness, and mitigation quality. It penalizes weak combined ratio and inadequate rate. The decision lane translates the score into Advance, Watch, or Fix first.

## Scenario Logic

Each guideline scenario applies explainable deltas to affected segments. The model compares baseline and proposed premium, expected losses, operating cost, reinsurance load, commission, combined ratio, and margin movement.
