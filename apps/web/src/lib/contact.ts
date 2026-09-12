/**
 * The public contact address.
 *
 * One place, for the same reason `whatsappNumber` is: the previous value
 * (hello@7magic.id) was wrong and had been copied into the contact page, the
 * Organization schema, a script's user-agent and a database migration, so
 * correcting it meant finding four of them.
 */
export const CONTACT_EMAIL = '7magicorganizer@gmail.com';

/**
 * The Instagram account, for the same reason: the footer linked
 * /7magicorganizer/ while the Organization schema claimed /7magicwedding.
 */
export const INSTAGRAM_URL = 'https://www.instagram.com/7magicorganizer/';
