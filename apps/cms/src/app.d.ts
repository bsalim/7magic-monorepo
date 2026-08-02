import type { AuthUser } from '$lib/api';

declare global {
  namespace App {
    interface Locals {
      token: string | null;
      user: AuthUser | null;
    }
  }
}

export {};
