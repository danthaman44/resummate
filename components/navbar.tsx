"use client";

import { Button } from "./ui/button";
import { GitIcon, MessageIcon } from "./icons";
import Link from "next/link";
import { useRouter } from "next/navigation"
import { useCallback } from "react";

export const Navbar = () => {

  const router = useRouter()
  const refreshSession = useCallback(async () => {
    const uuid = crypto.randomUUID()
    // Redirect to the home page with the UUID appended
    router.push(`/${uuid}`)
  }, [router]);

  return (
    <div className="p-2 flex flex-row gap-2 justify-between">
      <Link href="https://github.com/danthaman44/ai-sdk/">
        <Button variant="outline">
          <GitIcon /> View Source Code
        </Button>
      </Link>

      <Button onClick={(event) => {
        event.preventDefault();
        refreshSession();
      }}>
        <MessageIcon />
        New Session
      </Button>
    </div>
  );
};
