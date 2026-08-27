import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  // API, _next, statik fayllar va Next ichki yoʻllaridan tashqari hammasi.
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
