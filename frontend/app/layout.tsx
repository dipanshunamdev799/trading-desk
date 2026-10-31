import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trading Desk",
  description: "Local charts, backtests, and paper trading over Upstox data",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
