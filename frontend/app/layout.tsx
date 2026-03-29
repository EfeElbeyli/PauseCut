import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "PauseCut",
  description: "AI-powered video pause trimming",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-gray-50 text-gray-900" suppressHydrationWarning>
        <div className="mx-auto max-w-5xl px-6 py-10">{children}</div>
      </body>
    </html>
  );
}
