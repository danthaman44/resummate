"use client"

import { FileText, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileAttachmentProps {
  fileName: string
  fileType: string
  onRemove?: () => void
}

export function FileAttachment({ fileName, fileType, onRemove }: FileAttachmentProps) {
  return (
    <div className="inline-flex items-center gap-3 rounded-xl bg-zinc-100 px-3 py-2.5 pr-2">
      {/* Document Icon */}
      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-red-400 to-orange-500">
        <FileText className="h-7 w-7 text-white" strokeWidth={2} />
      </div>

      {/* File Info */}
      <div className="flex flex-col gap-0.5 min-w-0">
        <p className="text-sm font-medium text-zinc-900 leading-tight text-balance">{fileName}</p>
        <p className="text-xs text-zinc-600 uppercase tracking-wide">{fileType}</p>
      </div>

      {/* Close Button */}
      {onRemove && (
        <Button
          variant="ghost"
          size="icon"
          onClick={onRemove}
          className="ml-2 h-8 w-8 shrink-0 rounded-full bg-zinc-200 hover:bg-zinc-300 text-zinc-600 hover:text-zinc-900"
          aria-label="Remove file"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  )
}
