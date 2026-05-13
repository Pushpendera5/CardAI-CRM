import axios from "axios";

export const cardAiApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: false,
});

cardAiApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string) {
  const { data } = await cardAiApi.post("/auth/login", { email, password });
  localStorage.setItem("accessToken", data.data.access_token);
  localStorage.setItem("refreshToken", data.data.refresh_token);
  return data.data;
}

export async function scanBusinessCard(image: File) {
  const formData = new FormData();
  formData.append("image", image);
  const { data } = await cardAiApi.post("/cards/scan", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data.data;
}

export async function getContacts(params = { page: 1, page_size: 20 }) {
  const { data } = await cardAiApi.get("/contacts", { params });
  return data.data;
}

