import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const body = await request.json();
    if (!body?.url) {
      return NextResponse.json({ error: "URL chybí." }, { status: 400 });
    }
    return NextResponse.json({
      ok: true,
      provider: body.provider ?? "",
      owner: body.owner ?? "",
      repo: body.repo ?? "",
      branch: body.branch ?? ""
    });
  } catch (error) {
    return NextResponse.json({ error: "Repozitář se nepodařilo zpracovat." }, { status: 500 });
  }
}
