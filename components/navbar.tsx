"use client";

import { Button } from "./ui/button";
import { GitIcon, MessageIcon } from "./icons";
import Link from "next/link";
import { useRouter } from "next/navigation"
import { useCallback } from "react";
import { UserButton } from '@stackframe/stack';

export const Navbar = () => {

  const router = useRouter()
  const refreshSession = useCallback(async () => {
    const uuid = crypto.randomUUID()
    // Redirect to the home page with the UUID appended
    router.push(`/${uuid}`)
  }, [router]);

  return (
    <div className="fixed top-0 left-0 right-0 z-50 p-2 flex flex-row gap-2 justify-between bg-background">
      <div className="flex flex-row gap-2 items-center pl-2">
        <Button onClick={(event) => {
          event.preventDefault();
          refreshSession();
        }}>
          <MessageIcon />
          New Session
        </Button>
      </div>

      <div className="pr-2">
        <UserButton />
      </div>
    </div>
  );
};
