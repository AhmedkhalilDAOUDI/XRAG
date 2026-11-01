import type { NextConfig } from "next";

// vinext (the Cloudflare build) also reads this file, so the stand-in for `cloudflare:workers` applies only to the Vercel build.
const vercel = process.env.XRAG_TARGET === "vercel";

const nextConfig: NextConfig = vercel
  ? { turbopack: { resolveAlias: { "cloudflare:workers": "./lib/vercel-env.ts" } } }
  : {};

export default nextConfig;
