"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { CourseCard } from "@/components/course-card";
import { sendChatMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ChatAction, ChatSource, Course } from "@/types";
import { SendHorizonal } from "lucide-react";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  courses?: Course[];
  actions?: ChatAction[];
}

const WELCOME: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "안녕하세요! 학교 정보, 수강신청, 시간표, 강의실, 상담 관련해서 무엇이든 물어보세요.\n예: \"지금 신청 가능한 온라인 교양 알려줘\"",
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const idRef = useRef(0);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    idRef.current += 1;
    const userMessage: ChatMessage = { id: `u-${idRef.current}`, role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const response = await sendChatMessage(text);

    idRef.current += 1;
    setMessages((prev) => [
      ...prev,
      {
        id: `a-${idRef.current}`,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        courses: response.courses,
        actions: response.actions,
      },
    ]);
    setLoading(false);
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-6.5rem)] max-w-2xl flex-col gap-4 md:h-[calc(100vh-3.5rem)]">
      <ScrollArea className="flex-1 rounded-lg border border-border">
        <div className="flex flex-col gap-4 p-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn("flex flex-col gap-2", message.role === "user" ? "items-end" : "items-start")}
            >
              <div
                className={cn(
                  "max-w-[85%] whitespace-pre-line rounded-xl px-3 py-2 text-sm",
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground"
                )}
              >
                {message.content}
              </div>

              {message.sources && message.sources.length > 0 && (
                <div className="max-w-[85%] space-y-1">
                  {message.sources.map((source) => (
                    <a
                      key={source.url}
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block text-xs text-muted-foreground hover:underline"
                    >
                      출처: {source.title}
                    </a>
                  ))}
                </div>
              )}

              {message.courses && message.courses.length > 0 && (
                <div className="grid w-full max-w-[85%] gap-2">
                  {message.courses.map((course) => (
                    <CourseCard key={course.id} course={course} />
                  ))}
                </div>
              )}

              {message.actions && message.actions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {message.actions.map((action, i) => (
                    <Button key={i} size="sm" variant="outline" render={<Link href="/courses" />}>
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <Card className="max-w-[60%]">
              <CardContent className="py-2">
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          )}
        </div>
      </ScrollArea>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="무엇이든 물어보세요"
          disabled={loading}
        />
        <Button type="submit" size="icon" disabled={loading || !input.trim()}>
          <SendHorizonal className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
