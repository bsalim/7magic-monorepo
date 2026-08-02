import { browser } from '$app/environment';

export type AnalyticsProps = Record<string, string | number | boolean>;

declare global {
  interface Window {
    plausible?: {
      (event: string, options?: { props?: AnalyticsProps }): void;
      q?: unknown[];
    };
  }
}

/**
 * Send a Plausible custom event.
 *
 * Properties ride on a custom event rather than on the automatic pageview:
 * plausible(event, { props }) behaves the same whichever Plausible script
 * variant is loaded, while pageview properties depend on the variant.
 *
 * A no-op wherever the script is absent — every environment that leaves
 * PUBLIC_PLAUSIBLE_SRC unset, plus any visitor running a content blocker.
 * Analytics must never be able to break the page.
 */
export function trackEvent(event: string, props?: AnalyticsProps): void {
  if (!browser) return;

  window.plausible?.(event, props ? { props } : undefined);
}
