import { type RefObject, useEffect, useRef } from "react";

export function useInfiniteScroll(
  triggerRef: RefObject<HTMLElement | null>,
  callback: () => void,
) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    const trigger = triggerRef.current;

    if (!trigger) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          callbackRef.current();
        }
      },
      { rootMargin: "200px" },
    );

    observer.observe(trigger);

    return () => {
      observer.unobserve(trigger);
    };
  }, [triggerRef]);
}
