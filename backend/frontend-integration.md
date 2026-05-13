# CardAI CRM Frontend Integration

Base URL: `http://localhost:8000/api/v1`

All JSON endpoints return:

```json
{ "success": true, "message": "Success", "data": {}, "errors": null }
```

Axios service:

```ts
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function scanCard(file: File) {
  const form = new FormData();
  form.append("image", file);
  const { data } = await api.post("/cards/scan", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data.data;
}
```

Common endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `POST /cards/scan`
- `GET /contacts?page=1&page_size=20&search=abc`
- `GET /reports/overview`
- `GET /exports/contacts.xlsx`

