"use client";

import React from "react";

type Props = {
    className?: string;
    width?: number | string;
    height?: number | string;
    rounded?: string;
};

export default function Skeleton({ className = "", width = "100%", height = 16, rounded = "md" }: Props) {
    const style: React.CSSProperties = {
        width: typeof width === "number" ? `${width}px` : width,
        height: typeof height === "number" ? `${height}px` : height,
    };
    // Skeletons are presentational; hide from assistive tech
    return (
        <div
            aria-hidden="true"
            className={`animate-pulse bg-slate-700/30 ${className} rounded-${rounded}`}
            style={style}
        />
    );
}
