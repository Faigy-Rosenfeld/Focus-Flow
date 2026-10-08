/**
 * Lightweight face presence detector using getUserMedia + canvas brightness variance.
 * MediaPipe can be plugged in later; this keeps the camera pipeline working offline.
 */

export type FaceSample = {
  facePresent: boolean;
  landmarks: Array<{ x: number; y: number; z?: number }>;
};

export async function sampleFaceFromVideo(video: HTMLVideoElement): Promise<FaceSample> {
  if (!video.videoWidth || !video.videoHeight) {
    return { facePresent: false, landmarks: [] };
  }

  const canvas = document.createElement("canvas");
  const width = 96;
  const height = 72;
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return { facePresent: false, landmarks: [] };

  ctx.drawImage(video, 0, 0, width, height);
  const { data } = ctx.getImageData(0, 0, width, height);

  let sum = 0;
  let sumSq = 0;
  const pixels = width * height;
  for (let i = 0; i < data.length; i += 4) {
    const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    sum += gray;
    sumSq += gray * gray;
  }
  const mean = sum / pixels;
  const variance = sumSq / pixels - mean * mean;
  const facePresent = variance > 180 && mean > 25 && mean < 220;

  // Synthetic landmark grid around center for ONNX feature padding.
  const landmarks: Array<{ x: number; y: number; z?: number }> = [];
  if (facePresent) {
    for (let i = 0; i < 478; i++) {
      const angle = (i / 478) * Math.PI * 2;
      landmarks.push({
        x: 0.5 + Math.cos(angle) * 0.15,
        y: 0.5 + Math.sin(angle) * 0.2,
        z: 0,
      });
    }
  }

  return { facePresent, landmarks };
}
