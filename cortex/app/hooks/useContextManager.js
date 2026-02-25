import { useCallback, useMemo, useRef, useState } from "react";

export const useContextManager = () => {
  const [items, setItems] = useState([]);
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState(() => {
    if (typeof window === "undefined") {
      return {};
    }
    const stored = window.localStorage.getItem("contextMetrics");
    return stored ? JSON.parse(stored) : {};
  });
  const [undoState, setUndoState] = useState(null);
  const [cancelSummary, setCancelSummary] = useState(null);
  const operationsRef = useRef(new Map());
  const retryHandlersRef = useRef(new Map());

  const persistMetrics = useCallback((next) => {
    setMetrics(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("contextMetrics", JSON.stringify(next));
    }
  }, []);

  const addLog = useCallback((level, message, details = {}) => {
    setLogs((prev) => [
      {
        id: crypto.randomUUID(),
        level,
        message,
        details,
        timestamp: new Date().toISOString()
      },
      ...prev
    ]);
  }, []);

  const recordMetric = useCallback(
    (action, status) => {
      persistMetrics((prev) => {
        const current = prev[action] ?? { success: 0, failure: 0, cancelled: 0 };
        const next = {
          ...prev,
          [action]: { ...current, [status]: (current[status] ?? 0) + 1 }
        };
        return next;
      });
    },
    [persistMetrics]
  );

  const createItem = useCallback((item) => {
    const id = crypto.randomUUID();
    setItems((prev) => [
      {
        id,
        status: "pending",
        progress: 0,
        createdAt: new Date().toISOString(),
        ...item
      },
      ...prev
    ]);
    return id;
  }, []);

  const updateItem = useCallback((id, updates) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...updates } : item))
    );
  }, []);

  const removeItem = useCallback((id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
    retryHandlersRef.current.delete(id);
    operationsRef.current.delete(id);
  }, []);

  const registerOperation = useCallback((id, controller) => {
    operationsRef.current.set(id, controller);
  }, []);

  const registerRetry = useCallback((id, handler) => {
    retryHandlersRef.current.set(id, handler);
  }, []);

  const retryItem = useCallback(
    async (id) => {
      const handler = retryHandlersRef.current.get(id);
      if (!handler) {
        return;
      }
      await handler();
    },
    []
  );

  const removeLastWithUndo = useCallback(() => {
    setItems((prev) => {
      if (!prev.length) {
        return prev;
      }
      const [removed, ...rest] = prev;
      setUndoState({ item: removed, expiresAt: Date.now() + 10000 });
      return rest;
    });
  }, []);

  const undoRemove = useCallback(() => {
    if (!undoState?.item) {
      return;
    }
    setItems((prev) => [undoState.item, ...prev]);
    setUndoState(null);
  }, [undoState]);

  const clearUndo = useCallback(() => setUndoState(null), []);

  const stopAllOperations = useCallback(() => {
    const cancelled = [];
    operationsRef.current.forEach((controller, id) => {
      try {
        controller.abort();
        cancelled.push(id);
      } catch (error) {
        addLog("error", "Nepodařilo se zrušit operaci.", { id, error: String(error) });
      }
    });
    operationsRef.current.clear();
    setItems((prev) =>
      prev.map((item) =>
        cancelled.includes(item.id)
          ? { ...item, status: "cancelled", error: "Operace byla zrušena." }
          : item
      )
    );
    setCancelSummary({
      cancelled,
      timestamp: new Date().toISOString()
    });
  }, [addLog]);

  const totalCount = useMemo(() => items.length, [items.length]);

  return {
    items,
    logs,
    metrics,
    undoState,
    cancelSummary,
    totalCount,
    addLog,
    recordMetric,
    createItem,
    updateItem,
    removeItem,
    removeLastWithUndo,
    undoRemove,
    clearUndo,
    registerOperation,
    registerRetry,
    retryItem,
    stopAllOperations,
    setCancelSummary
  };
};
