import "./globals.css";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";
import { DarkModeToggle } from "@/components/dark-mode-toggle"
import { ThemeProvider } from "@/components/theme-provider";

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
        <ThemeProvider>
          <Toaster position="top-center" richColors />
          <Navbar />
          {children}
          <DarkModeToggle />
        </ThemeProvider>
      </body>
    </html>
  );
}