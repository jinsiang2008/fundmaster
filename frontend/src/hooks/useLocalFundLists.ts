/**
 * Watchlist & recent funds backed by localStorage.
 *
 * 注意：不能用 useSyncExternalStore + 每次返回新数组的 getSnapshot，
 * 否则会触发无限重渲染与白屏（React 要求快照在数据未变时保持引用稳定）。
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { addToRecent, loadRecentFunds, loadWatchlist, toggleWatchlist } from '../utils/storage';
import type { FundSearchResult } from '../types/fund';

function emitWatchlist() {
  window.dispatchEvent(new Event('fundmaster-watchlist'));
}

function emitRecent() {
  window.dispatchEvent(new Event('fundmaster-recent'));
}

export function useWatchlist() {
  const [items, setItems] = useState<FundSearchResult[]>(() => loadWatchlist());

  useEffect(() => {
    const sync = () => setItems(loadWatchlist());
    window.addEventListener('fundmaster-watchlist', sync);
    window.addEventListener('storage', sync);
    return () => {
      window.removeEventListener('fundmaster-watchlist', sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  const toggle = useCallback((fund: FundSearchResult) => {
    toggleWatchlist(fund);
    setItems(loadWatchlist());
    emitWatchlist();
  }, []);

  const isInWatchlist = useCallback(
    (code: string) => items.some((f) => f.code === code),
    [items]
  );

  return useMemo(
    () => ({
      watchlist: items,
      toggleWatchlist: toggle,
      isInWatchlist,
    }),
    [items, toggle, isInWatchlist]
  );
}

export function useRecentFunds() {
  const [items, setItems] = useState<FundSearchResult[]>(() => loadRecentFunds());

  useEffect(() => {
    const sync = () => setItems(loadRecentFunds());
    window.addEventListener('fundmaster-recent', sync);
    window.addEventListener('storage', sync);
    return () => {
      window.removeEventListener('fundmaster-recent', sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  const recordVisit = useCallback((fund: FundSearchResult) => {
    addToRecent(fund);
    setItems(loadRecentFunds());
    emitRecent();
  }, []);

  return useMemo(
    () => ({
      recentFunds: items,
      recordVisit,
    }),
    [items, recordVisit]
  );
}
