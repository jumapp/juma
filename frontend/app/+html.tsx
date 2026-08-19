import { ScrollViewStyleReset } from 'expo-router/html';
import type { PropsWithChildren } from 'react';

/**
 * This file is web-only and used to configure the root HTML for every
 * web page during static rendering.
 * The contents of this function only run in Node.js environments and
 * do not have access to the DOM or browser APIs.
 */
export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover"
        />
        <meta name="theme-color" content="#0a7ea4" />
        <meta name="description" content="Jumapp - a cross-platform app that works offline" />

        {/* PWA Manifest */}
        <link rel="manifest" href="/manifest.json" />

        {/* PWA Icons */}
        <link rel="icon" href="/favicon.ico" sizes="64x64 32x32 24x24 16x16" type="image/x-icon" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
        <link rel="apple-touch-icon" sizes="192x192" href="/icons/icon-192.png" />
        <link rel="apple-touch-icon" sizes="512x512" href="/icons/icon-512.png" />

        {/* iOS PWA meta tags */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Jumapp" />
        <meta name="mobile-web-app-capable" content="yes" />

        {/* Service Worker Registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function () {
                  navigator.serviceWorker.register('/service-worker.js').catch(function (error) {
                    console.error('Service worker registration failed:', error);
                  });
                });
              }
            `,
          }}
        />

        {/* Disable body scrolling while web app is loading */}
        <ScrollViewStyleReset />
      </head>
      <body>{children}</body>
    </html>
  );
}