"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type AccuracySummary = {
  resolved_predictions: number;
  converged: number;
  accuracy_pct: number;
  last_recalibrated?: string | null;
};

type BucketStats = {
  bucket: string;
  symbol: string;
  sample_size: number;
  convergence_rate: number;
  avg_time_to_converge_hours: number | null;
  worst_case_gap_pct: number | null;
  last_updated: string | null;
};

type TickerSignal = {
  symbol: string;
  underlying_name?: string;
  exchange: string;
  market_closed: boolean;
  last_real_close: number;
  token_price: number;
  gap_pct: number;
  bucket: string;
  bucket_stats: BucketStats | null;
  accuracy_summary: AccuracySummary;
};

type SummaryResponse = {
  count: number;
  tickers: TickerSignal[];
  accuracy_summary: AccuracySummary;
};

// value is a fraction already expressed as a percent (e.g. 5.0 for 5%)
const formatPercent = (value: number | null | undefined) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "No data";
  }
  return `${value.toFixed(2)}%`;
};

// value is a fractional ratio (0.05 => 5%). Use this for convergence_rate fields.
const formatRatioAsPercent = (value: number | null | undefined) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "No data";
  }
  return `${(value * 100).toFixed(2)}%`;
};

const formatHours = (value: number | null | undefined) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "No data";
  }
  return `${value.toFixed(1)}h`;
};

export default function Home() {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setLoading(true);
        const response = await fetch("/api/summary", { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const payload: SummaryResponse = await response.json();
        setSummary(payload);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load summary");
      } finally {
        setLoading(false);
      }
    };

    loadSummary();
  }, []);

  const topAccuracy = summary?.accuracy_summary ?? { resolved_predictions: 0, converged: 0, accuracy_pct: 0 };
 
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(148,163,184,0.14),_transparent_20%),linear-gradient(180deg,_#020817_0%,_#0f172a_100%)] px-5 py-8 text-slate-100 sm:px-6 lg:px-8" aria-busy={loading}>
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-col gap-4 border-b border-slate-800/80 pb-6 md:flex-row md:items-end md:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-medium uppercase tracking-[0.28em] text-slate-400">
              CloseWatch
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] text-white md:text-5xl">
              Closure-gap intelligence for tokenized equities
            </h1>
          </div>
          <div className="rounded-full border border-slate-700 bg-slate-900/80 px-3.5 py-2 text-sm text-slate-200 shadow-[0_0_20px_rgba(15,23,42,0.35)]">
            Market intelligence
          </div>
        </header>

        {loading ? (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="mb-3">
                <div className="h-3 w-32 animate-pulse bg-slate-700/30 rounded-md"></div>
              </div>
              <div className="h-8 w-20 animate-pulse bg-slate-700/30 rounded-md"></div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="mb-3">
                <div className="h-3 w-32 animate-pulse bg-slate-700/30 rounded-md"></div>
              </div>
              <div className="h-8 w-20 animate-pulse bg-slate-700/30 rounded-md"></div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="mb-3">
                <div className="h-3 w-32 animate-pulse bg-slate-700/30 rounded-md"></div>
              </div>
              <div className="h-8 w-20 animate-pulse bg-slate-700/30 rounded-md"></div>
            </div>
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-8 text-rose-200">
            Unable to reach the backend. Check that the FastAPI service is running on port 8000.
          </div>
        ) : summary ? (
          <>
            <section className="mb-8 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-700/80 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/20 backdrop-blur-sm">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Tracked tickers</p>
                <p className="mt-4 text-3xl font-semibold text-white">{summary.count}</p>
              </div>
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5 shadow-xl shadow-emerald-950/10 backdrop-blur-sm">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-300">Accuracy</p>
                <p className="mt-4 text-3xl font-semibold text-emerald-300">
                  {formatPercent(topAccuracy.accuracy_pct)}
                </p>
              </div>
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5 shadow-xl shadow-cyan-950/10 backdrop-blur-sm">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-300">Resolved predictions</p>
                <p className="mt-4 text-3xl font-semibold text-cyan-300">
                  {topAccuracy.resolved_predictions}
                </p>
                <p className="mt-2 text-xs text-slate-400">
                  Last recalibrated: {topAccuracy.last_recalibrated ? new Date(topAccuracy.last_recalibrated).toLocaleString() : "No data"}
                </p>
              </div>
            </section>

            <section className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3" aria-live="polite">
              {summary.tickers.map((ticker, idx) => {
                const bucketStats = ticker.bucket_stats;
                const sampleSize = bucketStats?.sample_size ?? 0;
                const lowConfidence = sampleSize < 10;
                return (
                  <Link key={ticker.symbol} href={`/ticker/${ticker.symbol}`} className="group block">
                    <article className="h-full rounded-2xl border border-slate-700/80 bg-slate-900/80 p-5 shadow-lg shadow-slate-950/20 transition duration-200 group-hover:-translate-y-0.5 group-hover:border-slate-500 group-hover:shadow-slate-800/60" role="article" aria-labelledby={`ticker-${idx}-title`}>
                      <div className="mb-5 flex items-start justify-between gap-3">
                        <div>
                          <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
                            {ticker.exchange}
                          </p>
                          <h2 id={`ticker-${idx}-title`} className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-white">{ticker.symbol}</h2>
                          <p className="mt-1 text-sm text-slate-300">{ticker.underlying_name ?? "Underlying name unavailable"}</p>
                        </div>
                        <span
                          className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
                            ticker.market_closed
                              ? "bg-amber-500/15 text-amber-200 ring-1 ring-amber-500/40"
                              : "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-500/40"
                          }`}
                        >
                          {ticker.market_closed ? "Closed" : "Open"}
                        </span>
                      </div>

                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="rounded-xl bg-slate-800/80 p-3.5">
                            <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">Last real close</p>
                            <p className="mt-2 text-lg font-medium text-white">
                              ${ticker.last_real_close.toFixed(2)}
                            </p>
                          </div>
                          <div className="rounded-xl bg-slate-800/80 p-3.5">
                            <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">Token price</p>
                            <p className="mt-2 text-lg font-medium text-white">
                              ${ticker.token_price.toFixed(2)}
                            </p>
                          </div>
                        </div>

                        <div className="rounded-xl border border-slate-600/80 bg-slate-800/80 p-3.5">
                          <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">Current gap</p>
                          <p className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-white">
                            {formatPercent(ticker.gap_pct)}
                          </p>
                        </div>

                        <div className="rounded-xl border border-slate-700 bg-slate-800/70 p-3.5">
                          <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">Bucket</p>
                          <p className="mt-2 text-lg font-medium text-white">{ticker.bucket}</p>
                          <p className="mt-2 text-sm text-slate-300">
                            Convergence rate: {bucketStats ? formatRatioAsPercent(bucketStats.convergence_rate) : "No data"}
                          </p>
                          <p className="mt-1 text-sm text-slate-300">
                            Avg time to converge: {bucketStats ? formatHours(bucketStats.avg_time_to_converge_hours) : "No data"}
                          </p>
                          <p className="mt-1 text-sm text-slate-300">
                            Worst-case tail: {bucketStats ? formatPercent(bucketStats.worst_case_gap_pct) : "No data"}
                          </p>
                          {lowConfidence ? (
                            <p className="mt-2 text-xs text-amber-300">
                              Low-confidence bucket: sample size {sampleSize} is below the 10-row confidence threshold.
                            </p>
                          ) : null}
                        </div>
                      </div>
                    </article>
                  </Link>
                );
              })}
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}
