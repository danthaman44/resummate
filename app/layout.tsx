import "./globals.css";
import { StackProvider, StackTheme } from "@stackframe/stack";
import { stackClientApp } from "../stack/client";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";
import { DarkModeToggle } from "@/components/dark-mode-toggle"
import { ThemeProvider } from "@/components/theme-provider";
import { ViewSourceCodeButton } from "@/components/ui/source-code-button";

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