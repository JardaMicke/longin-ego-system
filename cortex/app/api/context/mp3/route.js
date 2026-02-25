import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || typeof file === "string") {
      return NextResponse.json({ error: "MP3 chybí." }, { status: 400 });
    }
    const note = formData.get("note");
    return NextResponse.json({
      ok: true,
      name: file.name,
      size: file.size,
      note: typeof note === "string" ? note : ""
    });
  } catch (error) {
    return NextResponse.json({ error: "MP3 se nepodařilo zpracovat." }, { status: 500 });
  }
}
