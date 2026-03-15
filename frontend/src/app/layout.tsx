import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Million Miles | Car Listings",
  description: "Used car listings from CarSensor.net",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
