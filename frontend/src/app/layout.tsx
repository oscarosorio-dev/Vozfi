import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vozfi",
  description: "Finanzas personales con voz",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}