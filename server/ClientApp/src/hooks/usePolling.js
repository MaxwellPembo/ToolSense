import { useEffect, useRef, useState } from 'react';

// usePolling: fetches `url` every `interval` ms. Uses ETag (If-None-Match) to skip updates when unchanged.
// Pauses polling when document is hidden (tab inactive) to save resources.
export function usePolling(url, interval = 2000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const etagRef = useRef(null);
  const timerRef = useRef(null);
  const isFetchingRef = useRef(false);

  useEffect(() => {
    let mounted = true;

    const fetchOnce = async () => {
      if (isFetchingRef.current) return; // avoid overlapping
      isFetchingRef.current = true;
      try {
        const headers = { 'Cache-Control': 'no-cache' };
        if (etagRef.current) headers['If-None-Match'] = etagRef.current;

        const res = await fetch(url, { headers, cache: 'no-store' });
        if (res.status === 304) {
          // not modified
          isFetchingRef.current = false;
          return;
        }

        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);

        const json = await res.json();
        const newEtag = res.headers.get('ETag');
        if (newEtag) etagRef.current = newEtag;
        if (mounted) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (mounted) setError(err);
        console.error('usePolling fetch error', err);
      } finally {
        isFetchingRef.current = false;
      }
    };

    const start = () => {
      fetchOnce();
      timerRef.current = setInterval(fetchOnce, interval);
    };

    const stop = () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };

    const onVisibility = () => {
      if (document.hidden) stop();
      else start();
    };

    document.addEventListener('visibilitychange', onVisibility);
    start();

    return () => {
      mounted = false;
      stop();
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [url, interval]);

  return { data, error };
}
