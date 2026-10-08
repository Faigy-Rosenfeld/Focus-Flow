const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export type User = {
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  creation_date: string;
  permission: number;
  active: boolean;
};

export type Video = {
  video_id: number;
  youtube_id: string;
  upload_by: number | null;
  name: string;
  description: string;
  subject_name: string;
  added_date: string;
  length_seconds: number;
};

export type WatchItem = {
  watch_item_id: number;
  user_id: number;
  youtube_id: string;
  current_time: number;
  save_time: string;
  last_updated: string;
  status: string;
  average_focus: number | null;
};

export type WatchHistoryItem = {
  watch_item_id: number;
  youtube_id: string;
  video_name: string | null;
  status: string;
  current_time: number;
  average_focus: number | null;
  last_updated: string;
};

function authHeaders(token?: string | null): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    let detail = "Request failed";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  register(data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  }) {
    return request<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
  },
  login(data: { email: string; password: string }) {
    return request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
  },
  me(token: string) {
    return request<User>("/auth/me", { headers: authHeaders(token) });
  },
  listVideos(token: string) {
    return request<Video[]>("/content/videos", { headers: authHeaders(token) });
  },
  createVideo(
    token: string,
    data: {
      youtube_id: string;
      name: string;
      description?: string;
      subject_name?: string;
      length_seconds?: number;
    },
  ) {
    return request<Video>("/content/videos", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  startSession(token: string, youtube_id: string) {
    return request<WatchItem>("/sessions/start", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ youtube_id }),
    });
  },
  postFocus(
    token: string,
    watchItemId: number,
    data: {
      focus_score: number;
      vid_watch_time: number;
      fps_num?: number;
      model_name?: string;
      extraction_type?: string;
    },
  ) {
    return request<{
      watch_item_id: number;
      focus_score: number;
      average_focus: number;
      status: string;
    }>(`/sessions/${watchItemId}/focus`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  endSession(token: string, watchItemId: number) {
    return request<WatchItem>(`/sessions/${watchItemId}/end`, {
      method: "POST",
      headers: authHeaders(token),
    });
  },
  history(token: string) {
    return request<WatchHistoryItem[]>("/sessions/history", {
      headers: authHeaders(token),
    });
  },
};
