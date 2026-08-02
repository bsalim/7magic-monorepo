export type VenueFormPayload = {
  name: string;
  slug: string;
  city: string;
  district: string;
  address: string;
  stars: number;
  description: string;
  price_start_from: number | null;
  price_for_total_pax: number;
  status: 'draft' | 'active' | 'archived';
};

export type VenueFormErrors = Partial<Record<keyof VenueFormPayload, string>>;

export function venuePayloadFromForm(formData: FormData): VenueFormPayload {
  return {
    name: stringField(formData, 'name'),
    slug: stringField(formData, 'slug'),
    city: stringField(formData, 'city'),
    district: stringField(formData, 'district'),
    address: stringField(formData, 'address'),
    stars: numberField(formData, 'stars', 5),
    description: stringField(formData, 'description'),
    price_start_from: nullableNumberField(formData, 'price_start_from'),
    price_for_total_pax: numberField(formData, 'price_for_total_pax', 0),
    status: statusField(formData)
  };
}

export function validateVenuePayload(payload: VenueFormPayload): VenueFormErrors {
  const errors: VenueFormErrors = {};

  if (payload.name.length < 2) errors.name = 'Name must be at least 2 characters.';
  if (payload.slug.length < 2) errors.slug = 'Slug must be at least 2 characters.';
  if (payload.city.length < 2) errors.city = 'City must be at least 2 characters.';
  if (payload.district.length < 2) errors.district = 'District must be at least 2 characters.';
  if (payload.address.length < 2) errors.address = 'Address must be at least 2 characters.';
  if (payload.stars < 1 || payload.stars > 5) errors.stars = 'Stars must be between 1 and 5.';
  if (!payload.description) errors.description = 'Description is required.';
  if (payload.price_start_from !== null && payload.price_start_from < 0) {
    errors.price_start_from = 'Starting price cannot be negative.';
  }
  if (payload.price_for_total_pax < 0) {
    errors.price_for_total_pax = 'Package pax cannot be negative.';
  }

  return errors;
}

function stringField(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === 'string' ? value.trim() : '';
}

function nullableNumberField(formData: FormData, key: string): number | null {
  const value = stringField(formData, key);
  if (!value) return null;
  return Number(value);
}

function numberField(formData: FormData, key: string, fallback: number): number {
  const value = stringField(formData, key);
  if (!value) return fallback;
  return Number(value);
}

function statusField(formData: FormData): VenueFormPayload['status'] {
  const value = stringField(formData, 'status');
  if (value === 'active' || value === 'archived') return value;
  return 'draft';
}
