/**
 * The concierge services offered to couples marrying in Bali, and their guests.
 *
 * Exactly the services 7Magic's Bali team confirmed it can deliver, in-house or
 * through a partner it trusts (chosen by the user on 2026-10-21). Hair and
 * makeup, proposal planning, honeymoon extensions, video venue tours, a guest
 * RSVP site, a single AUD invoice and a date/permission check were offered and
 * not ticked, so they are not here. Adding one is one entry below.
 *
 * No prices: every service is "ask us". The cost calculator reads this list for
 * its add-ons and prices each one only where a public market range exists.
 */

export type ConciergeGroup = 'paperwork' | 'guests' | 'wedding-week' | 'before-after' | 'stay';

export type ConciergeKey =
  | 'legal'
  | 'transfers'
  | 'accommodation'
  | 'arrival'
  | 'activities'
  | 'welcome'
  | 'blessing'
  | 'hens'
  | 'prewedding'
  | 'renewal'
  | 'car'
  | 'massage'
  | 'chef'
  | 'reservations'
  | 'nanny'
  | 'wellness'
  | 'doctor'
  | 'holiday-photographer';

export type ConciergeService = {
  key: ConciergeKey;
  group: ConciergeGroup;
  name: string;
  blurb: string;
};

export const CONCIERGE_GROUPS: { key: ConciergeGroup; title: string }[] = [
  { key: 'paperwork', title: 'Paperwork & planning' },
  { key: 'guests', title: 'Your guests' },
  { key: 'wedding-week', title: 'Wedding week' },
  { key: 'before-after', title: 'Before & after' },
  { key: 'stay', title: 'During your stay' }
];

export const CONCIERGE_SERVICES: ConciergeService[] = [
  {
    key: 'legal',
    group: 'paperwork',
    name: 'Legal marriage paperwork',
    blurb:
      'We book your Certificate of No Impediment appointment, prepare the documents and handle the civil registration in Bali.'
  },
  {
    key: 'transfers',
    group: 'guests',
    name: 'Airport pickups & guest shuttles',
    blurb:
      "Pickups matched to each guest's flight, and shuttles between the hotels and the venue on the day."
  },
  {
    key: 'accommodation',
    group: 'guests',
    name: 'Accommodation blocks',
    blurb: 'A held block of villas or hotel rooms near your venue, so guests book in one place.'
  },
  {
    key: 'arrival',
    group: 'guests',
    name: 'Arrival help pack',
    blurb:
      'A plain-English guide for guests: visa on arrival, the Bali tourist levy, the arrival card, an eSIM and money.'
  },
  {
    key: 'activities',
    group: 'guests',
    name: 'Guest activities',
    blurb: 'Day trips to Ubud or Nusa Penida, spa days, surf lessons and things for the kids.'
  },
  {
    key: 'welcome',
    group: 'wedding-week',
    name: 'Welcome dinner & recovery brunch',
    blurb: 'An evening to gather everyone before the wedding, a slow brunch the day after.'
  },
  {
    key: 'blessing',
    group: 'wedding-week',
    name: 'Balinese blessing (melukat)',
    blurb: 'A water purification blessing led by a Balinese priest.'
  },
  {
    key: 'hens',
    group: 'wedding-week',
    name: 'Hens & bucks in Bali',
    blurb: 'A villa, a boat day or a beach club, organised for the bridal party.'
  },
  {
    key: 'prewedding',
    group: 'before-after',
    name: 'Pre-wedding shoot',
    blurb: 'An engagement or pre-wedding shoot at a location that suits you.'
  },
  {
    key: 'renewal',
    group: 'before-after',
    name: 'Vow renewal',
    blurb: 'An anniversary or vow renewal, planned by the same team at a smaller scale.'
  },
  {
    key: 'car',
    group: 'stay',
    name: 'Private car & driver',
    blurb: 'A car with an English-speaking driver, by the day, for you, your family or your guests.'
  },
  {
    key: 'massage',
    group: 'stay',
    name: 'Balinese massage & spa',
    blurb: 'In-villa massage, or a spa day for the bridal party.'
  },
  {
    key: 'chef',
    group: 'stay',
    name: 'Private chef',
    blurb: 'A chef for family dinners at the villa.'
  },
  {
    key: 'reservations',
    group: 'stay',
    name: 'Restaurant & beach-club bookings',
    blurb: 'Tables, day beds and sunset spots booked for groups.'
  },
  {
    key: 'nanny',
    group: 'stay',
    name: 'Nanny & babysitting',
    blurb: 'So the parents among your guests can enjoy the wedding night.'
  },
  {
    key: 'wellness',
    group: 'stay',
    name: 'Yoga, surf & wellness',
    blurb: 'A private sunrise yoga session or a surf lesson.'
  },
  {
    key: 'doctor',
    group: 'stay',
    name: 'On-call doctor',
    blurb: 'A doctor who visits the villa, and pharmacy runs, if anyone falls ill.'
  },
  {
    key: 'holiday-photographer',
    group: 'stay',
    name: 'Holiday photographer',
    blurb: 'A few hours of holiday photos for family or guests, apart from the wedding shoot.'
  }
];
