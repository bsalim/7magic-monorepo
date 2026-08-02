// adapter-node builds a standalone Node server (build/index.js) that systemd
// can run directly. adapter-auto only targets managed platforms and fails on a
// plain VPS.
import adapter from '@sveltejs/adapter-node';

const config = {
  kit: {
    adapter: adapter()
  }
};

export default config;
