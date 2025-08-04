import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ClannAI - Football Analysis Platform",
  description: "Professional video analysis platform for football teams. Upload matches, get AI-powered tactical insights, and improve your team's performance.",
  keywords: ["football", "analysis", "video", "tactics", "AI", "coaching", "team management"],
  authors: [{ name: "ClannAI" }],
  creator: "ClannAI",
  publisher: "ClannAI",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://clannai.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: "ClannAI - Football Analysis Platform",
    description: "Professional video analysis platform for football teams. Upload matches, get AI-powered tactical insights, and improve your team's performance.",
    url: 'https://clannai.com',
    siteName: 'ClannAI',
    images: [
      {
        url: '/clann-logo.png',
        width: 1200,
        height: 630,
        alt: 'ClannAI Football Analysis Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "ClannAI - Football Analysis Platform",
    description: "Professional video analysis platform for football teams. Upload matches, get AI-powered tactical insights, and improve your team's performance.",
    creator: '@ClannAI',
    images: ['/clann-logo.png'],
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
