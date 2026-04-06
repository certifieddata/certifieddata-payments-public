import { createApp } from "./server.js";

const PORT = Number(process.env.PORT ?? 3456);

const app = createApp();

app.listen(PORT, () => {
  console.log(`CertifiedData Payments mock server running on http://localhost:${PORT}`);
  console.log(`  GET /v1/health        → health check`);
  console.log(`  GET /v1/capabilities  → capabilities manifest`);
  console.log(`  GET /v1/version       → version manifest`);
  console.log(`  Environment: sandbox, livemode: false`);
});
