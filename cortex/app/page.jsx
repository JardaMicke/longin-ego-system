"use client";

import { useCallback, useEffect, useState } from "react";
import { Puck } from "@measured/puck";
import "@measured/puck/puck.css";
import { puckConfig } from "../lib/puckConfig";

const fallbackData = { content: [], root: { props: {} } };

export default function Home() {
  const [data, setData] = useState(fallbackData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch("/api/puck?path=/");
        if (!response.ok) {
          throw new Error(`Load failed: ${response.status}`);
        }
        const payload = await response.json();
        if (active && payload?.data) {
          setData(payload.data);
        }
      } catch (err) {
        if (active) {
          setError(String(err));
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      active = false;
    };
  }, []);

  const handlePublish = useCallback(async (nextData) => {
    const response = await fetch("/api/puck", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: "/", data: nextData })
    });
    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }
  }, []);

  if (loading) {
    return <div>Načítání...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return <Puck config={puckConfig} data={data} onPublish={handlePublish} />;
}
