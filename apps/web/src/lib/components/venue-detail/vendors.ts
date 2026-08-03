export type Vendor = {
	name: string;
	cat: string;
	logo: string;
};

export const VENDOR_CATS = [
  'All',
  'Photo & Video',
  'Decoration',
  'Cakes',
  'Entertainment',
  'Bridal & Suit',
  'Extra'
];

export const VENDORS: Vendor[] = [
  { name: 'Kian Photomorphosis', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-kian-photomorphosis-photographer.png' },
  { name: 'Canister Pictures', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-canister.png' },
  { name: 'Oxalis Pictures', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-oxaus-pictures.png' },
  { name: 'Gian Dhalimarta', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-gian-dalimarta.png' },
  { name: 'Khayalan', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-khayalan-photography.png' },
  { name: 'Wedding Factory', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-w-factory.png' },
  { name: 'Xion', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-xion-photographer.png' },
  { name: 'Monchichi', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-monchichi-photography.png' },
  { name: 'Alfa Kreasi', cat: 'Decoration', logo: '/img/vendor_venues/7magic-alfa-kreasi-decoration.png' },
  { name: 'Luxior', cat: 'Decoration', logo: '/img/vendor_venues/7magic-luxior-decoration.png' },
  { name: 'Eiffel Cake', cat: 'Cakes', logo: '/img/vendor_venues/7magic-eiffel-cake.png' },
  { name: 'Libra Cake', cat: 'Cakes', logo: '/img/vendor_venues/7magic-libracake.png' },
  { name: 'Royalty Cakes', cat: 'Cakes', logo: '/img/vendor_venues/7magic-royalty-cake.png' },
  { name: 'RR Cakes', cat: 'Cakes', logo: '/img/vendor_venues/7magic-rr-cakes.png' },
  { name: 'Double U Cakes', cat: 'Cakes', logo: '/img/vendor_venues/7magic-w-wedding-cake.png' },
  { name: 'David Entertainment', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-david-entertainment.png' },
  { name: 'Jingle Entertainment', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-jingle-entertainment.png' },
  { name: 'Unik Music', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-unik-entertainment.png' },
  { name: 'Crescendo', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-crescendo.png' },
  { name: 'Joyful Projects', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-joyful.png' },
  { name: 'Matthew Entertainment', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-matthew.png' },
  { name: 'Valencia Signature', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-valencia-signature.png' },
  { name: 'Coutier White', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-courtier.png' },
  { name: 'Veli Bridal & Couture', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-veli-bridal-couture.png' },
  { name: "Luxe'Brides", cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-luxebride.png' },
  { name: 'Sanggar Rias Indah', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-sanggar-rias-indah.png' },
  { name: 'SAS Designs', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-sas.png' },
  { name: 'Wong Hang Tailor', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-wonghang.png' },
  { name: 'Solo Baru Tailor', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-solobaru.png' },
  { name: 'Creativo', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-creativo.png' },
  { name: 'Catherine Wedding', cat: 'Bridal & Suit', logo: '/img/vendor_venues/7magic-catherine-wedding-bridal.png' },
  { name: 'Shuang Couture', cat: 'Extra', logo: '/img/vendor_venues/7magic-shuang-couture.png' },
  { name: 'Sixclover Gift', cat: 'Extra', logo: '/img/vendor_venues/7magic-six-clover-gift.png' },
  { name: 'Fendi Wedding Car', cat: 'Extra', logo: '/img/vendor_venues/7magic-fendi-wedding-car.png' },
  { name: 'Viding', cat: 'Extra', logo: '/img/vendor_venues/7magic-viding.png' }
];

/** Kept in sync automatically so the "vendor partners" stat cannot drift. */
export const vendorCount = VENDORS.length;
