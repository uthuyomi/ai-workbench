// app/api/chat/snapshot/route.ts
/**
 * Chat Snapshot API (Frontend Proxy)
 *
 * この route.ts は、
 * Frontend からの /api/chat/snapshot リクエストを受け取り、
 * Python Backend の /chat エンドポイントへ中継する。
 *
 * 役割:
 * - Client から Backend を直接叩かせない
 * - Snapshot をそのまま Backend Workflow に渡す
 * - Backend URL / 認証 / 将来変更を吸収する
 *
 * やってはいけないこと:
 * - Snapshot の解釈
 * - Diff の加工
 * - mode の意味理解
 * - Workflow / DevEngine を意識した分岐
 *
 * この層は
 * 「HTTP の翻訳機」であり、
 * 「思考の関与者」ではない。
 */

import { NextResponse } from "next/server";

/**
 * POST /api/chat/snapshot
 *
 * Frontend から Snapshot + mode 等を受け取り、
 * Backend /chat にそのまま転送する。
 */
export async function POST(req: Request) {
  try {
    /* ----------------------------------------
     * リクエストボディ取得
     * -------------------------------------- */
    const body = await req.json();

    /**
     * 期待される body 構造（例）:
     *
     * {
     *   snapshot: {
     *     project_id: string,
     *     files: [{ path: string, content: string }]
     *   },
     *   mode?: "dev" | "casual",
     *   existing_diff?: Diff
     * }
     *
     * ※ ここでは検証しない
     * ※ Backend 側が正規契約点
     */

    /* ----------------------------------------
     * Backend URL 解決
     * -------------------------------------- */
    const backendBaseUrl = process.env.BACKEND_BASE_URL;

    if (!backendBaseUrl) {
      return NextResponse.json(
        { error: "BACKEND_BASE_URL is not configured" },
        { status: 500 },
      );
    }

    /* ----------------------------------------
     * Backend /chat へ中継
     * -------------------------------------- */
    const backendRes = await fetch(`${backendBaseUrl}/chat/snapshot`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      /**
       * 注意:
       * - Cookie / Auth を載せるならここ
       * - この層では追加ロジックを持たない
       */
    });

    /* ----------------------------------------
     * Backend エラー透過
     * -------------------------------------- */
    if (!backendRes.ok) {
      const text = await backendRes.text();

      return NextResponse.json(
        {
          error: "Backend chat(snapshot) failed",
          detail: text,
        },
        { status: backendRes.status },
      );
    }

    /* ----------------------------------------
     * 正常レスポンス透過
     * -------------------------------------- */
    const data = await backendRes.json();

    return NextResponse.json(data);
  } catch (err) {
    /* ----------------------------------------
     * 想定外エラー
     * -------------------------------------- */
    console.error("[api/chat/snapshot] error:", err);

    return NextResponse.json(
      { error: "Unexpected error in chat snapshot proxy" },
      { status: 500 },
    );
  }
}

/* ============================================================
 * 使用上の注意（設計固定）
 * ============================================================
 *
 * - この route.ts は Snapshot を「読む」だけ
 * - Snapshot を「作らない」「直さない」
 * - Workflow / DevEngine の存在を知らない
 *
 * app/api/chat/snapshot は
 * 「実行スイッチ」であって
 * 「思考装置」ではない。
 */
