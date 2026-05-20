import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"

random.seed(42)

COUNTIES = [
    {"county": "Butte", "region": "Sierra foothills", "tier": "Severe", "base_lr": 0.43, "growth": 0.16},
    {"county": "El Dorado", "region": "Sierra foothills", "tier": "High", "base_lr": 0.36, "growth": 0.15},
    {"county": "Lake", "region": "North Coast range", "tier": "Severe", "base_lr": 0.45, "growth": 0.13},
    {"county": "Los Angeles", "region": "Coastal metro edge", "tier": "Moderate", "base_lr": 0.30, "growth": 0.19},
    {"county": "Marin", "region": "Bay Area wildland edge", "tier": "High", "base_lr": 0.35, "growth": 0.11},
    {"county": "Mendocino", "region": "North Coast range", "tier": "High", "base_lr": 0.38, "growth": 0.10},
    {"county": "Napa", "region": "Wine country", "tier": "High", "base_lr": 0.39, "growth": 0.12},
    {"county": "Nevada", "region": "Sierra foothills", "tier": "Severe", "base_lr": 0.44, "growth": 0.09},
    {"county": "Placer", "region": "Sierra foothills", "tier": "High", "base_lr": 0.35, "growth": 0.14},
    {"county": "Riverside", "region": "Inland wildland edge", "tier": "Moderate", "base_lr": 0.29, "growth": 0.21},
    {"county": "San Bernardino", "region": "Mountain metro edge", "tier": "High", "base_lr": 0.34, "growth": 0.18},
    {"county": "San Diego", "region": "Southern coastal canyon", "tier": "Moderate", "base_lr": 0.28, "growth": 0.20},
    {"county": "Santa Barbara", "region": "Central coast canyon", "tier": "High", "base_lr": 0.33, "growth": 0.12},
    {"county": "Shasta", "region": "Northern interior", "tier": "Severe", "base_lr": 0.46, "growth": 0.09},
    {"county": "Sonoma", "region": "Wine country", "tier": "High", "base_lr": 0.37, "growth": 0.13},
    {"county": "Ventura", "region": "Southern coastal canyon", "tier": "Moderate", "base_lr": 0.29, "growth": 0.18},
]

PRODUCTS = [
    {"product": "Admitted HO-3 renewal", "lane": "Admitted", "occupancy": "Primary", "premium_factor": 0.0062, "expense": 0.245},
    {"product": "E&S wildfire endorsement", "lane": "E&S", "occupancy": "Primary", "premium_factor": 0.0085, "expense": 0.275},
    {"product": "Secondary home package", "lane": "E&S", "occupancy": "Secondary", "premium_factor": 0.0091, "expense": 0.285},
    {"product": "Vacant home restricted form", "lane": "E&S", "occupancy": "Vacant", "premium_factor": 0.0108, "expense": 0.305},
]

GUIDELINE_SCENARIOS = [
    {
        "scenario": "Mitigation credit expansion",
        "lever": "Product enhancement",
        "description": "Increase credits for defensible space, Class A roof, ember-resistant vents, and monitored water supply.",
        "premium_delta": -0.025,
        "loss_delta": -0.080,
        "growth_delta": 0.055,
        "capacity_delta": 0.015,
        "implementation_risk": 0.22,
    },
    {
        "scenario": "Ember-zone eligibility tightening",
        "lever": "Underwriting guideline",
        "description": "Require updated inspection evidence for severe-tier homes with close fuel proximity.",
        "premium_delta": 0.018,
        "loss_delta": -0.115,
        "growth_delta": -0.040,
        "capacity_delta": -0.018,
        "implementation_risk": 0.34,
    },
    {
        "scenario": "Vacant-home deductible reset",
        "lever": "Policy language",
        "description": "Move vacant homes to higher wildfire deductible and clearer loss-condition wording.",
        "premium_delta": 0.032,
        "loss_delta": -0.060,
        "growth_delta": -0.018,
        "capacity_delta": -0.006,
        "implementation_risk": 0.29,
    },
    {
        "scenario": "Seasonal-home growth lane",
        "lever": "Growth plan",
        "description": "Open seasonal-home eligibility in moderate and selected high-tier counties with inspection guardrails.",
        "premium_delta": -0.010,
        "loss_delta": 0.025,
        "growth_delta": 0.095,
        "capacity_delta": 0.030,
        "implementation_risk": 0.31,
    },
]

IMPLEMENTATION_WORK = [
    ("Pricing adequacy memo", "Pricing", "Quantify rate need and expected loss ratio movement by county and occupancy.", "Analytics"),
    ("Eligibility guideline redline", "Underwriting guideline", "Document tier-specific eligibility rules, inspection requirements, and referral triggers.", "Product"),
    ("Policy form wording review", "Policy language", "Review wildfire deductible language, vacancy conditions, and mitigation credit endorsements.", "Product"),
    ("Agent enablement brief", "Agent practice", "Prepare appetite guide, objection handling, and bind authority notes for appointed agents.", "Distribution"),
    ("Filing and compliance checklist", "Implementation", "Track admitted filing artifacts and E&S disclosure requirements by lane.", "Compliance"),
    ("Post-launch monitoring pack", "Monitoring", "Define weekly metrics for quote flow, bind rate, loss signals, and referral quality.", "Analytics"),
    ("Inspection vendor control", "Operational process", "Confirm inspection SLA, photo evidence completeness, and exception handling.", "Operations"),
    ("Capacity steering review", "Profit and growth", "Compare written premium against county and peril capacity guardrails.", "Leadership"),
]


def money(value):
    return round(value, 2)


def pct(value):
    return round(value, 4)


def weighted_choice(options):
    total = sum(weight for _, weight in options)
    marker = random.random() * total
    running = 0
    for value, weight in options:
        running += weight
        if running >= marker:
            return value
    return options[-1][0]


def build_segments():
    rows = []
    segment_id = 1
    for county in COUNTIES:
        for product in PRODUCTS:
            if county["tier"] == "Severe" and product["lane"] == "Admitted":
                volume_factor = 0.72
            elif product["occupancy"] == "Vacant":
                volume_factor = 0.28
            elif product["occupancy"] == "Secondary":
                volume_factor = 0.46
            else:
                volume_factor = 1.0

            policy_count = int(random.randint(90, 430) * volume_factor * (1 + county["growth"]))
            tiv = policy_count * random.randint(585000, 980000)
            mitigation_credit = max(0.02, min(0.18, random.gauss(0.08, 0.035)))
            wildfire_adj = {"Moderate": 0.92, "High": 1.0, "Severe": 1.12}[county["tier"]]
            occupancy_adj = {"Primary": 1.0, "Secondary": 1.10, "Vacant": 1.26}[product["occupancy"]]
            premium = tiv * product["premium_factor"] * wildfire_adj * occupancy_adj * (1 - mitigation_credit * 0.34)
            technical_premium = premium * random.uniform(0.97, 1.14)

            attritional_lr = max(0.17, random.gauss(0.255, 0.035) + (0.025 if product["occupancy"] == "Vacant" else 0))
            cat_lr = county["base_lr"] * random.uniform(0.72, 1.10) * occupancy_adj * (1 - mitigation_credit * 0.55)
            expected_lr = attritional_lr + cat_lr
            reinsurance_load = {"Moderate": 0.085, "High": 0.120, "Severe": 0.160}[county["tier"]] + random.uniform(-0.01, 0.018)
            expense_ratio = product["expense"] + random.uniform(-0.012, 0.018)
            commission_ratio = 0.130 if product["lane"] == "E&S" else 0.115
            combined_ratio = expected_lr + reinsurance_load + expense_ratio + commission_ratio
            profit_margin = 1 - combined_ratio

            capacity_limit = premium * random.uniform(1.06, 1.58)
            capacity_used = min(0.98, premium / capacity_limit)
            agent_count = random.randint(6, 28) if product["lane"] == "E&S" else random.randint(10, 36)
            agent_readiness = max(0.45, min(0.97, random.gauss(0.76, 0.10) - (0.06 if product["occupancy"] == "Vacant" else 0)))
            rate_adequacy = technical_premium / premium
            retention = max(0.55, min(0.93, random.gauss(0.78, 0.07) - (0.04 if combined_ratio > 1.12 else 0)))
            quote_index = max(68, min(155, random.gauss(100 * (1 + county["growth"]), 16)))

            if combined_ratio <= 0.98 and capacity_used < 0.78 and agent_readiness >= 0.73:
                action = "Expand controlled growth"
            elif combined_ratio <= 1.06 and rate_adequacy >= 0.98:
                action = "Monitor with weekly guardrails"
            elif rate_adequacy < 0.98:
                action = "File rate or tighten eligibility"
            elif product["occupancy"] == "Vacant":
                action = "Reset deductible and wording"
            else:
                action = "Tighten underwriting guideline"

            rows.append(
                {
                    "segment_id": f"CAT-{segment_id:03d}",
                    "county": county["county"],
                    "region": county["region"],
                    "product_program": product["product"],
                    "market_lane": product["lane"],
                    "occupancy_type": product["occupancy"],
                    "wildfire_tier": county["tier"],
                    "policy_count": policy_count,
                    "total_insured_value": money(tiv),
                    "annual_premium": money(premium),
                    "technical_premium": money(technical_premium),
                    "attritional_loss_ratio": pct(attritional_lr),
                    "cat_loss_ratio": pct(cat_lr),
                    "expected_loss_ratio": pct(expected_lr),
                    "reinsurance_load": pct(reinsurance_load),
                    "expense_ratio": pct(expense_ratio),
                    "commission_ratio": pct(commission_ratio),
                    "expected_combined_ratio": pct(combined_ratio),
                    "profit_margin": pct(profit_margin),
                    "capacity_limit": money(capacity_limit),
                    "capacity_used": pct(capacity_used),
                    "mitigation_credit": pct(mitigation_credit),
                    "agent_count": agent_count,
                    "agent_readiness": pct(agent_readiness),
                    "rate_adequacy": pct(rate_adequacy),
                    "renewal_retention": pct(retention),
                    "new_business_index": round(quote_index, 1),
                    "filing_status": weighted_choice(
                        [
                            ("No filing required", 0.40),
                            ("Filing memo drafted", 0.22),
                            ("Actuarial support needed", 0.20),
                            ("Compliance review", 0.18),
                        ]
                    ),
                    "guideline_state": weighted_choice(
                        [
                            ("Ready for launch", 0.28),
                            ("Needs wording review", 0.24),
                            ("Needs underwriting signoff", 0.24),
                            ("Needs agent practice update", 0.24),
                        ]
                    ),
                    "recommended_action": action,
                    "owner": weighted_choice(
                        [
                            ("Product", 0.34),
                            ("Underwriting", 0.28),
                            ("Pricing", 0.18),
                            ("Distribution", 0.12),
                            ("Operations", 0.08),
                        ]
                    ),
                }
            )
            segment_id += 1
    return rows


def score_segments(rows):
    scored = []
    for row in rows:
        premium = float(row["annual_premium"])
        margin = float(row["profit_margin"])
        combined = float(row["expected_combined_ratio"])
        capacity_used = float(row["capacity_used"])
        agent_readiness = float(row["agent_readiness"])
        rate_adequacy = float(row["rate_adequacy"])
        growth = float(row["new_business_index"]) / 100
        mitigation = float(row["mitigation_credit"])
        growth_score = min(38, math.log1p(premium) * 1.65 + growth * 8)
        profit_score = max(0, min(34, (1.12 - combined) * 130 + margin * 18))
        execution_score = min(24, agent_readiness * 14 + (1 - capacity_used) * 8 + mitigation * 14)
        risk_penalty = max(0, (combined - 1.04) * 36) + max(0, (0.99 - rate_adequacy) * 24)
        priority = max(0, min(100, growth_score + profit_score + execution_score - risk_penalty))
        if priority >= 62 and combined < 1.04:
            decision = "Advance"
        elif priority >= 48:
            decision = "Watch"
        else:
            decision = "Fix first"

        scored.append({**row, "priority_score": round(priority, 1), "decision_lane": decision})
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    return scored


def build_scenarios(scored_rows):
    scenario_rows = []
    for scenario in GUIDELINE_SCENARIOS:
        affected = []
        for row in scored_rows:
            product = row["product_program"]
            tier = row["wildfire_tier"]
            occupancy = row["occupancy_type"]
            include = False
            if scenario["scenario"] == "Mitigation credit expansion":
                include = tier in {"High", "Severe"} and float(row["mitigation_credit"]) < 0.11
            elif scenario["scenario"] == "Ember-zone eligibility tightening":
                include = tier == "Severe"
            elif scenario["scenario"] == "Vacant-home deductible reset":
                include = occupancy == "Vacant"
            elif scenario["scenario"] == "Seasonal-home growth lane":
                include = occupancy == "Secondary" and tier in {"Moderate", "High"}
            if include:
                affected.append(row)

        baseline_premium = sum(float(row["annual_premium"]) for row in affected)
        baseline_loss = sum(float(row["annual_premium"]) * float(row["expected_loss_ratio"]) for row in affected)
        baseline_combined_cost = sum(
            float(row["annual_premium"])
            * (
                float(row["expected_loss_ratio"])
                + float(row["expense_ratio"])
                + float(row["commission_ratio"])
                + float(row["reinsurance_load"])
            )
            for row in affected
        )
        proposed_premium = baseline_premium * (1 + scenario["premium_delta"] + scenario["growth_delta"])
        proposed_loss = baseline_loss * (1 + scenario["loss_delta"] + scenario["growth_delta"])
        proposed_expense = baseline_premium * (0.31 + scenario["implementation_risk"] * 0.035) * (1 + scenario["growth_delta"])
        proposed_reinsurance = baseline_premium * (0.145 + scenario["capacity_delta"]) * (1 + scenario["growth_delta"])
        proposed_commission = proposed_premium * 0.14
        proposed_combined_cost = proposed_loss + proposed_expense + proposed_reinsurance + proposed_commission
        baseline_cr = baseline_combined_cost / baseline_premium if baseline_premium else 0
        proposed_cr = proposed_combined_cost / proposed_premium if proposed_premium else 0
        incremental_premium = proposed_premium - baseline_premium
        margin_delta = (proposed_premium - proposed_combined_cost) - (baseline_premium - baseline_combined_cost)

        if proposed_cr < baseline_cr and margin_delta > 0:
            recommendation = "Recommend pilot"
        elif margin_delta > 0:
            recommendation = "Pilot with guardrails"
        else:
            recommendation = "Revise before launch"

        scenario_rows.append(
            {
                "scenario": scenario["scenario"],
                "lever": scenario["lever"],
                "description": scenario["description"],
                "affected_segments": len(affected),
                "baseline_premium": money(baseline_premium),
                "incremental_premium": money(incremental_premium),
                "baseline_combined_ratio": pct(baseline_cr),
                "proposed_combined_ratio": pct(proposed_cr),
                "combined_ratio_delta": pct(proposed_cr - baseline_cr),
                "margin_delta": money(margin_delta),
                "implementation_risk": pct(scenario["implementation_risk"]),
                "recommendation": recommendation,
            }
        )
    return scenario_rows


def build_implementation_plan(scored_rows, scenario_rows):
    rows = []
    for idx, work in enumerate(IMPLEMENTATION_WORK, start=1):
        scenario = scenario_rows[(idx - 1) % len(scenario_rows)]
        priority = "High" if scenario["recommendation"] != "Revise before launch" and idx in {1, 2, 3, 6} else "Medium"
        readiness = max(0.42, min(0.98, random.gauss(0.72, 0.12)))
        if "Compliance" in work[3] or "Policy language" in work[1]:
            readiness -= 0.08
        status = "Ready" if readiness >= 0.82 else "In review" if readiness >= 0.64 else "Blocked"
        rows.append(
            {
                "workstream_id": f"IMP-{idx:02d}",
                "workstream": work[0],
                "work_type": work[1],
                "description": work[2],
                "owner": work[3],
                "linked_scenario": scenario["scenario"],
                "priority": priority,
                "readiness_score": pct(readiness),
                "status": status,
                "blocker": "None"
                if status == "Ready"
                else weighted_choice(
                    [
                        ("Needs actuarial exhibit", 0.28),
                        ("Needs product wording decision", 0.26),
                        ("Needs underwriting approval", 0.24),
                        ("Needs agent communication", 0.22),
                    ]
                ),
                "due_in_days": random.randint(7, 35),
            }
        )
    return rows


def build_language_reviews():
    reviews = [
        ("Wildfire deductible endorsement", "Policy form", "Clarify event trigger and multiple-location application.", "Legal review"),
        ("Mitigation credit schedule", "Product language", "Tie credits to evidence requirements and inspection recency.", "Product approved"),
        ("Vacancy condition wording", "Policy form", "Define vacancy threshold and required owner attestation.", "Needs underwriting signoff"),
        ("Binding authority addendum", "Agent practice", "Document broker authority by county tier and occupancy type.", "Distribution review"),
        ("Inspection evidence checklist", "Underwriting guideline", "Require roof, defensible space, venting, and access photos.", "Ready"),
        ("Nonrenewal referral trigger", "Operational process", "Route severe-tier renewal exceptions to underwriting review.", "Analytics review"),
    ]
    return [
        {
            "review_id": f"LANG-{idx:02d}",
            "item": item,
            "category": category,
            "decision_needed": decision,
            "status": status,
            "risk_level": weighted_choice([("High", 0.28), ("Medium", 0.50), ("Low", 0.22)]),
        }
        for idx, (item, category, decision, status) in enumerate(reviews, start=1)
    ]


def write_csv(path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_docs(scored, scenarios, implementation, language):
    top = scored[0]
    advance = [row for row in scored if row["decision_lane"] == "Advance"]
    fix = [row for row in scored if row["decision_lane"] == "Fix first"]
    total_premium = sum(float(row["annual_premium"]) for row in scored)
    avg_cr = sum(float(row["expected_combined_ratio"]) * float(row["annual_premium"]) for row in scored) / total_premium
    weighted_margin = 1 - avg_cr
    best_scenario = max(scenarios, key=lambda row: float(row["margin_delta"]))
    blocked = [row for row in implementation if row["status"] == "Blocked"]

    summary = {
        "portfolio": {
            "segment_count": len(scored),
            "total_premium": money(total_premium),
            "weighted_combined_ratio": pct(avg_cr),
            "weighted_margin": pct(weighted_margin),
            "advance_segments": len(advance),
            "fix_first_segments": len(fix),
            "top_segment": top["segment_id"],
            "top_county": top["county"],
            "top_action": top["recommended_action"],
        },
        "scenario": {
            "recommended_scenarios": len([row for row in scenarios if row["recommendation"] == "Recommend pilot"]),
            "best_scenario": best_scenario["scenario"],
            "best_margin_delta": best_scenario["margin_delta"],
            "best_combined_ratio_delta": best_scenario["combined_ratio_delta"],
        },
        "implementation": {
            "workstreams": len(implementation),
            "blocked_workstreams": len(blocked),
            "ready_workstreams": len([row for row in implementation if row["status"] == "Ready"]),
            "language_items": len(language),
        },
    }
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    (ROOT / "analysis" / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I Analyzed",
                "",
                f"I modeled {len(scored)} catastrophe-exposed homeowners product segments across county, product form, occupancy type, market lane, expected loss, reinsurance load, expenses, capacity use, and agent readiness.",
                "",
                "## Findings",
                "",
                f"- The portfolio carries ${total_premium:,.0f} of modeled annual premium with a weighted expected combined ratio of {avg_cr:.1%}.",
                f"- {len(advance)} segments are in the Advance lane because profit, capacity, and agent readiness support controlled growth.",
                f"- {len(fix)} segments are in the Fix first lane because rate adequacy, capacity use, or implementation readiness needs action before growth.",
                f"- The top-ranked opportunity is {top['segment_id']} in {top['county']} for {top['product_program']}, with a priority score of {top['priority_score']}.",
                f"- The strongest modeled product change is {best_scenario['scenario']}, with ${float(best_scenario['margin_delta']):,.0f} of modeled margin movement and a {float(best_scenario['combined_ratio_delta']):.1%} combined-ratio change.",
                "",
                "## Recommendation",
                "",
                "Use the workbench as a weekly product review artifact. Advance profitable growth lanes, route weak segments to rate or guideline work, and keep product-language and agent-practice implementation tied to the same profitability view leadership uses.",
                "",
            ]
        )
    )

    (ROOT / "analysis" / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "## Business Question",
                "",
                "Which catastrophe-exposed homeowners product segments should be expanded, monitored, or fixed before growth, and which guideline or product-language changes should move first?",
                "",
                "## Method",
                "",
                "1. Build a segment-level profitability file by county, product program, occupancy type, market lane, wildfire tier, premium, technical premium, loss ratios, reinsurance load, expense load, capacity, and agent readiness.",
                "2. Score each segment using premium scale, expected combined ratio, rate adequacy, capacity headroom, mitigation credit, and agent readiness.",
                "3. Model guideline scenarios as explainable deltas to premium, loss, growth, capacity, and implementation risk.",
                "4. Convert the top scenarios into product, underwriting, compliance, analytics, and distribution workstreams.",
                "5. Review outputs with leadership as a profit and growth operating artifact rather than a passive dashboard.",
                "",
            ]
        )
    )

    (ROOT / "analysis" / "methodology.md").write_text(
        "\n".join(
            [
                "# Methodology",
                "",
                "## Synthetic Data Design",
                "",
                "The data is synthetic and intentionally labeled. It is modeled on the structure of catastrophe-exposed homeowners product management: county-level wildfire tiers, homeowners product forms, admitted and E&S lanes, occupancy types, mitigation credits, expected loss ratios, reinsurance load, expense load, capacity guardrails, and agent rollout readiness.",
                "",
                "## Profitability Logic",
                "",
                "Expected combined ratio equals expected loss ratio plus reinsurance load, expense ratio, and commission ratio. Profit margin is one minus expected combined ratio. Technical premium is generated separately so rate adequacy can be evaluated as technical premium divided by actual annual premium.",
                "",
                "## Priority Logic",
                "",
                "The priority score rewards premium scale, profit, capacity headroom, agent readiness, and mitigation quality. It penalizes weak combined ratio and inadequate rate. The decision lane translates the score into Advance, Watch, or Fix first.",
                "",
                "## Scenario Logic",
                "",
                "Each guideline scenario applies explainable deltas to affected segments. The model compares baseline and proposed premium, expected losses, operating cost, reinsurance load, commission, combined ratio, and margin movement.",
                "",
            ]
        )
    )


def write_sql_checks():
    (ROOT / "analysis" / "sql_checks.sql").write_text(
        "\n".join(
            [
                "-- Portfolio SQL checks for a catastrophe homeowners product review.",
                "",
                "-- 1. Product segments where growth should pause until rate or guideline work is complete.",
                "select",
                "  segment_id, county, product_program, market_lane,",
                "  expected_combined_ratio, rate_adequacy, capacity_used, recommended_action",
                "from product_segments",
                "where expected_combined_ratio > 1.06",
                "   or rate_adequacy < 0.98",
                "order by expected_combined_ratio desc;",
                "",
                "-- 2. County and lane profitability for leadership profit and growth review.",
                "select",
                "  county, market_lane,",
                "  sum(annual_premium) as annual_premium,",
                "  sum(annual_premium * expected_combined_ratio) / nullif(sum(annual_premium), 0) as weighted_combined_ratio,",
                "  avg(agent_readiness) as avg_agent_readiness",
                "from product_segments",
                "group by county, market_lane",
                "order by weighted_combined_ratio desc;",
                "",
                "-- 3. Scenario recommendations with implementation risk.",
                "select",
                "  scenario, lever, affected_segments, incremental_premium,",
                "  combined_ratio_delta, margin_delta, implementation_risk, recommendation",
                "from guideline_scenario_summary",
                "order by margin_delta desc;",
                "",
                "-- 4. Workstreams blocking a launch decision.",
                "select",
                "  workstream_id, workstream, work_type, owner, linked_scenario, blocker, due_in_days",
                "from implementation_readiness_queue",
                "where status = 'Blocked' or readiness_score < 0.64",
                "order by due_in_days asc;",
                "",
            ]
        )
    )


def main():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    segments = build_segments()
    scored = score_segments(segments)
    scenarios = build_scenarios(scored)
    implementation = build_implementation_plan(scored, scenarios)
    language = build_language_reviews()

    write_csv(DATA / "product_segments.csv", scored)
    write_csv(DATA / "guideline_scenarios.csv", scenarios)
    write_csv(DATA / "implementation_plan.csv", implementation)
    write_csv(DATA / "product_language_reviews.csv", language)
    write_csv(OUTPUTS / "segment_profitability_queue.csv", scored)
    write_csv(OUTPUTS / "guideline_scenario_summary.csv", scenarios)
    write_csv(OUTPUTS / "implementation_readiness_queue.csv", implementation)
    write_csv(OUTPUTS / "product_language_review.csv", language)
    write_docs(scored, scenarios, implementation, language)
    write_sql_checks()

    top = scored[0]
    print(f"Generated {len(scored)} product segments.")
    print(f"Top segment: {top['segment_id']} {top['county']} {top['product_program']} score={top['priority_score']}")
    print(f"Best scenario: {max(scenarios, key=lambda row: float(row['margin_delta']))['scenario']}")


if __name__ == "__main__":
    main()
