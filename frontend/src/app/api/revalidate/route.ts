import { revalidatePath } from "next/cache";
import { NextResponse } from "next/server";
import { timingSafeEqual } from "node:crypto";

/**
 * On-demand ISR purge — `manage.py reskin` va `make warm` shu yerni chaqiradi.
 *
 * Nega kerak: barcha server fetch'lar `next: { revalidate: 300 }` bilan keshlanadi
 * (lib/api.ts), shuning uchun reskin'dan keyin sayt 5 daqiqagacha ESKI brend bilan
 * qolardi — jonli demoda "reskin → sahifani yangilang" qadami shu sababli yiqilardi
 * (AUDIT-2026-08-29 / T-FIX-02).
 *
 * Xavfsizlik: `REVALIDATE_SECRET` boʻlmasa endpoint YOPIQ (503) — fail-closed, chunki
 * himoyasiz purge endpoint'i arzon DoS vektori. Sir `x-revalidate-secret` header'ida.
 * `/api/*` proxy matcher'idan tashqarida (src/proxy.ts), shuning uchun locale rewrite boʻlmaydi.
 */
export const dynamic = "force-dynamic";

function safeEqual(given: string, expected: string): boolean {
  const a = Buffer.from(given);
  const b = Buffer.from(expected);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}

export async function POST(request: Request) {
  const secret = process.env.REVALIDATE_SECRET;
  if (!secret) {
    return NextResponse.json(
      { ok: false, error: "revalidate_disabled", detail: "REVALIDATE_SECRET oʻrnatilmagan" },
      { status: 503 },
    );
  }
  if (!safeEqual(request.headers.get("x-revalidate-secret") ?? "", secret)) {
    return NextResponse.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  // '/' + 'layout' — ildiz layout'i ostidagi BARCHA yoʻllarni bekor qiladi (uch til ham).
  revalidatePath("/", "layout");
  return NextResponse.json({ ok: true, scope: "layout", path: "/" });
}
