// app/api/workspace/scan/route.ts
/**
 * Workspace Scan API (Frontend Proxy)
 *
 * この route.ts は、
 * Frontend からの /api/workspace/scan リクエストを受け取り、
 * Python Backend の /workspace/scan に中継する。
 *
 * 役割:
 * - Client から Backend を直接叩かせない
 * - Backend URL / 認証 / 将来の差異を吸収する
 * - Frontend 側 API の「正規入口」になる
 *
 * やってはいけないこと:
 * - WorkspaceIndex の解釈
 * - Snapshot の生成
 * - UI 用の整形
 *
 * この層は
 * 「HTTP の翻訳機」であり、
 * 「意味の理解者」ではない。
 */

import { NextResponse } from "next/server";

/**
 * POST /api/workspace/scan
 */
export async function POST(req: Request) {
  try {
    // ----------------------------------------
    // リクエストボディ取得
    // ----------------------------------------
    const body = await req.json();

    // ----------------------------------------
    // Backend URL 解決
    // ----------------------------------------
    const backendBaseUrl = process.env.BACKEND_BASE_URL;

    if (!backendBaseUrl) {
      return NextResponse.json(
        { error: "BACKEND_BASE_URL is not configured" },
        { status: 500 },
      );
    }

    // ----------------------------------------
    // Backend へ中継
    // ----------------------------------------
    const backendRes = await fetch(`${backendBaseUrl}/workspace/scan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      // ※ Cookie / Auth を載せるならここ
    });

    // ----------------------------------------
    // Backend エラー透過
    // ----------------------------------------
    if (!backendRes.ok) {
      const text = await backendRes.text();
      return NextResponse.json(
        {
          error: "Backend workspace scan failed",
          detail: text,
        },
        { status: backendRes.status },
      );
    }

    // ----------------------------------------
    // 正常レスポンスをそのまま返却
    // ----------------------------------------
    const data = await backendRes.json();

    return NextResponse.json(data);
  } catch (err) {
    // ----------------------------------------
    // 想定外エラー
    // ----------------------------------------
    console.error("[api/workspace/scan] error:", err);

    return NextResponse.json(
      { error: "Unexpected error in workspace scan proxy" },
      { status: 500 },
    );
  }
}
