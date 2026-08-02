import type { VenueDetail } from '$lib/api';

export type DisplayPhoto = {
	src: string;
	thumb: string;
	label: string;
	real: boolean;
};

// Rendered only when a venue has no photos at all. Kept unlabelled rather than
// naming rooms the venue may not have — PhotoMosaic filters these out anyway.
const PLACEHOLDER_COUNT = 5;

export function normalizePhotos(source: VenueDetail): DisplayPhoto[] {
	const realPhotos = source.gallery
		.map((photo, index) => {
			const src =
				photo.fallback ??
				photo.webp ??
				photo.url ??
				photo.thumbnail_url ??
				photo.thumbFallback ??
				photo.thumbWebp;
			if (!src) return undefined;

			return {
				src,
				thumb: photo.thumbFallback ?? photo.thumbWebp ?? photo.thumbnail_url ?? src,
				label:
					photo.alt_text ??
					(index === 0 ? source.cover_photo.alt : `${source.name} photo ${index + 1}`),
				real: true
			};
		})
		.filter((photo): photo is DisplayPhoto => Boolean(photo));

	const coverPhoto = {
		src: source.cover_photo.small_url,
		thumb: source.cover_photo.small_url,
		label: source.cover_photo.alt,
		real: true
	};

	if (realPhotos.length) return realPhotos;

	const placeholders = Array.from({ length: PLACEHOLDER_COUNT }, (_, index) => ({
		src: '',
		thumb: '',
		label: `${source.name} ${index + 1}`,
		real: false
	}));

	return [coverPhoto, ...placeholders].slice(0, 6);
}
