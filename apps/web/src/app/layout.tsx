import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Overlay365 - Environmental Initiatives Ecosystem',
  description: '13 Interconnected Climate-Tech Sub-Businesses | Strategic Partnerships & Affiliate Marketing | Overlay365',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
