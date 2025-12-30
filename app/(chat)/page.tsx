"use client"

import { Chat } from "@/components/chat";
import { useEffect } from "react"
import { useParams, useRouter } from "next/navigation"

export const dynamic = "force-dynamic";

export default function Page() {
  const router = useRouter()
  const params = useParams()

  useEffect(() => {
    // Only redirect if uuid is not already in the URL
    const existingUuid = params?.uuid as string;
    
    if (!existingUuid || existingUuid === "") {
      // Generate a random UUID using the Web Crypto API
      const uuid = crypto.randomUUID()

      // Redirect to the home page with the UUID appended
      router.push(`/${uuid}`)
    }
  }, [router, params])

  return <Chat />;
}
