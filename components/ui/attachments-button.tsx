"use client";

import React, { memo } from "react";
import { PaperclipIcon } from "../icons";
import { Button } from "./button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./dropdown-menu";
import type { UseChatHelpers, UIMessage } from "@ai-sdk/react";

interface AttachmentsButtonProps {
  resumeInputRef: React.MutableRefObject<HTMLInputElement | null>;
  jobDescriptionInputRef: React.MutableRefObject<HTMLInputElement | null>;
  status: UseChatHelpers<UIMessage>["status"];
}

function PureAttachmentsButton({
  resumeInputRef,
  jobDescriptionInputRef,
  status,
}: AttachmentsButtonProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          className="rounded-full p-1.5 h-fit absolute bottom-2 left-2 m-0.5 border dark:border-zinc-600"
          data-testid="attachments-button"
          disabled={status !== "ready"}
          variant="ghost"
        >
          <PaperclipIcon size={14} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" side="top" className="min-w-[160px]">
        <DropdownMenuItem
          onClick={() => {
            resumeInputRef.current?.click();
          }}
        >
          Resume
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => {
            jobDescriptionInputRef.current?.click();
          }}
        >
          Job Description
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export const AttachmentsButton = memo(PureAttachmentsButton);
