import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChild<T> = T extends { child?: any } ? Omit<T, 'child'> : T;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, 'children'> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };

export function formatPrice(value: number | null | undefined) {
	if (!value) return 'Contact us';
	return `Rp ${value.toLocaleString('id-ID')}`;
}

/**
 * Jakarta shops for wedding packages in millions, not full rupiah, so
 * Rp 88.000.000 reads as "Rp 88 juta" (or "Rp 88 million" in English -- the
 * unit word is passed in because "juta" means nothing to an English reader).
 * Values under a million keep full digits.
 */
export function formatMillions(value: number, unit: string): string {
  if (value < 1_000_000) return `Rp ${value.toLocaleString('id-ID')}`;
  const millions = value / 1_000_000;
  const rounded = Number.isInteger(millions) ? millions : Math.round(millions * 10) / 10;
  return `Rp ${rounded.toLocaleString('id-ID')} ${unit}`;
}

export function titleCase(value: string) {
	return value
		.split(/[-\s]+/)
		.filter(Boolean)
		.map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
		.join(' ');
}

export function articlePath(category: string, slug: string) {
	return `/artikel/${category}/${slug}`;
}
