import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { api, type WatchHistoryItem } from "../api";
import { useAuth } from "../auth";

export function History() {
  const { token, user, loading } = useAuth();
  const [items, setItems] = useState<WatchHistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .history(token)
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"));
  }, [token]);

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  return (
    <main className="page">
      <h1>History</h1>
      <p className="muted">Past focus sessions for your account only.</p>
      {error && <p className="error">{error}</p>}
      <ul className="history-list">
        {items.map((item) => (
          <li key={item.watch_item_id}>
            <div>
              <strong>{item.video_name || item.youtube_id}</strong>
              <div className="muted">
                {item.status} · watched {Math.round(item.current_time)}s · focus{" "}
                {item.average_focus === null ? "n/a" : `${Math.round(item.average_focus * 100)}%`}
              </div>
            </div>
            <time>{new Date(item.last_updated).toLocaleString()}</time>
          </li>
        ))}
        {items.length === 0 && <li className="muted">No sessions yet.</li>}
      </ul>
    </main>
  );
}
