/**
 * localStorage helpers with JSON safety and simple versioning.
 */

import type { FundSearchResult } from '../types/fund';

const PREFIX = 'fundmaster.v1';
const WATCHLIST_KEY = `${PREFIX}.watchlist`;
const RECENT_KEY = `${PREFIX}.recentFunds`;
const MAX_WATCHLIST = 80;
const MAX_RECENT = 30;

function safeParse<T>(raw: string | null, fallback: T): T {
  if (raw == null || raw === '') return fallback;
  try {
    const v = JSON.parse(raw) as unknown;
    if (!Array.isArray(v)) return fallback;
    return v as T;
  } catch {
    return fallback;
  }
}

function isFundItem(x: unknown): x is { code: string; name: string; type?: unknown } {
  if (!x || typeof x !== 'object') return false;
  const o = x as Record<string, unknown>;
  return typeof o.code === 'string' && typeof o.name === 'string';
}

function normalizeList(raw: unknown[]): FundSearchResult[] {
  const out: FundSearchResult[] = [];
  for (const x of raw) {
    if (!isFundItem(x)) continue;
    const typeStr = typeof x.type === 'string' ? x.type : '';
    out.push({ code: x.code.trim(), name: x.name, type: typeStr });
  }
  return out;
}

export function loadWatchlist(): FundSearchResult[] {
  const parsed = safeParse<string | unknown[]>(localStorage.getItem(WATCHLIST_KEY), []);
  if (Array.isArray(parsed)) {
    return normalizeList(parsed).slice(0, MAX_WATCHLIST);
  }
  return [];
}

export function saveWatchlist(items: FundSearchResult[]): void {
  try {
    const trimmed = items.slice(0, MAX_WATCHLIST);
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(trimmed));
  } catch {
    /* quota / private mode */
  }
}

export function loadRecentFunds(): FundSearchResult[] {
  const parsed = safeParse<string | unknown[]>(localStorage.getItem(RECENT_KEY), []);
  if (Array.isArray(parsed)) {
    return normalizeList(parsed).slice(0, MAX_RECENT);
  }
  return [];
}

export function saveRecentFunds(items: FundSearchResult[]): void {
  try {
    const trimmed = items.slice(0, MAX_RECENT);
    localStorage.setItem(RECENT_KEY, JSON.stringify(trimmed));
  } catch {
    /* ignore */
  }
}

export function addToRecent(fund: FundSearchResult): FundSearchResult[] {
  const cur = loadRecentFunds().filter((f) => f.code !== fund.code);
  const next = [{ ...fund, type: fund.type || '' }, ...cur].slice(0, MAX_RECENT);
  saveRecentFunds(next);
  return next;
}

export function toggleWatchlist(fund: FundSearchResult): { next: FundSearchResult[]; added: boolean } {
  const cur = loadWatchlist();
  const idx = cur.findIndex((f) => f.code === fund.code);
  let next: FundSearchResult[];
  let added: boolean;
  if (idx >= 0) {
    next = cur.filter((f) => f.code !== fund.code);
    added = false;
  } else {
    next = [{ ...fund, type: fund.type || '' }, ...cur].slice(0, MAX_WATCHLIST);
    added = true;
  }
  saveWatchlist(next);
  return { next, added };
}

export function isInWatchlist(code: string): boolean {
  return loadWatchlist().some((f) => f.code === code);
}
