"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Sparkline from "../../../components/Sparkline";

type BucketStats = {
    bucket: string;
    symbol: string;
    sample_size: number;
    convergence_rate: number;
    avg_time_to_converge_hours: number | null;
    worst_case_gap_pct: number | null;
    last_updated: string | null;
};

type AccuracySummary = {
    resolved_predictions: number;
    converged: number;
    accuracy_pct: number;
    last_recalibrated?: string | null;
};

type Signal = {
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

type HistoryResponse = {
    history: {
        real_closes: Array<{ date: string; price: number }>;
        token_prices: Array<{ timestamp: string; price: number }>;
    };
};

export default function TickerPage() {
    const params = useParams() as { symbol?: string };
    const symbol = params?.symbol ?? "";

    const [signal, setSignal] = useState<Signal | null>(null);
    const [history, setHistory] = useState<HistoryResponse | null>(null);
    const [calibration, setCalibration] = useState<BucketStats[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const pollRef = useRef<number | null>(null);

    useEffect(() => {
        if (!symbol) return;

        let cancelled = false;

        const load = async () => {
            try {
                setLoading(true);
                const r1 = await fetch(`/api/ticker/${symbol}/signal`);
                if (!r1.ok) throw new Error(`signal ${r1.status}`);
                const sig = await r1.json();
                if (cancelled) return;
                setSignal(sig);

                const r2 = await fetch(`/api/ticker/${symbol}/calibration`);
                if (r2.ok) {
                    const cal = await r2.json();
                    if (!cancelled) setCalibration(cal.buckets ?? []);
                }

                const r3 = await fetch(`/api/ticker/${symbol}/history`);
                if (r3.ok) {
                    const hist = await r3.json();
                    if (!cancelled) setHistory(hist);
                }
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : String(err));
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        load();

        // Poll every 30 seconds for new signal
        pollRef.current = window.setInterval(() => {
            load();
        }, 30_000);

        return () => {
            cancelled = true;
            if (pollRef.current) window.clearInterval(pollRef.current);
        };
    }, [symbol]);

    if (!symbol) return <div className="p-6">Missing symbol</div>;

    return (
        <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(148,163,184,0.14),_transparent_24%),linear-gradient(180deg,_#020817_0%,_#0f172a_100%)] p-6 text-slate-100" role="main" aria-busy={loading}>
            <div className="mx-auto max-w-5xl">
                <header className="mb-6 flex items-start justify-between gap-4 border-b border-slate-800/80 pb-5">
                    <div>
                        <p className="text-[11px] uppercase tracking-[0.25em] text-slate-400">CloseWatch</p>
                        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em] text-white">{signal?.underlying_name ?? symbol}</h1>
                        <p className="mt-1 text-sm text-slate-400">{symbol}</p>
                    </div>
                    <Link href="/" className="rounded-full border border-slate-700 bg-slate-900/80 px-3.5 py-2 text-sm text-slate-200 transition hover:border-slate-500 hover:text-white">
                        Back to dashboard
                    </Link>
                </header>

                {loading ? (
                    <section className="space-y-4">
                        <div className="h-8 w-1/3 animate-pulse bg-slate-700/30 rounded-md" />
                        <div className="grid grid-cols-2 gap-4">
                            <div className="h-20 animate-pulse bg-slate-700/30 rounded-md" />
                            <div className="h-20 animate-pulse bg-slate-700/30 rounded-md" />
                        </div>
                        <div className="h-24 animate-pulse bg-slate-700/30 rounded-md" />
                        <div className="h-32 animate-pulse bg-slate-700/30 rounded-md" />
                    </section>
                ) : error ? (
                    <div className="text-rose-400" role="alert" aria-live="assertive">
                        <div>{error}</div>
                        <div className="mt-3">
                            <button
                                className="rounded bg-rose-600 px-3 py-1 text-sm text-white"
                                aria-label={`Retry loading ${symbol} signal`}
                                onClick={() => {
                                    setError(null);
                                    setLoading(true);
                                    fetch(`/api/ticker/${symbol}/signal`).then((r) => r.json()).then((s) => setSignal(s)).catch((e) => setError(String(e))).finally(() => setLoading(false));
                                }}
                            >
                                Retry
                            </button>
                        </div>
                    </div>
                ) : signal ? (
                    <section className="space-y-6">
                        <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-xl shadow-slate-950/20 backdrop-blur-sm">
                            <div className="flex items-center justify-between gap-4">
                                <div>
                                    <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Exchange</div>
                                    <div className="mt-1 text-lg font-medium text-white">{signal.exchange}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Market</div>
                                    <div className={`mt-1 text-lg font-medium ${signal.market_closed ? "text-amber-300" : "text-emerald-300"}`}>
                                        {signal.market_closed ? "Closed" : "Open"}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-lg shadow-slate-950/20">
                                <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Last real close</div>
                                <div className="mt-2 text-xl font-semibold text-white">${signal.last_real_close.toFixed(2)}</div>
                            </div>
                            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-lg shadow-slate-950/20">
                                <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Token price</div>
                                <div className="mt-2 text-xl font-semibold text-white">${signal.token_price.toFixed(2)}</div>
                            </div>
                        </div>

                        <div className="rounded-2xl border border-slate-600/80 bg-slate-800/80 p-4 shadow-lg shadow-slate-950/10">
                            <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Current gap</div>
                            <div className="mt-2 text-3xl font-semibold tracking-[-0.04em] text-white">{signal.gap_pct.toFixed(2)}%</div>
                            <div className="mt-2 text-sm text-slate-300">Bucket: {signal.bucket}</div>
                        </div>

                        <div className="grid gap-6 lg:grid-cols-2">
                            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-xl shadow-slate-950/20">
                                <h3 className="text-lg font-medium text-white">Bucket stats</h3>
                                {signal.bucket_stats ? (
                                    <div className="mt-3 space-y-2 text-sm text-slate-300">
                                        <div>Sample size: <span className="text-white">{signal.bucket_stats.sample_size}</span></div>
                                        <div>Convergence rate: <span className="text-white">{(signal.bucket_stats.convergence_rate * 100).toFixed(1)}%</span></div>
                                        <div>Avg time to converge: <span className="text-white">{signal.bucket_stats.avg_time_to_converge_hours ?? "No data"}h</span></div>
                                        <div>Worst-case gap: <span className="text-white">{signal.bucket_stats.worst_case_gap_pct ?? "No data"}%</span></div>
                                    </div>
                                ) : (
                                    <div className="mt-3 text-sm text-slate-400">No data for this bucket yet.</div>
                                )}
                            </div>

                            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-xl shadow-slate-950/20">
                                <h3 className="text-lg font-medium text-white">Accuracy summary</h3>
                                <div className="mt-3 space-y-2 text-sm text-slate-300">
                                    <div>Resolved: <span className="text-white">{signal.accuracy_summary.resolved_predictions}</span></div>
                                    <div>Converged: <span className="text-white">{signal.accuracy_summary.converged}</span></div>
                                    <div>Accuracy: <span className="text-white">{signal.accuracy_summary.accuracy_pct.toFixed(2)}%</span></div>
                                    <div>Last recalibrated: <span className="text-white">{signal.accuracy_summary.last_recalibrated ? new Date(signal.accuracy_summary.last_recalibrated).toLocaleString() : "No data"}</span></div>
                                </div>
                            </div>
                        </div>

                        <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-xl shadow-slate-950/20">
                            <h3 className="text-lg font-medium text-white">Gap trend</h3>
                            <div className="mt-3 overflow-hidden rounded-xl border border-slate-800 bg-slate-950/60 p-2">
                                {history && history.history && (history.history.real_closes.length > 0 || history.history.token_prices.length > 0) ? (
                                    (() => {
                                        const trendValues = [
                                            ...history.history.real_closes.map((entry) => entry.price),
                                            ...history.history.token_prices.map((entry) => entry.price),
                                        ];
                                        return trendValues.length > 1 ? (
                                            <Sparkline values={trendValues} width={480} height={80} stroke="#06b6d4" />
                                        ) : (
                                            <div className="text-sm text-slate-400">No trend available — insufficient data.</div>
                                        );
                                    })()
                                ) : (
                                    <div className="text-sm text-slate-400">No trend available — insufficient data.</div>
                                )}
                            </div>
                        </div>

                        {calibration ? (
                            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-xl shadow-slate-950/20">
                                <h3 className="text-lg font-medium text-white">All buckets (sample)</h3>
                                <div className="mt-3 grid gap-2">
                                    {calibration.map((b) => (
                                        <div key={b.bucket} className="rounded-xl border border-slate-700 bg-slate-800/70 p-3 text-sm text-slate-300">
                                            <div className="flex justify-between gap-3">
                                                <div className="font-medium text-white">{b.bucket}</div>
                                                <div>n={b.sample_size}</div>
                                            </div>
                                            <div className="mt-1 text-xs text-slate-400">conv {Math.round((b.convergence_rate ?? 0) * 100)}% • avg {b.avg_time_to_converge_hours ?? "-"}h</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : null}
                    </section>
                ) : null}
            </div>
        </main>
    );
}
