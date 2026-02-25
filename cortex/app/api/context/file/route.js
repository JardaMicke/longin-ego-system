import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || typeof file === "string") {
      return NextResponse.json({ error: "Soubor chybí." }, { status: 400 });
    }
    return NextResponse.json({ ok: true, name: file.name, size: file.size });
  } catch (error) {
    return NextResponse.json({ error: "Soubor se nepodařilo zpracovat." }, { status: 500 });
  }
}
