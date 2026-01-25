"use client";

import { Sidebar } from "@/components/chat/sidebar";
import { Header } from "@/components/chat/header";
import { ChatPanel } from "@/components/chat/chat";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ActionPanel } from "@/components/chat/action-panel";

export function AppShell() {
  return (
    <div
      className="
        h-screen w-screen
        bg-[var(--background)]
        text-[var(--foreground)]
        overflow-hidden
      "
    >
      <div className="h-full grid grid-cols-[260px_1fr_360px]">
        {/* Sidebar */}
        <Sidebar />

        {/* Center column */}
        <section
          className="
            relative
            flex flex-col
            min-h-0
            bg-[var(--background)]
          "
        >
          {/* Header */}
          <div
            className="
              sticky top-0
              z-30
              bg-[var(--background)]
            "
          >
            <Header />
          </div>

          {/* Chat area */}
          <div className="flex-1 min-h-0 flex flex-col">
            <ChatPanel />
            <ChatComposer />
          </div>
        </section>

        {/* Action panel */}
        <ActionPanel />
      </div>
    </div>
  );
}
