import { useEffect, useRef, useState } from "react";
import { sampleFaceFromVideo } from "../utils/faceLandmarks";
import { inferFocusScore } from "../utils/focusInference";

type Props = {
  enabled: boolean;
  onScore: (score: number, meta: { modelName: string; extractionType: string }) => void;
  intervalMs?: number;
};

export function Camera({ enabled, onScore, intervalMs = 2000 }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [liveScore, setLiveScore] = useState<number | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let stream: MediaStream | null = null;
    let cancelled = false;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: 640, height: 480 },
          audio: false,
        });
        if (cancelled || !videoRef.current) return;
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      } catch {
        if (!cancelled) setError("Camera permission denied or unavailable.");
      }
    }

    start();
    return () => {
      cancelled = true;
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;

    const tick = async () => {
      const video = videoRef.current;
      if (!video || cancelled) return;
      const sample = await sampleFaceFromVideo(video);
      const result = await inferFocusScore(sample);
      if (cancelled) return;
      setLiveScore(result.score);
      onScore(result.score, {
        modelName: result.modelName,
        extractionType: result.extractionType,
      });
    };

    tick();
    const id = window.setInterval(tick, intervalMs);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [enabled, intervalMs, onScore]);

  return (
    <div className="camera-panel">
      <video ref={videoRef} muted playsInline className="camera-video" />
      {error && <p className="error">{error}</p>}
      {!error && (
        <p className="camera-meta">
          Live focus: {liveScore === null ? "…" : `${Math.round(liveScore * 100)}%`}
        </p>
      )}
    </div>
  );
}
