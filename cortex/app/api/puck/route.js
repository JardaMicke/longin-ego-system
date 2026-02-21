import { NextResponse } from "next/server";
import { getLayout, saveLayout } from "../../../lib/db";

function normalizeProject(value) {
  if (!value || typeof value !== "string") {
    return "default";
  }
  return value;
}

export async function GET(request) {
  try {
    const url = new URL(request.url);
    const projectId = normalizeProject(url.searchParams.get("project") || url.searchParams.get("path"));
    const result = await getLayout(projectId);
    return NextResponse.json({
      projectId,
      data: result?.data ?? null,
      version: result?.version ?? null
    });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request) {
  try {
    const payload = await request.json();
    const projectId = normalizeProject(payload.projectId || payload.project || payload.path);
    const data = payload.data;
    if (!data) {
      return NextResponse.json({ error: "Layout data is required" }, { status: 400 });
    }
    const version = await saveLayout(projectId, data);
    return NextResponse.json({ status: "saved", projectId, version });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
