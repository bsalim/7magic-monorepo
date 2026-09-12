import { browser } from '$app/environment';

export type AnalyticsProps = Record<string, string | number | boolean>;

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}

/**
 * Send a Google Analytics (gtag.js) custom event.
 *
 * A no-op wherever the script is absent — every environment that leaves
 * PUBLIC_GA_MEASUREMENT_ID unset, plus any visitor running a content
 * blocker. Analytics must never be able to break the page.
 */
export function trackEvent(event: string, props?: AnalyticsProps): void {
  if (!browser) return;

  window.gtag?.('event', event, props);
}
