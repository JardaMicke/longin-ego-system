import { NextResponse } from "next/server";
import { getLayout, saveLayout } from "../../../lib/db";

function normalizePath(path) {
  if (!path || typeof path !== "string") {
    return "/";
  }
  return path;
}

export async function GET(request) {
  try {
    const url = new URL(request.url);
    const path = normalizePath(url.searchParams.get("path"));
    const data = await getLayout(path);
    return NextResponse.json({ path, data });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request) {
  try {
    const payload = await request.json();
    const path = normalizePath(payload.path);
    const data = payload.data ?? null;
    await saveLayout(path, data);
    return NextResponse.json({ status: "saved", path });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
