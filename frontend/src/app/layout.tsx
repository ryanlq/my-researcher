import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GPT-Researcher - AI 研究助手",
  description: "基于 AI 的自动化研究平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="h-full">
      <body className={inter.className + " h-full m-0 p-0"}>
        {children}
      </body>
    </html>
  );
}
