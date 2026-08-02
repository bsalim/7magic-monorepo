// vitest-setup.ts lives outside the tsconfig include, so its jest-dom import
// never reaches svelte-check. This pulls the matcher augmentation into scope
// for test files (toBeInTheDocument, toHaveAttribute, ...).
import '@testing-library/jest-dom/vitest';
