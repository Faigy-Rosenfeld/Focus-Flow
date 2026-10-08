import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";
import { api, type Video } from "../api";
import { useAuth } from "../auth";

export function Library() {
  const { token, user, loading } = useAuth();
  const [videos, setVideos] = useState<Video[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [youtubeId, setYoutubeId] = useState("dQw4w9WgXcQ");
  const [name, setName] = useState("Sample learning video");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!token) return;
    api
      .listVideos(token)
      .then(setVideos)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [token]);

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  async function onAdd(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await api.createVideo(token!, {
        youtube_id: youtubeId.trim(),
        name: name.trim(),
        description: "Added from FocusFlow library",
        subject_name: "learning",
      });
      setVideos((prev) => [created, ...prev]);
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add video");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <h1>Library</h1>
      <p className="muted">Choose a video and start a focus session.</p>

      <form className="add-form" onSubmit={onAdd}>
        <label>
          YouTube ID
          <input value={youtubeId} onChange={(e) => setYoutubeId(e.target.value)} required />
        </label>
        <label>
          Title
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "Adding…" : "Add video"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul className="video-list">
        {videos.map((video) => (
          <li key={video.video_id}>
            <div>
              <strong>{video.name}</strong>
              <span className="muted"> · {video.youtube_id}</span>
            </div>
            <Link className="button-link" to={`/session/${video.youtube_id}`}>
              Start session
            </Link>
          </li>
        ))}
        {videos.length === 0 && <li className="muted">No videos yet — add one above.</li>}
      </ul>
    </main>
  );
}
