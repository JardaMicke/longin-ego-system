import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || typeof file === "string") {
      return NextResponse.json({ error: "Nahrávka chybí." }, { status: 400 });
    }
    const transcript = formData.get("transcript");
    return NextResponse.json({
      ok: true,
      name: file.name,
      size: file.size,
      transcript: typeof transcript === "string" ? transcript : ""
    });
  } catch (error) {
    return NextResponse.json({ error: "Nahrávku se nepodařilo zpracovat." }, { status: 500 });
  }
}
