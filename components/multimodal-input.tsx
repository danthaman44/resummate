"use client";

import { motion } from "framer-motion";
import React, {
  useRef,
  useEffect,
  useCallback,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import { toast } from "sonner";
import { useLocalStorage, useWindowSize } from "usehooks-ts";

import { cn, sanitizeUIMessages } from "@/lib/utils";

import { ArrowUpIcon, StopIcon } from "./icons";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { FileAttachment as FileAttachmentComponent } from "./file-attachment";
import { AttachmentsButton } from "./ui/attachments-button";
import { MicrophoneButton } from "./ui/microphone-button";

import type { UIMessage, UseChatHelpers } from "@ai-sdk/react";

type ChatRequestOptions = {
  headers?: Record<string, string> | Headers;
  body?: object;
  data?: any;
};

const suggestedActions = [
  {
    title: "0",
    label: "What’s the biggest red flag?",
  },
  {
    title: "1",
    label: "How would this resume differ for startups?",
  },
  {
    title: "2",
    label: "Where can I show ownership or decision-making?",
  },
  {
    title: "3",
    label: "How ATS-friendly is this resume?",
  },
];

export function MultimodalInput({
  chatId,
  input,
  setInput,
  isLoading,
  stop,
  messages,
  setMessages,
  sendMessage,
  handleSubmit,
  status,
  className,
}: {
  chatId: string;
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  stop: () => void;
  messages: Array<UIMessage>;
  setMessages: Dispatch<SetStateAction<Array<UIMessage>>>;
  sendMessage: UseChatHelpers<UIMessage>['sendMessage']
  handleSubmit: (
    event?: {
      preventDefault?: () => void;
    },
    chatRequestOptions?: ChatRequestOptions
  ) => void;
  status: UseChatHelpers<UIMessage>["status"];
  className?: string;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const resumeInputRef = useRef<HTMLInputElement>(null);
  const jobDescriptionInputRef = useRef<HTMLInputElement>(null);
  const [isResumeLoading, setIsResumeLoading] = useState<boolean>(false);
  const [isJobDescriptionLoading, setIsJobDescriptionLoading] = useState<boolean>(false);
  const [attachedResume, setAttachedResume] = useState<{ name: string; type: string } | null>(null);
  const [attachedJobDescription, setAttachedJobDescription] = useState<{ name: string; type: string } | null>(null);

  // audio recording
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const { width } = useWindowSize();

  useEffect(() => {
    if (textareaRef.current) {
      adjustHeight();
    }
  }, []);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight + 2}px`;
    }
  };

  const [localStorageInput, setLocalStorageInput] = useLocalStorage(
    "input",
    ""
  );

  useEffect(() => {
    if (textareaRef.current) {
      const domValue = textareaRef.current.value;
      // Prefer DOM value over localStorage to handle hydration
      const finalValue = domValue || localStorageInput || "";
      setInput(finalValue);
      adjustHeight();
    }
    // Only run once after hydration
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setLocalStorageInput(input);
  }, [input, setLocalStorageInput]);

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    adjustHeight();
  };

  const uploadResume = useCallback(async (file: File, chatId: string) => {
    setIsResumeLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("uuid", chatId);

    // Store the attached file info
    const fileType = file.type.split('/')[1]?.toUpperCase() || 'PDF';
    setAttachedResume({
      name: file.name,
      type: fileType,
    });

    try {
      const response = await fetch("/api/files/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(file.name + " uploaded successfully!");

        return {
          url: data.url,
          name: data.pathname,
          contentType: data.contentType,
        };
      } else {
        toast.error("Failed to upload resume, please try again!");
      }
    } catch (_error) {
      toast.error("Failed to upload resume, please try again!");
    } finally {
      setIsResumeLoading(false);
    }
  }, []);

  const submitForm = useCallback(() => {
    handleSubmit(undefined, {});
    setLocalStorageInput("");

    if (width && width > 768) {
      textareaRef.current?.focus();
    }
  }, [handleSubmit, setLocalStorageInput, width]);

  const loadResume = useCallback(async (chatId: string) => {
    try {
      const response = await fetch(`/api/files/${chatId}`, {
        method: "GET",
      });

      if (response.ok) {
        const data = await response.json();

        const fileType = data.contentType.split('/')[1]?.toUpperCase() || 'PDF';
        setAttachedResume({
          name: data.name,
          type: fileType,
        });
      } else {
        setAttachedResume(null);
      }
    } catch (error) {
      console.error(error);
      setAttachedResume(null);
    }
  }, []);

  const removeResume = useCallback(async (chatId: string) => {
    setAttachedResume(null);
    try {
      const response = await fetch(`/api/files/${chatId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
      } else {
        toast.error("Failed to delete resume, please try again!");
      }
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    loadResume(chatId);
  }, [chatId, loadResume]);

  const uploadJobDescription = useCallback(async (file: File, chatId: string) => {
    setIsJobDescriptionLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("uuid", chatId);
    formData.append("type", "job-description");

    const fileType = file.type.split('/')[1]?.toUpperCase() || 'PDF';
    setAttachedJobDescription({
      name: file.name,
      type: fileType,
    });

    try {
      const response = await fetch("/api/files/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(file.name + " uploaded successfully!");

        return {
          url: data.url,
          name: data.pathname,
          contentType: data.contentType,
        };
      } else {
        toast.error("Failed to upload job description, please try again!");
      }
    } catch (_error) {
      toast.error("Failed to upload job description, please try again!");
    } finally {
      setIsJobDescriptionLoading(false);
    }
  }, []);

  const loadJobDescription = useCallback(async (chatId: string) => {
    try {
      const response = await fetch(`/api/files/${chatId}?type=job-description`, {
        method: "GET",
      });

      if (response.ok) {
        const data = await response.json();

        const fileType = data.contentType.split('/')[1]?.toUpperCase() || 'PDF';
        setAttachedJobDescription({
          name: data.name,
          type: fileType,
        });
      } else {
        setAttachedJobDescription(null);
      }
    } catch (error) {
      console.error(error);
      setAttachedJobDescription(null);
    }
  }, []);

  const removeJobDescription = useCallback(async (chatId: string) => {
    setAttachedJobDescription(null);
    try {
      const response = await fetch(`/api/files/${chatId}?type=job-description`, {
        method: "DELETE",
      });
      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
      } else {
        toast.error("Failed to delete job description, please try again!");
      }
    } catch (error) {
      console.error(error);
    }
  }, []);

  // useEffect(() => {
  //   loadJobDescription(chatId);
  // }, [chatId, loadJobDescription]);

  const handleMicrophoneClick = useCallback(async () => {
    if (isRecording) {
      console.log("stopping recording");
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      // Start recording
      try {
        console.log("starting recording");
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          console.log("event.data", event.data);
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          console.log("audioBlob", audioBlob);
          // TODO: Handle the recorded audio (e.g., send to API, transcribe, etc.)
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        console.error("Error accessing microphone:", error);
        toast.error("Failed to access microphone. Please check permissions.");
      }
    }
  }, [isRecording]);

  return (
    <div className="relative w-full flex flex-col gap-4">
      {messages.length === 0 && (
        <div className="grid sm:grid-cols-2 gap-2 w-full">
          {suggestedActions.map((suggestedAction, index) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.05 * index }}
              key={`suggested-action-${suggestedAction.title}-${index}`}
              className={index > 1 ? "hidden sm:block" : "block"}
            >
              <Button
                variant="ghost"
                onClick={async () => {
                  sendMessage({
                    role: "user",
                    parts: [
                      {
                        type: "text",
                        text: suggestedAction.label,
                      },
                    ],
                  });
                }}
                className="text-left border rounded-xl px-4 py-3.5 text-sm w-full h-auto justify-start items-start whitespace-normal break-words overflow-wrap-anywhere"
              >
                <span className="text-muted-foreground">
                  {suggestedAction.label}
                </span>
              </Button>
            </motion.div>
          ))}
        </div>
      )}

      {/* File Attachments */}
      {(attachedResume || isResumeLoading || attachedJobDescription || isJobDescriptionLoading) && (
        <div className="flex flex-wrap gap-2 justify-start">
          {(attachedResume || isResumeLoading) && (
            <FileAttachmentComponent
              fileName={attachedResume?.name || "Resume"}
              fileType={attachedResume?.type || "PDF"}
              onRemove={() => removeResume(chatId)}
              isLoading={isResumeLoading}
            />
          )}
          {(attachedJobDescription || isJobDescriptionLoading) && (
            <FileAttachmentComponent
              fileName={attachedJobDescription?.name || "Job Description"}
              fileType={attachedJobDescription?.type || "PDF"}
              onRemove={() => removeJobDescription(chatId)}
              isLoading={isJobDescriptionLoading}
            />
          )}
        </div>
      )}

      <Textarea
        ref={textareaRef}
        placeholder="Send a message..."
        value={input || ""}
        onChange={handleInput}
        className={cn(
          "min-h-[24px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-xl !text-base bg-muted",
          className
        )}
        rows={3}
        autoFocus
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (isLoading) {
              toast.error("Please wait for the model to finish its response!");
            } else {
              submitForm();
            }
          }
        }}
      />

      <input
        ref={resumeInputRef}
        type="file"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            uploadResume(file, chatId);
          }
        }}
        accept="application/pdf"
      />

      <input
        ref={jobDescriptionInputRef}
        type="file"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            uploadJobDescription(file, chatId);
          }
        }}
        accept="application/pdf"
      />

      <AttachmentsButton
        resumeInputRef={resumeInputRef}
        jobDescriptionInputRef={jobDescriptionInputRef}
        status={status}
      />

      <MicrophoneButton
        isRecording={isRecording}
        onClick={handleMicrophoneClick}
        status={status}
      />

      {isLoading ? (
        <Button
          className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
          onClick={(event) => {
            event.preventDefault();
            stop();
            setMessages((messages) => sanitizeUIMessages(messages));
          }}
        >
          <StopIcon size={14} />
        </Button>
      ) : (
        <Button
          className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
          onClick={(event) => {
            event.preventDefault();
            submitForm();
          }}
          disabled={!input || input.length === 0}
        >
          <ArrowUpIcon size={14} />
        </Button>
      )}
    </div>
  );
}