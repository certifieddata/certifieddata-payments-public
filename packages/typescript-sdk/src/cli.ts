#!/usr/bin/env node
/**
 * cdac — CertifiedData Agent Commerce command-line helper (TypeScript).
 *
 * Usage:
 *   cdac demo [basic|certified|denied|idempotency]
 *   cdac verify <receipt_id>
 *   cdac capabilities
 *   cdac health
 */

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_BASE_URL = "https://certifieddata.io";
const DEMO_KEY = "cdp_test_demo_certifieddata_io_2026";

function baseUrl(): string {
  return (process.env["CDAC_BASE_URL"] ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
}

function ensureKey(): void {
  if (!process.env["CDAC_API_KEY"]) process.env["CDAC_API_KEY"] = DEMO_KEY;
}

function repoRoot(): string {
  const here = dirname(fileURLToPath(import.meta.url));
  return resolve(here, "..", "..", "..", "..");
}

function runDemo(name: string): number {
  const mapping: Record<string, string> = {
    basic:       "examples/claude-demo/demo.ts",
    certified:   "examples/claude-demo/demo_certified.ts",
    denied:      "examples/claude-demo/demo_denied.py",      // ts variant not shipped
    idempotency: "examples/claude-demo/demo_idempotency.py", // ts variant not shipped
  };
  const rel = mapping[name];
  if (!rel) {
    console.error(`cdac: unknown demo '${name}'. options: ${Object.keys(mapping).join(", ")}`);
    return 2;
  }
  const script = resolve(repoRoot(), rel);
  if (!existsSync(script)) {
    console.error(`cdac: demo script not found at ${script}.`);
    return 2;
  }
  ensureKey();
  const runner = script.endsWith(".py") ? "python" : "tsx";
  const result = spawnSync(runner, [script], { stdio: "inherit", env: process.env });
  return result.status ?? 1;
}

async function cmdVerify(args: string[]): Promise<number> {
  if (args.length === 0) {
    console.error("Usage: cdac verify <receipt_id>");
    return 2;
  }
  const url = `${baseUrl()}/api/payments/verify/${args[0]}`;
  try {
    const resp = await fetch(url);
    const body = await resp.json() as Record<string, unknown>;
    console.log(JSON.stringify(body, null, 2));
    return body["valid"] ? 0 : 1;
  } catch (e: unknown) {
    console.error(`cdac verify: ${e instanceof Error ? e.message : String(e)}`);
    return 1;
  }
}

async function getJson(path: string): Promise<number> {
  try {
    const resp = await fetch(`${baseUrl()}${path}`);
    console.log(await resp.text());
    return resp.ok ? 0 : 1;
  } catch (e: unknown) {
    console.error(`cdac: ${e instanceof Error ? e.message : String(e)}`);
    return 1;
  }
}

const USAGE = `cdac — CertifiedData Agent Commerce CLI

Commands:
  demo [basic|certified|denied|idempotency]  run a bundled demo (default: basic)
  verify <receipt_id>                        independent public verification
  capabilities                               GET /v1/capabilities
  health                                     GET /v1/health

Environment:
  CDAC_API_KEY    API key (falls back to built-in public demo key)
  CDAC_BASE_URL   Default ${DEFAULT_BASE_URL}
`;

async function main(): Promise<number> {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || ["-h", "--help", "help"].includes(argv[0] as string)) {
    console.log(USAGE);
    return 0;
  }
  const [cmd, ...rest] = argv;
  switch (cmd) {
    case "demo":         return runDemo((rest[0] as string) ?? "basic");
    case "verify":       return cmdVerify(rest);
    case "capabilities": return getJson("/v1/capabilities");
    case "health":       return getJson("/v1/health");
    default:
      console.error(`cdac: unknown command '${cmd}'\n${USAGE}`);
      return 2;
  }
}

main().then((code) => process.exit(code));
