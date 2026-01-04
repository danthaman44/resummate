"use client";

import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import { useChat, type UIMessage } from "@ai-sdk/react";
import { toast } from "sonner";
import React, { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { Spinner } from "@/components/ui/spinner"

export function Chat() {
  const params = useParams();
  const uuid = params?.uuid as string;
  const chatId = uuid || "001";

  const [initialMessages, setInitialMessages] = useState<UIMessage[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  useEffect(() => {
      // Use setTimeout to avoid synchronous setState in effect
      const timeoutId = setTimeout(() => {
        setIsLoadingHistory(true);
        setInitialMessages([]);
      }, 0);
      
      fetch(`/api/chat/history/${chatId}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch chat history');
          return res.json();
        })
        .then(data => {
          setInitialMessages(data.messages || []);
          setIsLoadingHistory(false);
        })
        .catch(error => {
          toast.error('Failed to load chat history');
          setIsLoadingHistory(false);
        });
      
      return () => clearTimeout(timeoutId);
  }, [chatId]);

  const { messages, setMessages, sendMessage, status, stop } = useChat({
    id: chatId,
    messages: initialMessages,
    onError: (error: Error) => {
      if (error.message.includes("Too many requests")) {
        toast.error(
          "You are sending too many messages. Please try again later."
        );
      }
    },
  });

  useEffect(() => {
    if (!isLoadingHistory && initialMessages.length > 0 && messages.length === 0) {
      setMessages(initialMessages)
    }
  }, [isLoadingHistory, initialMessages, messages.length, setMessages])

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();

  const [input, setInput] = React.useState("");

  const isLoading = status === "submitted" || status === "streaming";

  const handleSubmit = (event?: { preventDefault?: () => void }) => {
    event?.preventDefault?.();
    if (input.trim()) {
      sendMessage(
        { text: input },
        {
          body: {
            id: chatId,
          },
        }
      );
      setInput("");
    }
  };

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner className="h-8 w-8 mx-auto" />
          <p className="mt-4 text-sm text-muted-foreground">Loading chat history...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-background">
      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4"
      >

      {messages.length === 0 && <Overview />}

      {messages.map((message: UIMessage, index: number) => (
        <PreviewMessage
          key={message.id}
          chatId={chatId}
          message={message}
          isLoading={isLoading && messages.length - 1 === index}
        />
      ))}

      {isLoading &&
        messages.length > 0 &&
        messages[messages.length - 1].role === "user" && <ThinkingMessage />}

        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          stop={stop}
          messages={messages}
          setMessages={setMessages}
          sendMessage={sendMessage}
          status={status}
        />
      </form>
    </div>
  );
}
