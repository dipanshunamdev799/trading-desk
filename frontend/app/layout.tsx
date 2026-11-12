import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trading Desk",
  description: "Learn the markets through guided research, historical backtests and paper trading.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
