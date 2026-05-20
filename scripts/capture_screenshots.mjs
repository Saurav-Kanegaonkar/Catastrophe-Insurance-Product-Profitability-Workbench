import { mkdir } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const root = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const outDir = path.join(root, "docs", "images");
const url = process.env.PORTFOLIO_ARTIFACT_URL || "http://127.0.0.1:5279";

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });

await page.goto(url, { waitUntil: "networkidle" });
await page.screenshot({ path: path.join(outDir, "profit-cockpit.png"), fullPage: true });

await page.click('[data-view="scenario"]');
await page.waitForSelector("#scenarioView.active");
await page.screenshot({ path: path.join(outDir, "guideline-lab.png"), fullPage: true });

await page.click('[data-view="implementation"]');
await page.waitForSelector("#implementationView.active");
await page.screenshot({ path: path.join(outDir, "implementation-tracker.png"), fullPage: true });

const checks = await page.evaluate(() => ({
  metrics: document.querySelectorAll(".metric-strip article").length,
  scenarios: document.querySelectorAll(".scenario-card").length,
  tasks: document.querySelectorAll(".task-card").length,
  activeSurface: document.querySelector(".view.active")?.id,
}));

await browser.close();

console.log(JSON.stringify(checks, null, 2));
