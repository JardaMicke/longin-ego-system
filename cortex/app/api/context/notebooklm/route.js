import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const body = await request.json();
    if (!body?.url) {
      return NextResponse.json({ error: "URL chybí." }, { status: 400 });
    }
    return NextResponse.json({ ok: true, url: body.url, note: body.note ?? "" });
  } catch (error) {
    return NextResponse.json({ error: "NotebookLM se nepodařilo zpracovat." }, { status: 500 });
  }
}
