import { loadBookableBranches } from '$lib/tour';

import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
  // Read live rather than hardcoded, so the page advertises exactly the branches
  // that can take a booking -- and starts showing a new one the day its opening
  // hours are set, with no code change.
  return { branches: await loadBookableBranches(fetch) };
};
