/**
 * DRF backend bilan ishlash (ADR-016).
 * Tiplar `src/lib/api-types.ts` da — OpenAPI schema'dan generatsiya qilinadi:
 *   make fe-types
 */
import type { components, paths } from "./api-types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";


/** Schema'dan olingan model tiplari — komponentlar shularni ishlatadi. */
export type ClinicSettings = components["schemas"]["ClinicSettings"];
export type Service = components["schemas"]["ServiceList"];
export type ServiceDetail = components["schemas"]["ServiceDetail"];
export type ServiceCategory = components["schemas"]["ServiceCategory"];
export type PriceItem = components["schemas"]["PriceItem"];
export type Doctor = components["schemas"]["DoctorList"];
export type Review = components["schemas"]["Review"];
export type CasePair = components["schemas"]["CasePair"];
export type Post = components["schemas"]["PostList"];
export type Faq = components["schemas"]["Faq"];
export type DoctorDetail = components["schemas"]["DoctorDetail"];
export type PostDetail = components["schemas"]["PostDetail"];
export type GalleryImage = components["schemas"]["GalleryImage"];
export type StaticPage = components["schemas"]["StaticPage"];
export type SeoRoutes = {
  services: { slugs: Record<string, string>; updated_at: string }[];
  doctors: { slugs: Record<string, string>; updated_at: string }[];
  cases: { slugs: Record<string, string>; updated_at: string }[];
  posts: { slugs: Record<string, string>; updated_at: string }[];
  pages: { key: string; updated_at: string }[];
};

/** Backend rasm obyekti — yalangʻoch URL emas (CLS=0 uchun). */
export type ApiImage = {
  src: string;
  width: number | null;
  height: number | null;
  alt?: string | null;
} | null;

export type ImageLike =
  | { src?: string | null; width?: number | null; height?: number | null; alt?: string | null }
  | null
  | undefined;

type Paginated<T> = { count: number; results: T[] };

/**
 * Server komponentlar uchun sodda fetch.
 * Locale `Accept-Language` orqali uzatiladi — backend modeltranslation bilan hal qiladi.
 */
async function get<T>(
  path: string,
  locale: string,
  opts: { revalidate?: number } = {},
): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
      headers: { "Accept-Language": locale },
      next: { revalidate: opts.revalidate ?? 300 },
    });
    if (!res.ok) {
      console.error(`API ${path} → ${res.status}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (err) {
    // Backend ishlamayotgan boʻlsa sahifa qulamasin — boʻsh holat koʻrsatiladi.
    console.error(`API ${path} yetib bormadi:`, err);
    return null;
  }
}

const listOf = <T>(data: Paginated<T> | T[] | null): T[] =>
  data == null ? [] : Array.isArray(data) ? data : data.results;

// ─────────────── Fetcherlar ───────────────

export const getSiteSettings = (locale: string) =>
  get<ClinicSettings>("/site-settings/", locale);

export const getServices = async (
  locale: string,
  opts: { featured?: boolean; category?: string } = {},
) => {
  const q = new URLSearchParams();
  if (opts.featured) q.set("featured", "1");
  if (opts.category) q.set("category", opts.category);
  const qs = q.toString();
  return listOf(await get<Paginated<Service>>(`/services/${qs ? `?${qs}` : ""}`, locale));
};

export const getService = (locale: string, slug: string) =>
  get<ServiceDetail>(`/services/${encodeURIComponent(slug)}/`, locale);

export const getServiceCategories = async (locale: string) =>
  listOf(await get<ServiceCategory[]>("/services/categories/", locale));

export const getPrices = async (locale: string) =>
  listOf(await get<PriceItem[]>("/services/prices/", locale));

export const getDoctors = async (locale: string, opts: { service?: string } = {}) =>
  listOf(
    await get<Paginated<Doctor>>(
      `/doctors/${opts.service ? `?service=${encodeURIComponent(opts.service)}` : ""}`,
      locale,
    ),
  );

export const getDoctor = (locale: string, slug: string) =>
  get<DoctorDetail>(`/doctors/${encodeURIComponent(slug)}/`, locale);

export const getReviews = async (locale: string, opts: { featured?: boolean } = {}) =>
  listOf(
    await get<Paginated<Review>>(`/reviews/${opts.featured ? "?featured=1" : ""}`, locale),
  );

export const getReviewSummary = (locale: string) =>
  get<{ average: number; total: number }>("/reviews/summary/", locale);

export const getCases = async (
  locale: string,
  opts: { featured?: boolean; service?: string } = {},
) => {
  const q = new URLSearchParams();
  if (opts.featured) q.set("featured", "1");
  if (opts.service) q.set("service", opts.service);
  const qs = q.toString();
  return listOf(await get<Paginated<CasePair>>(`/cases/${qs ? `?${qs}` : ""}`, locale));
};

export const getPosts = async (locale: string, opts: { q?: string } = {}) =>
  listOf(
    await get<Paginated<Post>>(`/posts/${opts.q ? `?q=${encodeURIComponent(opts.q)}` : ""}`, locale),
  );

export const getPost = (locale: string, slug: string) =>
  get<PostDetail>(`/posts/${encodeURIComponent(slug)}/`, locale);

export const getGallery = async (locale: string, opts: { category?: string } = {}) =>
  listOf(
    await get<Paginated<GalleryImage>>(
      `/gallery/${opts.category ? `?category=${encodeURIComponent(opts.category)}` : ""}`,
      locale,
    ),
  );

export const getStaticPage = (locale: string, key: string) =>
  get<StaticPage>(`/pages/${encodeURIComponent(key)}/`, locale);

export const getSeoRoutes = (locale: string) => get<SeoRoutes>("/seo/routes/", locale);

export const getFaqs = async (locale: string) =>
  listOf(await get<Paginated<Faq>>("/faq/", locale));

// ─────────────── Booking (Faza 2) ───────────────

const CLIENT_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type ApiSlot = {
  starts_at: string;
  start_utc: string;
  end: string;
  label: string;
  doctor_ids: number[];
};
export type ApiDay = {
  date: string;
  weekday: number;
  closed_reason: string;
  slots: ApiSlot[];
};
export type SlotsResponse = {
  timezone: string;
  duration_minutes: number | null;
  booking_enabled: boolean;
  reason: string;
  window: { from: string; to: string };
  days: ApiDay[];
};

export type Problem = {
  type: string;
  title: string;
  status: number;
  detail: string;
  code: string;
  errors?: Record<string, string[]>;
  available?: { days: ApiDay[] };
};

export type BookingResult = {
  ok: boolean;
  code: string;
  cancel_token: string;
  starts_at: string;
  ends_at: string;
  doctor: number | null;
  service: number | null;
  status: string;
  notified: boolean;
};

/** Client-side fetch (brauzerda ishlaydi — same-origin bo'lmasa CLIENT_BASE). */
async function clientFetch<T>(
  path: string,
  init: RequestInit = {},
  locale?: string,
): Promise<{ ok: true; data: T } | { ok: false; problem: Problem }> {
  const res = await fetch(`${CLIENT_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(locale ? { "Accept-Language": locale } : {}),
      ...(init.headers ?? {}),
    },
  });
  if (res.ok) return { ok: true, data: (await res.json()) as T };
  let problem: Problem;
  try {
    problem = (await res.json()) as Problem;
  } catch {
    problem = { type: "", title: "", status: res.status, detail: "", code: "server_error" };
  }
  return { ok: false, problem };
}

export async function fetchSlots(params: {
  service?: number | string;
  doctor?: number | string | null;
  date_from?: string;
  date_to?: string;
  exclude?: string;
  signal?: AbortSignal;
}): Promise<SlotsResponse | null> {
  const q = new URLSearchParams();
  if (params.service) q.set("service", String(params.service));
  if (params.doctor) q.set("doctor", String(params.doctor));
  if (params.date_from) q.set("date_from", params.date_from);
  if (params.date_to) q.set("date_to", params.date_to);
  if (params.exclude) q.set("exclude", params.exclude);
  try {
    const res = await fetch(`${CLIENT_BASE}/api/v1/appointments/slots/?${q}`, {
      signal: params.signal,
    });
    if (!res.ok) return null;
    return (await res.json()) as SlotsResponse;
  } catch {
    return null;
  }
}

export async function fetchFormToken(): Promise<string> {
  try {
    const res = await fetch(`${CLIENT_BASE}/api/v1/appointments/form-token/`);
    const data = await res.json();
    return data.form_token as string;
  } catch {
    return "";
  }
}

export function createBooking(body: Record<string, unknown>, idempotencyKey?: string) {
  return clientFetch<BookingResult>("/appointments/", {
    method: "POST",
    headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {},
    body: JSON.stringify(body),
  });
}

export function createLead(body: Record<string, unknown>) {
  return clientFetch<{ ok: boolean; notified: boolean; deduplicated?: boolean }>("/leads/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type PublicAppointment = {
  code: string;
  starts_at: string;
  ends_at: string;
  status: string;
  doctor_name: string | null;
  doctor_specialization: string | null;
  service_title: string | null;
  patient_name: string;
  can_cancel: boolean;
  can_reschedule: boolean;
};

export async function fetchAppointment(token: string, locale?: string): Promise<PublicAppointment | null> {
  const r = await clientFetch<PublicAppointment>(`/appointments/${token}/`, {}, locale);
  return r.ok ? r.data : null;
}

export function cancelAppointment(token: string, reason: string) {
  return clientFetch<{ ok: boolean; status: string }>(`/appointments/${token}/cancel/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function rescheduleAppointment(token: string, startsAt: string, locale?: string) {
  return clientFetch<PublicAppointment>(
    `/appointments/${token}/reschedule/`,
    { method: "POST", body: JSON.stringify({ starts_at: startsAt }) },
    locale,
  );
}
