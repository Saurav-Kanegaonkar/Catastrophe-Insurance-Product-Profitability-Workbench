-- Portfolio SQL checks for a catastrophe homeowners product review.

-- 1. Product segments where growth should pause until rate or guideline work is complete.
select
  segment_id, county, product_program, market_lane,
  expected_combined_ratio, rate_adequacy, capacity_used, recommended_action
from product_segments
where expected_combined_ratio > 1.06
   or rate_adequacy < 0.98
order by expected_combined_ratio desc;

-- 2. County and lane profitability for leadership profit and growth review.
select
  county, market_lane,
  sum(annual_premium) as annual_premium,
  sum(annual_premium * expected_combined_ratio) / nullif(sum(annual_premium), 0) as weighted_combined_ratio,
  avg(agent_readiness) as avg_agent_readiness
from product_segments
group by county, market_lane
order by weighted_combined_ratio desc;

-- 3. Scenario recommendations with implementation risk.
select
  scenario, lever, affected_segments, incremental_premium,
  combined_ratio_delta, margin_delta, implementation_risk, recommendation
from guideline_scenario_summary
order by margin_delta desc;

-- 4. Workstreams blocking a launch decision.
select
  workstream_id, workstream, work_type, owner, linked_scenario, blocker, due_in_days
from implementation_readiness_queue
where status = 'Blocked' or readiness_score < 0.64
order by due_in_days asc;
