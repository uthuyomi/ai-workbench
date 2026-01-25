"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import clsx from "clsx";
import { supabase } from "@/lib/supabase/client";
import { useTranslations } from "next-intl";

type Chat = {
  id: string;
  label: string;
};

type UserInfo = {
  name: string;
  avatarUrl: string | null;
  provider: string | null;
};

export function Sidebar() {
  const t = useTranslations("chat");

  const initialChats: Chat[] = [
    { id: "chat-1", label: t("chat1") },
    { id: "chat-2", label: t("chat2") },
    { id: "chat-3", label: t("chat3") },
  ];

  const [chats, setChats] = useState(initialChats);
  const [activeId, setActiveId] = useState("chat-1");
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);
  const [user, setUser] = useState<UserInfo | null>(null);

  /* =====================
     Auth: get user
     ===================== */
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      const u = data.session?.user;
      if (!u) return;

      setUser({
        name: u.user_metadata?.name ?? u.email ?? t("defaultUser"),
        avatarUrl: u.user_metadata?.avatar_url ?? null,
        provider: u.app_metadata?.provider ?? null,
      });
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) setUser(null);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [t]);

  const signOut = async () => {
    await supabase.auth.signOut();
    location.href = "/login";
  };

  /* =====================
     Chat actions
     ===================== */
  const renameChat = (id: string) => {
    const label = prompt(t("renameChatPrompt"));
    if (!label) return;

    setChats((prev) => prev.map((c) => (c.id === id ? { ...c, label } : c)));
    setMenuOpenId(null);
  };

  const deleteChat = (id: string) => {
    if (!confirm(t("deleteChatConfirm"))) return;

    setChats((prev) => prev.filter((c) => c.id !== id));
    setMenuOpenId(null);

    if (activeId === id && chats.length > 1) {
      setActiveId(chats[0].id);
    }
  };

  return (
    <aside className="h-full flex flex-col bg-[var(--bg-side)] px-3 py-4">
      {/* New Chat */}
      <button
        className="
          mb-4
          w-full
          rounded-xl
          bg-[var(--bg-card)]
          px-4 py-2.5
          text-sm
          text-[var(--foreground)]
          shadow-[0_4px_12px_rgba(0,0,0,0.25)]
          hover:opacity-90
        "
      >
        {t("newChat")}
      </button>

      {/* Chat list */}
      <div className="flex flex-col gap-1">
        {chats.map((chat) => {
          const active = chat.id === activeId;
          const menuOpen = chat.id === menuOpenId;

          return (
            <div
              key={chat.id}
              onClick={() => setActiveId(chat.id)}
              className={clsx(
                `
                  group relative flex items-center
                  rounded-xl px-4 py-2.5
                  text-sm cursor-pointer transition
                `,
                active
                  ? `
                      bg-[var(--bg-card)]
                      text-[var(--foreground)]
                      shadow-[0_4px_12px_rgba(0,0,0,0.25)]
                    `
                  : `
                      text-[var(--text-muted)]
                      hover:bg-[var(--bg-hover)]
                    `,
              )}
            >
              <span className="flex-1 truncate">{chat.label}</span>

              {/* Kebab */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpenId(menuOpen ? null : chat.id);
                }}
                className="
                  ml-2 rounded-md px-1.5 py-1
                  text-[var(--text-faint)]
                  opacity-0 group-hover:opacity-100
                  hover:bg-[var(--bg-hover)]
                "
              >
                ⋮
              </button>

              {menuOpen && (
                <div
                  className="
                    absolute right-2 top-full mt-1
                    w-28 rounded-xl
                    bg-[var(--bg-card)]
                    shadow-[0_6px_20px_rgba(0,0,0,0.35)]
                    overflow-hidden z-50
                  "
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      renameChat(chat.id);
                    }}
                    className="
                      w-full px-3 py-2 text-left text-sm
                      text-[var(--foreground)]
                      hover:bg-[var(--bg-hover)]
                    "
                  >
                    {t("rename")}
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteChat(chat.id);
                    }}
                    className="
                      w-full px-3 py-2 text-left text-sm
                      text-[var(--text-muted)]
                      hover:bg-[var(--bg-hover)]
                    "
                  >
                    {t("delete")}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex-1" />

      {/* =====================
          Logged-in User Panel
          ===================== */}
      {user && (
        <div
          className="
            mt-4 rounded-xl
            bg-[var(--bg-card)]
            px-3 py-3
            text-sm
            shadow-[0_4px_12px_rgba(0,0,0,0.25)]
          "
        >
          <div className="flex items-center gap-3">
            {user.avatarUrl ? (
              <Image
                src={user.avatarUrl}
                alt="Avatar"
                width={36}
                height={36}
                className="rounded-full"
              />
            ) : (
              <div className="h-9 w-9 rounded-full bg-[var(--bg-hover)]" />
            )}

            <div className="min-w-0">
              <div className="truncate text-[var(--foreground)]">
                {user.name}
              </div>
              <div className="text-xs text-[var(--text-faint)]">
                {user.provider}
              </div>
            </div>
          </div>

          {/* Settings */}
          <Link
            href="/setting"
            className="
              mt-3 block w-full
              rounded-lg
              bg-[var(--bg-hover)]
              px-3 py-2
              text-center text-xs
              text-[var(--foreground)]
              hover:opacity-90
            "
          >
            {t("settings")}
          </Link>

          {/* Logout */}
          <button
            onClick={signOut}
            className="
              mt-2 w-full
              rounded-lg
              bg-[var(--bg-hover)]
              px-3 py-2
              text-xs
              text-[var(--foreground)]
              hover:opacity-90
            "
          >
            {t("logout")}
          </button>
        </div>
      )}
    </aside>
  );
}
