/** The contact-lead API rejects a longer message. */
const MAX_MESSAGE = 2000;

/**
 * The lead's message body: what the couple chose on the page, then their notes.
 *
 * The contact-lead schema has no wedding columns, so the qualifying answers are
 * folded into the message the way /bali-wedding-planning does it. The context
 * goes first so a truncation only ever cuts the free-text notes.
 */
export function enquiryMessage(context: string[], notes: string): string {
  const message = [...context, '', notes.trim() || 'No extra notes.'].join('\n');
  return message.slice(0, MAX_MESSAGE);
}
