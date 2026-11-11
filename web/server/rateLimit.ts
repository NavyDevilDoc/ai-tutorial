export interface RateLimitOptions {
  windowMs: number;
  max: number;
  now?: () => number;
}

export interface RateLimiter {
  check: (key: string) => { allowed: boolean; retryAfterSec: number };
}

export function createRateLimiter(opts: RateLimitOptions): RateLimiter {
  const buckets = new Map<string, { count: number; resetAt: number }>();
  const now = opts.now ?? (() => Date.now());

  return {
    check(key: string) {
      const t = now();
      const existing = buckets.get(key);
      if (!existing || existing.resetAt <= t) {
        buckets.set(key, { count: 1, resetAt: t + opts.windowMs });
        return { allowed: true, retryAfterSec: 0 };
      }
      if (existing.count >= opts.max) {
        return {
          allowed: false,
          retryAfterSec: Math.ceil((existing.resetAt - t) / 1000),
        };
      }
      existing.count += 1;
      return { allowed: true, retryAfterSec: 0 };
    },
  };
}
