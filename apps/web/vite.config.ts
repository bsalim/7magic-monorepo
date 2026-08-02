/// <reference types="vitest/config" />
import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    paraglideVitePlugin({
      project: './project.inlang',
      outdir: './src/lib/paraglide',
      // Indonesian stays at the root so existing URLs and their SEO are
      // untouched; English lives under /en.
      strategy: ['url', 'preferredLanguage', 'baseLocale'],
      // The prefixed locale must be listed first: '/:path(.*)?' also matches
      // '/en/...', so a base-locale-first order would swallow the prefix and
      // de-localization would never strip it.
      urlPatterns: [
        {
          pattern: '/:path(.*)?',
          localized: [
            ['en', '/en/:path(.*)?'],
            ['id', '/:path(.*)?']
          ]
        }
      ]
    }),
    tailwindcss(),
    sveltekit()
  ],
  // Svelte 5 components must resolve to their browser build under jsdom.
  // Scoped to test runs so the dev/build SSR resolution is untouched.
  resolve: process.env.VITEST ? { conditions: ['browser'] } : undefined,
  // vitest 3.2 ships vite 7 types while this project is on vite 8, so its
  // augmentation of UserConfig does not apply and `test` reads as unknown.
  // Vitest still reads this block at runtime.
  // @ts-expect-error -- remove once vitest ships vite 8 types
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest-setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts}']
  }
});
