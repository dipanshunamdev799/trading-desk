/** One request at a time, aligned to minute boundaries, with visibility-aware refresh. */
export function startMinutePolling<T>({
  load, onData, onError, onLoading, live, visibility = document,
}: {
  load: () => Promise<T>;
  onData: (data: T) => void;
  onError: (error: unknown) => void;
  onLoading: (loading: boolean) => void;
  live: boolean;
  visibility?: Pick<Document, "visibilityState" | "addEventListener" | "removeEventListener">;
}): () => void {
  let stopped = false;
  let inFlight = false;
  let timer: ReturnType<typeof setTimeout> | undefined;

  async function refresh() {
    if (stopped || inFlight) return;
    inFlight = true;
    onLoading(true);
    try {
      const data = await load();
      if (!stopped) onData(data);
    } catch (error) {
      if (!stopped) onError(error);
    } finally {
      inFlight = false;
      if (!stopped) onLoading(false);
    }
  }

  function schedule() {
    timer = setTimeout(() => {
      if (stopped) return;
      if (visibility.visibilityState === "visible") void refresh();
      schedule();
    }, 60_000 - (Date.now() % 60_000));
  }

  function onVisibility() {
    if (visibility.visibilityState === "visible") void refresh();
  }

  void refresh();
  if (live) {
    schedule();
    visibility.addEventListener("visibilitychange", onVisibility);
  }
  return () => {
    stopped = true;
    clearTimeout(timer);
    visibility.removeEventListener("visibilitychange", onVisibility);
  };
}
