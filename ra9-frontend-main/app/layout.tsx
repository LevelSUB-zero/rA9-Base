import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { Suspense } from "react"
import { UIPrefsProvider } from "@/components/ra9/ui-prefs"
import { ThemeTray } from "@/components/ra9/theme-tray"
import "./globals.css"

export const metadata: Metadata = {
  title: "v0 App",
  description: "Created with v0",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable} ra9 antialiased`}>
        <UIPrefsProvider>
          <Suspense fallback={null}>{children}</Suspense>
          <ThemeTray />
        </UIPrefsProvider>
        <Analytics />
      </body>
    </html>
  )
}
