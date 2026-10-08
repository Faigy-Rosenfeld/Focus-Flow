import { useCallback, useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { api, type Video, type WatchItem } from "../api";
import { useAuth } from "../auth";
import { Camera } from "../components/Camera";
import { ContentViewer } from "../components/ContentViewer";

export function Session() {
  const { youtubeId = "" } = useParams();
  const { token, user, loading } = useAuth();
  const [video, setVideo] = useState<Video | null>(null);
  const [watchItem, setWatchItem] = useState<WatchItem | null>(null);
  const [averageFocus, setAverageFocus] = useState<number | null>(null);
  const [lastScore, setLastScore] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ended, setEnded] = useState(false);
  const startedAt = useRef(Date.now());
  const posting = useRef(false);

  useEffect(() => {
    if (!token || !youtubeId) return;
    let cancelled = false;

    async function boot() {
      try {
        const videos = await api.listVideos(token!);
        const found = videos.find((v) => v.youtube_id === youtubeId) || null;
        if (!found) throw new Error("Video not found in library");
        const session = await api.startSession(token!, youtubeId);
        if (cancelled) return;
        setVideo(found);
        setWatchItem(session);
        setAverageFocus(session.average_focus);
        startedAt.current = Date.now();
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not start session");
      }
    }

    boot();
    return () => {
      cancelled = true;
    };
  }, [token, youtubeId]);

  const onScore = useCallback(
    async (score: number, meta: { modelName: string; extractionType: string }) => {
      if (!token || !watchItem || ended || posting.current) return;
      posting.current = true;
      setLastScore(score);
      try {
        const vidWatchTime = (Date.now() - startedAt.current) / 1000;
        const res = await api.postFocus(token, watchItem.watch_item_id, {
          focus_score: score,
          vid_watch_time: vidWatchTime,
          model_name: meta.modelName,
          extraction_type: meta.extractionType,
        });
        setAverageFocus(res.average_focus);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to save focus sample");
      } finally {
        posting.current = false;
      }
    },
    [token, watchItem, ended],
  );

  async function endSession() {
    if (!token || !watchItem) return;
    try {
      const res = await api.endSession(token, watchItem.watch_item_id);
      setWatchItem(res);
      setEnded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not end session");
    }
  }

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  return (
    <main className="page session-page">
      <div className="session-top">
        <Link to="/library">← Back to library</Link>
        <div className="scoreboard">
          <span>Last: {lastScore === null ? "—" : `${Math.round(lastScore * 100)}%`}</span>
          <span>
            Average: {averageFocus === null ? "—" : `${Math.round(averageFocus * 100)}%`}
          </span>
          {!ended && (
            <button type="button" onClick={endSession}>
              End session
            </button>
          )}
          {ended && <span className="ok">Session ended</span>}
        </div>
      </div>

      {error && <p className="error">{error}</p>}

      {video && (
        <div className="session-grid">
          <ContentViewer youtubeId={video.youtube_id} title={video.name} />
          <Camera enabled={!ended && !!watchItem} onScore={onScore} />
        </div>
      )}

      {averageFocus !== null && averageFocus < 0.4 && !ended && (
        <p className="warn">Low focus detected — try looking at the content and facing the camera.</p>
      )}
    </main>
  );
}
