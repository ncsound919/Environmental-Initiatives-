import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Overlay365 - Environmental Initiatives Ecosystem',
  description: '13 Interconnected Climate-Tech Sub-Businesses | Strategic Partnerships & Affiliate Marketing | Overlay365',
  icons: {
    icon: '/overlay-ecos-logo.png',
    apple: '/overlay-ecos-logo.png',
  },
  openGraph: {
    title: 'Overlay ECOS',
    description: '13 Interconnected Climate-Tech Sub-Businesses | Strategic Partnerships & Affiliate Marketing | Overlay365',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Sidebar />
          <main className="app-main">{children}</main>
        </div>
      </body>
    </html>
  );
}
