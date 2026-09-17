"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type AccuracySummary = {
  resolved_predictions: number;
  converged: number;
  accuracy_pct: number;
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

const formatPercent = (value: number | null | undefined) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "No data";
  }
  return `${value.toFixed(2)}%`;
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
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100" aria-busy={loading}>
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-col gap-4 border-b border-slate-800 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-400">
              CloseWatch
            </p>
            <h1 className="mt-2 text-4xl font-semibold tracking-tight text-white">
              Closure-gap intelligence for tokenized equities
            </h1>
          </div>
          <div className="rounded-full border border-cyan-500/50 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-200">
            API-driven dashboard
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
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Tracked tickers</p>
                <p className="mt-3 text-3xl font-semibold text-white">{summary.count}</p>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Accuracy</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-400">
                  {formatPercent(topAccuracy.accuracy_pct)}
                </p>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Resolved predictions</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {topAccuracy.resolved_predictions}
                </p>
              </div>
            </section>

            <section className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3" aria-live="polite">
              {summary.tickers.map((ticker, idx) => {
                const bucketStats = ticker.bucket_stats;
                const sampleSize = bucketStats?.sample_size ?? 0;
                const lowConfidence = sampleSize < 10;
                return (
                  <Link key={ticker.symbol} href={`/ticker/${ticker.symbol}`} className="block">
                    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg shadow-slate-950/20" role="article" aria-labelledby={`ticker-${idx}-title`}>
                      <div className="mb-5 flex items-center justify-between gap-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                            {ticker.exchange}
                          </p>
                          <h2 id={`ticker-${idx}-title`} className="mt-1 text-2xl font-semibold text-white">{ticker.symbol}</h2>
                        </div>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-medium ${
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
                          <div className="rounded-xl bg-slate-800/80 p-3">
                            <p className="text-xs text-slate-400">Last real close</p>
                            <p className="mt-2 text-lg font-medium text-white">
                              ${ticker.last_real_close.toFixed(2)}
                            </p>
                          </div>
                          <div className="rounded-xl bg-slate-800/80 p-3">
                            <p className="text-xs text-slate-400">Token price</p>
                            <p className="mt-2 text-lg font-medium text-white">
                              ${ticker.token_price.toFixed(2)}
                            </p>
                          </div>
                        </div>

                        <div className="rounded-xl border border-slate-700 bg-slate-800/70 p-3">
                          <p className="text-xs text-slate-400">Current gap</p>
                          <p className="mt-2 text-2xl font-semibold text-cyan-300">
                            {formatPercent(ticker.gap_pct)}
                          </p>
                        </div>

                        <div className="rounded-xl border border-slate-700 bg-slate-800/70 p-3">
                          <p className="text-xs text-slate-400">Bucket</p>
                          <p className="mt-2 text-lg font-medium text-white">{ticker.bucket}</p>
                          <p className="mt-2 text-sm text-slate-300">
                            Convergence rate: {bucketStats ? formatPercent(bucketStats.convergence_rate * 100) : "No data"}
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
