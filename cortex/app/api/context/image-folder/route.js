import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const files = formData.getAll("files").filter((file) => typeof file !== "string");
    if (!files.length) {
      return NextResponse.json({ error: "Obrázky chybí." }, { status: 400 });
    }
    let ok = 0;
    let failed = 0;
    files.forEach((file) => {
      if (file.size > 0) {
        ok += 1;
      } else {
        failed += 1;
      }
    });
    return NextResponse.json({ ok, failed, backup: true });
  } catch (error) {
    return NextResponse.json({ error: "Složku obrázků se nepodařilo zpracovat." }, { status: 500 });
  }
}
