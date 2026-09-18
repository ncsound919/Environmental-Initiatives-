import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: 'Overlay ECOS — 13 Climate-Tech Initiatives',
  description: 'Overlay ECOS: 13 climate-tech initiatives seeking blended funding — grants, strategic partners, and revenue design partners.',
  icons: {
    icon: '/overlay-ecos-logo.png',
    apple: '/overlay-ecos-logo.png',
  },
  openGraph: {
    title: 'Overlay ECOS — 13 Climate-Tech Initiatives',
    description: '13 climate-tech initiatives seeking blended funding — grants, strategic partners, and revenue design partners.',
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
