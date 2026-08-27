import { createNavigation } from "next-intl/navigation";
import { routing } from "./routing";

// Locale'ni saqlaydigan Link / router (til almashtirgich shundan foydalanadi).
export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
