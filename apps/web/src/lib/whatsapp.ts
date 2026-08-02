/**
 * The 7Magic enquiry line, in wa.me format (country code, no + or spaces).
 * Matches the number published in the footer and on 7magicwedding.com.
 *
 * This lives in one place because the previous placeholder (6281234567890) had
 * been copied into several components, so every WhatsApp CTA on the site was
 * pointing at a number nobody owns.
 */
export const whatsappNumber = '6289628614447';

/** Builds a wa.me link with the message pre-filled. */
export function whatsappHref(message: string): string {
	return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
}

/** Human-readable form, for display next to the link. */
export const whatsappDisplay = '+62 896 2861 4447';
