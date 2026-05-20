const state = {
  segments: [],
  scenarios: [],
  tasks: [],
  language: [],
  summary: null,
  lane: "All",
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });

function pct(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function parseCsv(text) {
  const rows = [];
  const lines = text.trim().split(/\r?\n/);
  const headers = splitCsvLine(lines.shift());
  for (const line of lines) {
    const values = splitCsvLine(line);
    rows.push(Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
  }
  return rows;
}

function splitCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

async function loadData() {
  const [segments, scenarios, tasks, language, summary] = await Promise.all([
    fetch("analysis/outputs/segment_profitability_queue.csv").then((response) => response.text()).then(parseCsv),
    fetch("analysis/outputs/guideline_scenario_summary.csv").then((response) => response.text()).then(parseCsv),
    fetch("analysis/outputs/implementation_readiness_queue.csv").then((response) => response.text()).then(parseCsv),
    fetch("analysis/outputs/product_language_review.csv").then((response) => response.text()).then(parseCsv),
    fetch("analysis/outputs/summary.json").then((response) => response.json()),
  ]);
  state.segments = segments;
  state.scenarios = scenarios;
  state.tasks = tasks;
  state.language = language;
  state.summary = summary;
  renderAll();
}

function renderAll() {
  renderHero();
  renderMetrics();
  renderSegmentRows();
  renderLaneBars();
  renderCountyPressure();
  renderScenarios();
  renderTasks();
  renderLanguage();
}

function renderHero() {
  const top = state.segments[0];
  document.querySelector("#topAction").textContent = `${top.decision_lane}: ${top.recommended_action}`;
  document.querySelector("#topContext").textContent = `${top.segment_id} in ${top.county} has a ${pct(top.expected_combined_ratio)} expected combined ratio and ${pct(top.capacity_used)} capacity use.`;
}

function renderMetrics() {
  const portfolio = state.summary.portfolio;
  const scenario = state.summary.scenario;
  const implementation = state.summary.implementation;
  const metrics = [
    ["Modeled premium", money.format(portfolio.total_premium), `${portfolio.segment_count} product segments`],
    ["Weighted combined ratio", pct(portfolio.weighted_combined_ratio), `${portfolio.advance_segments} advance lanes`],
    ["Best scenario", money.format(scenario.best_margin_delta), scenario.best_scenario],
    ["Launch readiness", `${implementation.ready_workstreams}/${implementation.workstreams}`, `${implementation.blocked_workstreams} blocked workstreams`],
  ];
  document.querySelector("#metricStrip").innerHTML = metrics
    .map(
      ([label, value, note]) => `
        <article>
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${note}</em>
        </article>
      `,
    )
    .join("");
}

function renderSegmentRows() {
  const rows = state.segments
    .filter((segment) => state.lane === "All" || segment.decision_lane === state.lane)
    .slice(0, 12);
  document.querySelector("#segmentRows").innerHTML = rows
    .map(
      (segment) => `
        <tr>
          <td><strong>${segment.segment_id}</strong></td>
          <td>${segment.county}</td>
          <td>${segment.product_program}</td>
          <td>${number.format(segment.priority_score)}</td>
          <td>${pct(segment.expected_combined_ratio)}</td>
          <td><span class="pill ${laneClass(segment.decision_lane)}">${segment.decision_lane}</span></td>
          <td>${segment.recommended_action}</td>
        </tr>
      `,
    )
    .join("");
}

function renderLaneBars() {
  const counts = countBy(state.segments, "decision_lane");
  const total = state.segments.length;
  const order = ["Advance", "Watch", "Fix first"];
  document.querySelector("#laneBars").innerHTML = order
    .map((lane) => {
      const count = counts[lane] || 0;
      const width = Math.max(6, (count / total) * 100);
      return `
        <div class="bar-row">
          <div>
            <strong>${lane}</strong>
            <span>${count} segments</span>
          </div>
          <div class="bar-track"><span class="${laneClass(lane)}" style="width:${width}%"></span></div>
        </div>
      `;
    })
    .join("");
}

function renderCountyPressure() {
  const countyMap = new Map();
  for (const segment of state.segments) {
    const current = countyMap.get(segment.county) || { premium: 0, weightedCr: 0, count: 0 };
    const premium = Number(segment.annual_premium);
    current.premium += premium;
    current.weightedCr += premium * Number(segment.expected_combined_ratio);
    current.count += 1;
    countyMap.set(segment.county, current);
  }
  const counties = [...countyMap.entries()]
    .map(([county, value]) => ({ county, premium: value.premium, cr: value.weightedCr / value.premium, count: value.count }))
    .sort((a, b) => b.cr - a.cr)
    .slice(0, 7);
  document.querySelector("#countyList").innerHTML = counties
    .map(
      (item) => `
        <div class="county-item">
          <div>
            <strong>${item.county}</strong>
            <span>${money.format(item.premium)} modeled premium</span>
          </div>
          <b>${pct(item.cr)}</b>
        </div>
      `,
    )
    .join("");
}

function renderScenarios() {
  document.querySelector("#scenarioCards").innerHTML = state.scenarios
    .map(
      (scenario) => `
        <article class="scenario-card">
          <div>
            <span class="pill neutral">${scenario.lever}</span>
            <h3>${scenario.scenario}</h3>
            <p>${scenario.description}</p>
          </div>
          <dl>
            <div><dt>Affected segments</dt><dd>${scenario.affected_segments}</dd></div>
            <div><dt>Incremental premium</dt><dd>${money.format(scenario.incremental_premium)}</dd></div>
            <div><dt>Combined ratio move</dt><dd>${pct(scenario.combined_ratio_delta)}</dd></div>
            <div><dt>Margin move</dt><dd>${money.format(scenario.margin_delta)}</dd></div>
          </dl>
          <footer>
            <strong>${scenario.recommendation}</strong>
            <span>Implementation risk ${pct(scenario.implementation_risk)}</span>
          </footer>
        </article>
      `,
    )
    .join("");
}

function renderTasks() {
  document.querySelector("#taskList").innerHTML = state.tasks
    .map(
      (task) => `
        <article class="task-card">
          <div>
            <span class="pill ${statusClass(task.status)}">${task.status}</span>
            <h3>${task.workstream}</h3>
            <p>${task.description}</p>
          </div>
          <div class="task-meta">
            <span>${task.owner}</span>
            <span>${task.work_type}</span>
            <span>${task.due_in_days} days</span>
            <span>${task.blocker}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderLanguage() {
  document.querySelector("#languageList").innerHTML = state.language
    .map(
      (item) => `
        <article class="language-card">
          <span class="risk">${item.risk_level}</span>
          <h3>${item.item}</h3>
          <p>${item.decision_needed}</p>
          <small>${item.category} / ${item.status}</small>
        </article>
      `,
    )
    .join("");
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    acc[row[key]] = (acc[row[key]] || 0) + 1;
    return acc;
  }, {});
}

function laneClass(lane) {
  if (lane === "Advance") return "good";
  if (lane === "Watch") return "watch";
  return "fix";
}

function statusClass(status) {
  if (status === "Ready") return "good";
  if (status === "In review") return "watch";
  return "fix";
}

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-view]").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#${button.dataset.view}View`).classList.add("active");
  });
});

document.querySelector("#laneFilter").addEventListener("change", (event) => {
  state.lane = event.target.value;
  renderSegmentRows();
});

loadData();
