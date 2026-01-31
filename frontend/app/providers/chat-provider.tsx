// frontend/src/providers/chat-provider.tsx
"use client";

/**
 * ChatProvider
 *
 * このファイルは、ai-workbench Frontend における
 * 「チャット状態とバックエンド連携」を一元管理する Provider である。
 *
 * この層の役割:
 * - UI を一切持たない
 * - Chat / Snapshot / Diff / 実行状態を保持する
 * - Backend API を呼び出す唯一の窓口になる
 *
 * やってはいけないこと:
 * - UI 表示
 * - 文体・表現の決定
 * - Snapshot の意味解釈
 * - Diff の適用
 *
 * この Provider は
 * 「状態と操作の契約書」であり、
 * 「画面」ではない。
 */

import React, { createContext, useContext, useReducer, ReactNode } from "react";

/* =========================================================
 * Domain Types（Backend と対応）
 * ======================================================= */

/**
 * SnapshotFile
 * Backend domain/snapshot.py と 1:1 対応
 */
export type SnapshotFile = {
  path: string;
  content: string;
};

/**
 * Snapshot
 */
export type Snapshot = {
  project_id: string;
  files: SnapshotFile[];
};

/**
 * DiffFile
 */
export type DiffFile = {
  path: string;
  before: string;
  after: string;
};

/**
 * Diff
 */
export type Diff = {
  project_id: string;
  files: DiffFile[];
};

/* =========================================================
 * State 定義
 * ======================================================= */

/**
 * ChatState
 *
 * Provider が保持する全状態。
 * UI はこの構造を「読むだけ」。
 */
export type ChatState = {
  /** 現在の Snapshot（未生成の場合 null） */
  snapshot: Snapshot | null;

  /** 最新の Diff（未生成の場合 null） */
  diff: Diff | null;

  /** 処理中フラグ（Backend 呼び出し中） */
  isLoading: boolean;

  /** エラーメッセージ（発生時のみ） */
  error: string | null;
};

/**
 * 初期状態
 */
const initialState: ChatState = {
  snapshot: null,
  diff: null,
  isLoading: false,
  error: null,
};

/* =========================================================
 * Action 定義
 * ======================================================= */

/**
 * ChatAction
 *
 * 状態遷移は必ず Action を経由する。
 * 暗黙の setState は禁止。
 */
type ChatAction =
  | { type: "SET_SNAPSHOT"; snapshot: Snapshot }
  | { type: "REQUEST_START" }
  | { type: "REQUEST_SUCCESS"; diff: Diff }
  | { type: "REQUEST_ERROR"; error: string }
  | { type: "RESET" };

/* =========================================================
 * Reducer
 * ======================================================= */

/**
 * chatReducer
 *
 * 状態遷移の唯一の定義点。
 * ここを読めば、全フローが把握できる。
 */
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "SET_SNAPSHOT":
      return {
        ...state,
        snapshot: action.snapshot,
      };

    case "REQUEST_START":
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case "REQUEST_SUCCESS":
      return {
        ...state,
        isLoading: false,
        diff: action.diff,
      };

    case "REQUEST_ERROR":
      return {
        ...state,
        isLoading: false,
        error: action.error,
      };

    case "RESET":
      return initialState;

    default:
      return state;
  }
}

/* =========================================================
 * Context 定義
 * ======================================================= */

type ChatContextValue = {
  state: ChatState;

  /**
   * Snapshot を外部からセットする
   * （Workspace Scan → SnapshotBuilder 結果を想定）
   */
  setSnapshot: (snapshot: Snapshot) => void;

  /**
   * Backend /chat を呼び出す
   */
  runChat: (mode?: string) => Promise<void>;

  /**
   * 状態を完全リセットする
   */
  reset: () => void;
};

const ChatContext = createContext<ChatContextValue | null>(null);

/* =========================================================
 * Provider 実装
 * ======================================================= */

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  /* -----------------------------
   * Actions
   * --------------------------- */

  const setSnapshot = (snapshot: Snapshot) => {
    dispatch({ type: "SET_SNAPSHOT", snapshot });
  };

  const reset = () => {
    dispatch({ type: "RESET" });
  };

  /**
   * Backend /chat 呼び出し
   *
   * 注意:
   * - Snapshot が無い場合は何もしない
   * - Diff の解釈はしない
   */
  const runChat = async (mode?: string) => {
    if (!state.snapshot) {
      dispatch({
        type: "REQUEST_ERROR",
        error: "Snapshot is not set",
      });
      return;
    }

    dispatch({ type: "REQUEST_START" });

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          snapshot: state.snapshot,
          mode,
          existing_diff: state.diff,
        }),
      });

      if (!res.ok) {
        throw new Error(`Chat API failed: ${res.status}`);
      }

      const data = await res.json();

      dispatch({
        type: "REQUEST_SUCCESS",
        diff: data.diff,
      });
    } catch (err) {
      dispatch({
        type: "REQUEST_ERROR",
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  /* -----------------------------
   * Context 提供
   * --------------------------- */

  return (
    <ChatContext.Provider
      value={{
        state,
        setSnapshot,
        runChat,
        reset,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

/* =========================================================
 * Hook
 * ======================================================= */

/**
 * useChat
 *
 * Provider の値を安全に取得するための Hook。
 */
export function useChat(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChat must be used within ChatProvider");
  }
  return ctx;
}
