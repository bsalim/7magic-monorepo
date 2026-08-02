// adapter-node builds a standalone Node server (build/index.js) that systemd
// can run directly. adapter-auto only targets managed platforms and fails on a
// plain VPS.
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter()
  }
};

export default config;
