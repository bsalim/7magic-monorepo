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
  'Beauty & Bridal',
  'Attire & Extras'
];

export const VENDORS: Vendor[] = [
  { name: 'Kian Photomorphosis', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-kian-photomorphosis-photographer.png' },
  { name: 'JTV Art', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-jtv-art.png' },
  { name: 'Canister Pictures', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-canister.png' },
  { name: 'Oxalis Pictures', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-oxaus-pictures.png' },
  { name: 'Matthew', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-matthew.png' },
  { name: 'Gian Dhalimarta', cat: 'Photo & Video', logo: '/img/vendor_venues/7magic-gian-dalimarta.png' },
  { name: 'Alfa Kreasi', cat: 'Decoration', logo: '/img/vendor_venues/7magic-alfa-kreasi-decoration.png' },
  { name: 'Luxior', cat: 'Decoration', logo: '/img/vendor_venues/7magic-luxior-decoration.png' },
  { name: 'Creativo', cat: 'Decoration', logo: '/img/vendor_venues/7magic-creativo.png' },
  { name: 'Khayalan', cat: 'Decoration', logo: '/img/vendor_venues/7magic-khayalan-photography.png' },
  { name: 'Eiffel Cake', cat: 'Cakes', logo: '/img/vendor_venues/7magic-eiffel-cake.png' },
  { name: 'Libra Cake', cat: 'Cakes', logo: '/img/vendor_venues/7magic-libracake.png' },
  { name: 'Royalty Cakes', cat: 'Cakes', logo: '/img/vendor_venues/7magic-royalty-cake.png' },
  { name: 'RR Cakes', cat: 'Cakes', logo: '/img/vendor_venues/7magic-rr-cakes.png' },
  { name: 'David Entertainment', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-david-entertainment.png' },
  { name: 'Jingle Entertainment', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-jingle-entertainment.png' },
  { name: 'Unik Music', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-unik-entertainment.png' },
  { name: 'Crescendo', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-crescendo.png' },
  { name: 'Joyful Projects', cat: 'Entertainment', logo: '/img/vendor_venues/7magic-joyful.png' },
  { name: 'Valencia Signature', cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-valencia-signature.png' },
  { name: 'Sharon Cindy MUA', cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-sharon-cindy-makeup-artist.png' },
  { name: 'Coutier White', cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-courtier.png' },
  { name: 'Veli Bridal & Couture', cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-veli-bridal-couture.png' },
  { name: "Luxe'Brides", cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-luxebride.png' },
  { name: 'Skin+ by Euromedica', cat: 'Beauty & Bridal', logo: '/img/vendor_venues/7magic-skin.png' },
  { name: 'Shuang Couture', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-shuang-couture.png' },
  { name: 'Wong Hang Tailor', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-wonghang.png' },
  { name: 'Solo Baru Tailor', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-solobaru.png' },
  { name: 'Fendi Wedding Car', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-fendi-wedding-car.png' },
  { name: 'Sixclover Gift', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-six-clover-gift.png' },
  { name: 'Catherine Wedding', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-catherine-wedding-bridal.png' },
  { name: 'Wedding Factory', cat: 'Attire & Extras', logo: '/img/vendor_venues/7magic-w-factory.png' }
];

/** Kept in sync automatically so the "vendor partners" stat cannot drift. */
export const vendorCount = VENDORS.length;
