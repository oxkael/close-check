"use client";

import React from "react";

type Props = {
    values: number[];
    width?: number;
    height?: number;
    stroke?: string;
    fill?: string | null;
    ariaLabel?: string;
};

export default function Sparkline({
    values,
    width = 240,
    height = 48,
    stroke = "#06b6d4",
    fill = null,
    ariaLabel,
}: Props) {
    if (!values || values.length === 0) {
        return <svg width={width} height={height} />;
    }

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    const points = values
        .map((v, i) => {
            const x = (i / (values.length - 1)) * width;
            const y = height - ((v - min) / range) * height;
            return `${x},${y}`;
        })
        .join(" ");

    const polyline = <polyline fill="none" stroke={stroke} strokeWidth={2} points={points} />;

    return (
        <svg
            width={width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
            role="img"
            aria-label={ariaLabel ?? "Sparkline chart"}
        >
            {fill ? (
                <polyline
                    points={points}
                    fill={fill}
                    stroke="none"
                    opacity={0.08}
                />
            ) : null}
            {polyline}
        </svg>
    );
}
