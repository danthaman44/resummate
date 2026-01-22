'use client'

import { useState } from "react"
import { Sun, Moon } from "lucide-react"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle"

export function DarkModeToggle() {
  const [mode, setMode] = useState("light")

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <ToggleGroup
        type="single"
        value={mode}
        onValueChange={(value) => {
          if (value) setMode(value)
        }}
        variant="outline"
      >
        <ToggleGroupItem value="light" aria-label="Light mode" className="gap-2 px-4">
          <Sun className="h-4 w-4" />
          <span>Light</span>
        </ToggleGroupItem>
        <ToggleGroupItem value="dark" aria-label="Dark mode" className="gap-2 px-4">
          <Moon className="h-4 w-4" />
          <span>Dark</span>
        </ToggleGroupItem>
      </ToggleGroup>
    </div>
  )
}