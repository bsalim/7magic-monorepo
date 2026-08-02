import { deLocalizeUrl } from '$lib/paraglide/runtime';

// Strips the /en prefix so both locales resolve to the same SvelteKit route.
export const reroute = (request: { url: URL }) => deLocalizeUrl(request.url).pathname;
