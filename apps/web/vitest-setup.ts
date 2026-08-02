import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/svelte';
import { afterEach } from 'vitest';

// testing-library only auto-registers cleanup when vitest runs with
// `globals: true`. This config keeps globals off, so unmount explicitly —
// otherwise rendered DOM leaks between tests and queries match stale nodes.
afterEach(() => {
  cleanup();
});
