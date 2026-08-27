"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type Hrefs = Record<string, string> | null;
const Ctx = createContext<{ hrefs: Hrefs; set: (h: Hrefs) => void }>({
  hrefs: null,
  set: () => {},
});

/** Til almashtirgich uchun joriy sahifaning har-locale URL'larini saqlaydi. */
export function LocaleAlternatesProvider({ children }: { children: ReactNode }) {
  const [hrefs, set] = useState<Hrefs>(null);
  return <Ctx.Provider value={{ hrefs, set }}>{children}</Ctx.Provider>;
}

export function useLocaleAlternates() {
  return useContext(Ctx);
}

/** Detail sahifalar buni render qiladi — server hisoblagan hrefs'ni kontekstga qoʻyadi. */
export function SetLocaleHrefs({ hrefs }: { hrefs: Record<string, string> }) {
  const { set } = useLocaleAlternates();
  const key = JSON.stringify(hrefs);
  useEffect(() => {
    set(hrefs);
    return () => set(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return null;
}
