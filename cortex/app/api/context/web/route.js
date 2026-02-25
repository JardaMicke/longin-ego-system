import { NextResponse } from "next/server";

const stripHtml = (html) => {
  if (!html) {
    return "";
  }
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<\/(nav|header|footer|aside)>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
};

export async function POST(request) {
  try {
    const body = await request.json();
    if (!body?.url) {
      return NextResponse.json({ error: "URL chybí." }, { status: 400 });
    }
    const response = await fetch(body.url, { redirect: "follow" });
    if (!response.ok) {
      return NextResponse.json({ error: "Web není dostupný." }, { status: 400 });
    }
    const html = await response.text();
    const preview = stripHtml(html).slice(0, 400);
    return NextResponse.json({ ok: true, preview });
  } catch (error) {
    return NextResponse.json({ error: "Web se nepodařilo zpracovat." }, { status: 500 });
  }
}
