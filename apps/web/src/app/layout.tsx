import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ECOS - Environmental Initiatives Ecosystem',
  description: '13 Interconnected Climate-Tech Businesses | Unified Ecosystem for Sustainable Future',
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
