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
      //
      // The article patterns must come before the catch-all for the same
      // first-match-wins reason -- the catch-all would otherwise turn
      // '/en/articles/x' into the route '/articles/x', which does not exist.
      // The bare '/artikel' is listed separately because '/artikel/:path(.*)?'
      // requires the trailing slash and so does not match the list page itself.
      //
      // This localizes the path *structure* only. The category and slug segments
      // differ per locale too, but they are content, not routing: paraglide
      // cannot know them, so `localizeHref` on an article URL produces a
      // structurally valid path with the wrong segments. Anything that needs a
      // real cross-locale article URL uses the `alternates` map the API returns.
      urlPatterns: [
        {
          pattern: '/artikel',
          localized: [
            ['en', '/en/articles'],
            ['id', '/artikel']
          ]
        },
        {
          pattern: '/artikel/:path(.*)?',
          localized: [
            ['en', '/en/articles/:path(.*)?'],
            ['id', '/artikel/:path(.*)?']
          ]
        },
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
