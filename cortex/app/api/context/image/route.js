import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || typeof file === "string") {
      return NextResponse.json({ error: "Obrázek chybí." }, { status: 400 });
    }
    const altText = formData.get("altText");
    return NextResponse.json({
      ok: true,
      name: file.name,
      size: file.size,
      altText: typeof altText === "string" ? altText : ""
    });
  } catch (error) {
    return NextResponse.json({ error: "Obrázek se nepodařilo zpracovat." }, { status: 500 });
  }
}
