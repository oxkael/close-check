"use client";

import { useEffect, useState, useRef } from "react";
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
        <main className="min-h-screen p-6" role="main" aria-busy={loading}>
            <div className="mx-auto max-w-4xl">
                <header className="mb-6">
                    <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">CloseWatch</p>
                    <h1 className="mt-2 text-3xl font-semibold">{signal?.underlying_name ?? symbol}</h1>
                    <p className="mt-1 text-sm text-slate-400">{symbol}</p>
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
                        <div className="rounded-xl border p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-sm text-slate-400">Exchange</div>
                                    <div className="text-lg font-medium">{signal.exchange}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-slate-400">Market</div>
                                    <div className="text-lg">{signal.market_closed ? "Closed" : "Open"}</div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="rounded-xl border p-4">
                                <div className="text-sm text-slate-400">Last real close</div>
                                <div className="mt-2 text-xl font-semibold">${signal.last_real_close.toFixed(2)}</div>
                            </div>
                            <div className="rounded-xl border p-4">
                                <div className="text-sm text-slate-400">Token price</div>
                                <div className="mt-2 text-xl font-semibold">${signal.token_price.toFixed(2)}</div>
                            </div>
                        </div>

                        <div className="rounded-xl border p-4">
                            <div className="text-sm text-slate-400">Current gap</div>
                            <div className="mt-2 text-2xl font-semibold">{signal.gap_pct.toFixed(2)}%</div>
                            <div className="mt-2 text-sm">Bucket: {signal.bucket}</div>
                        </div>

                        <div className="rounded-xl border p-4">
                            <h3 className="text-lg font-medium">Bucket stats</h3>
                            {signal.bucket_stats ? (
                                <div className="mt-3 space-y-2 text-sm">
                                    <div>Sample size: {signal.bucket_stats.sample_size}</div>
                                    <div>Convergence rate: {(signal.bucket_stats.convergence_rate * 100).toFixed(1)}%</div>
                                    <div>Avg time to converge: {signal.bucket_stats.avg_time_to_converge_hours ?? "No data"}h</div>
                                    <div>Worst-case gap: {signal.bucket_stats.worst_case_gap_pct ?? "No data"}%</div>
                                </div>
                            ) : (
                                <div className="mt-3 text-sm">No data for this bucket yet.</div>
                            )}
                        </div>

                        <div className="rounded-xl border p-4">
                            <h3 className="text-lg font-medium">Gap trend</h3>
                            <div className="mt-3">
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

                        <div className="rounded-xl border p-4">
                            <h3 className="text-lg font-medium">Accuracy summary</h3>
                            <div className="mt-3 text-sm">
                                <div>Resolved: {signal.accuracy_summary.resolved_predictions}</div>
                                <div>Converged: {signal.accuracy_summary.converged}</div>
                                <div>Accuracy: {signal.accuracy_summary.accuracy_pct.toFixed(2)}%</div>
                                <div>Last recalibrated: {signal.accuracy_summary.last_recalibrated ? new Date(signal.accuracy_summary.last_recalibrated).toLocaleString() : "No data"}</div>
                            </div>
                        </div>

                        {calibration ? (
                            <div className="rounded-xl border p-4">
                                <h3 className="text-lg font-medium">All buckets (sample)</h3>
                                <div className="mt-3 grid gap-2">
                                    {calibration.map((b) => (
                                        <div key={b.bucket} className="rounded-md border p-2 text-sm">
                                            <div className="flex justify-between">
                                                <div>{b.bucket}</div>
                                                <div>n={b.sample_size}</div>
                                            </div>
                                            <div className="text-xs">conv {Math.round((b.convergence_rate ?? 0) * 100)}% • avg {b.avg_time_to_converge_hours ?? "-"}h</div>
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
