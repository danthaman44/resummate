import "./globals.css";
import { StackProvider, StackTheme } from "@stackframe/stack";
import { stackClientApp } from "../stack/client";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";
import { DarkModeToggle } from "@/components/dark-mode-toggle"
import { ThemeProvider } from "@/components/theme-provider";
import { GitIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export const metadata = {
  title: "Resummate",
  description:
    "Resummate is an AI-powered resume review platform that helps you create a Top 1% application.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head></head>
      <body className={cn(GeistSans.className, "antialiased")}>
        <StackProvider app={stackClientApp}>
          <StackTheme>
            <ThemeProvider>
              <Toaster position="top-center" richColors />
              <Navbar />
              <main className="pt-14">
                {children}
              </main>
              <ViewSourceCodeButton />
              <DarkModeToggle />
            </ThemeProvider>
          </StackTheme>
        </StackProvider>
      </body>
    </html>
  );
}

export function ViewSourceCodeButton() {
  return (
    <div className="fixed bottom-4 left-4 z-50">  
      <Link href="https://github.com/danthaman44/experience-iq/">
        <Button variant="outline">
          <GitIcon /> View Source Code
        </Button>
      </Link>
    </div>
  )
}