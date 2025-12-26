"use client"

import { Chat } from "@/components/chat";
import { useEffect } from "react"
import { useRouter } from "next/navigation"

export const dynamic = "force-dynamic";

export default function Page() {
  const router = useRouter()

  useEffect(() => {
    // Generate a random UUID using the Web Crypto API
    const uuid = crypto.randomUUID()

    // Redirect to the home page with the UUID appended
    router.push(`/${uuid}`)
  }, [router])

  return <Chat />;
}
