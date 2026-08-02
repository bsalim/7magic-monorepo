import { redirect } from '@sveltejs/kit';

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  const isLoginRoute = url.pathname === '/login';

  if (!locals.user && !isLoginRoute) {
    const redirectTo = `${url.pathname}${url.search}`;
    throw redirect(303, `/login?redirectTo=${encodeURIComponent(redirectTo)}`);
  }

  if (locals.user && isLoginRoute) {
    throw redirect(303, '/');
  }

  return {
    user: locals.user
  };
};
