import { UIMessage } from "@ai-sdk/react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function sanitizeUIMessages(
  messages: Array<UIMessage>
): Array<UIMessage> {
  const messagesBySanitizedParts = messages.map((message) => {
    if (message.role !== "assistant") return message;

    if (!message.parts) return message;

    const sanitizedParts = message.parts.filter((part: unknown) => {
      const typedPart = part as { type?: string; state?: string; text?: string };
      if (typedPart.type === "text") return true;

      if (typedPart.type?.startsWith("tool-")) {
        return typedPart.state === "output-available";
      }

      return true;
    });

    return {
      ...message,
      parts: sanitizedParts,
    };
  });

  return messagesBySanitizedParts.filter((message) => {
    if (!message.parts || message.parts.length === 0) return false;

    return message.parts.some((part: unknown) => {
      const typedPart = part as { type?: string; state?: string; text?: string };
      if (typedPart.type === "text" && typedPart.text?.length && typedPart.text.length > 0) return true;
      if (typedPart.type?.startsWith("tool-") && typedPart.state === "output-available")
        return true;
      return false;
    });
  });
}
