import { useEffect, useState } from "react";

export function useMediaQuery(query: string) {
  const [matched, setMatched] = useState(false);

  useEffect(() => {
    const listener = (event: MediaQueryListEvent) => {
      setMatched(event.matches);
    };

    const mql = window.matchMedia(query);
    setMatched(mql.matches);

    mql.addEventListener("change", listener);

    return () => {
      mql.removeEventListener("change", listener);
    };
  }, [query]);

  return matched;
}
