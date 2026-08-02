import { fail, redirect } from '@sveltejs/kit';

import type { VenueDetail, VenuePhoto } from '$lib/api';
import { ApiRequestError, apiFetch } from '$lib/server/api';
import {
  validateVenuePayload,
  venuePayloadFromForm,
  type VenueFormErrors,
  type VenueFormPayload
} from '$lib/server/venueForm';

import type { Actions, PageServerLoad } from './$types';

type VenueTranslation = {
  venue_id: number;
  locale: string;
  description: string | null;
};

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.token) {
    throw redirect(303, '/login');
  }

  try {
    const venue = await apiFetch<VenueDetail>(`/api/v1/admin/venues/${params.id}`, {
      token: locals.token
    });

    // A venue with no English row yet returns empty fields, not a 404.
    const translation = await apiFetch<VenueTranslation>(
      `/api/v1/admin/venues/${params.id}/translations/en`,
      { token: locals.token }
    );

    return {
      error: '',
      values: valuesFromVenue(venue),
      descriptionEn: translation.description ?? '',
      venue
    };
  } catch (error) {
    return {
      error:
        error instanceof ApiRequestError
          ? error.message
          : 'Unable to load venue. Check the API server and try again.',
      values: null,
      descriptionEn: '',
      venue: null
    };
  }
};

export const actions: Actions = {
  save: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const formData = await request.formData();
    const descriptionEn = stringField(formData, 'description_en');
    const values = venuePayloadFromForm(formData);
    const errors = validateVenuePayload(values);
    if (Object.keys(errors).length) {
      return fail(400, {
        errors,
        message: 'Fix the highlighted venue fields.',
        values
      });
    }

    try {
      const venue = await apiFetch<VenueDetail>(`/api/v1/admin/venues/${params.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
        token: locals.token
      });

      // An empty box clears the translation, restoring the Indonesian fallback.
      await apiFetch(`/api/v1/admin/venues/${params.id}/translations/en`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: descriptionEn || null }),
        token: locals.token
      });

      return {
        errors: {},
        message: 'Venue saved.',
        descriptionEn,
        values: valuesFromVenue(venue)
      };
    } catch (error) {
      const apiErrors: VenueFormErrors = {};
      if (error instanceof ApiRequestError && error.code === 'slug_conflict') {
        apiErrors.slug = error.message;
      }

      return fail(error instanceof ApiRequestError ? error.status : 500, {
        errors: apiErrors,
        message:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to save venue. Check the API server and try again.',
        values
      });
    }
  },

  uploadPhoto: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const formData = await request.formData();
    const file = formData.get('file');
    if (!(file instanceof File) || file.size === 0) {
      return fail(400, {
        uploadMessage: 'Choose a venue photo to upload.'
      });
    }

    const upstream = new FormData();
    upstream.set('file', file);
    upstream.set('alt_text', stringField(formData, 'alt_text'));
    upstream.set('sort_order', stringField(formData, 'sort_order') || '0');
    upstream.set('set_as_cover', formData.get('set_as_cover') === 'on' ? 'true' : 'false');

    try {
      const photo = await apiFetch<VenuePhoto>(`/api/v1/admin/venues/${params.id}/photos`, {
        method: 'POST',
        body: upstream,
        token: locals.token
      });

      return {
        photo,
        uploadMessage: 'Photo uploaded.'
      };
    } catch (error) {
      const storageNotConfigured =
        error instanceof ApiRequestError && error.code === 'storage_not_configured';
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        storageNotConfigured,
        uploadMessage: storageNotConfigured
          ? 'Photo storage (R2) is not configured yet, so uploads are disabled. The venue record was not changed.'
          : error instanceof ApiRequestError
            ? error.message
            : 'Unable to upload photo. Check R2 settings and try again.'
      });
    }
  },

  deletePhoto: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const photoId = stringField(await request.formData(), 'photo_id');
    if (!photoId) {
      return fail(400, { uploadMessage: 'Missing photo id.' });
    }

    try {
      await apiFetch<VenueDetail>(`/api/v1/admin/venues/${params.id}/photos/${photoId}`, {
        method: 'DELETE',
        token: locals.token
      });
      return { uploadMessage: 'Photo removed.' };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        uploadMessage:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to remove photo. Try again.'
      });
    }
  },

  setCoverPhoto: async ({ locals, params, request }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    const photoId = stringField(await request.formData(), 'photo_id');
    if (!photoId) {
      return fail(400, { uploadMessage: 'Missing photo id.' });
    }

    try {
      await apiFetch(`/api/v1/admin/venues/${params.id}/photos/${photoId}/cover`, {
        method: 'POST',
        token: locals.token
      });
      return { uploadMessage: 'Cover photo updated.' };
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        uploadMessage:
          error instanceof ApiRequestError ? error.message : 'Unable to set cover photo.'
      });
    }
  },

  deleteVenue: async ({ locals, params }) => {
    if (!locals.token) {
      throw redirect(303, '/login');
    }

    try {
      await apiFetch(`/api/v1/admin/venues/${params.id}`, {
        method: 'DELETE',
        token: locals.token
      });
    } catch (error) {
      return fail(error instanceof ApiRequestError ? error.status : 500, {
        deleteMessage:
          error instanceof ApiRequestError
            ? error.message
            : 'Unable to delete venue. Try again.'
      });
    }

    throw redirect(303, '/venues');
  }
};

function valuesFromVenue(venue: VenueDetail): VenueFormPayload {
  return {
    name: venue.name,
    slug: venue.slug,
    city: venue.city,
    district: venue.district,
    address: venue.address,
    stars: venue.stars,
    description: venue.description,
    price_start_from: venue.price_start_from,
    price_for_total_pax: venue.price_for_total_pax,
    status: venue.status === 'active' || venue.status === 'archived' ? venue.status : 'draft'
  };
}

function stringField(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === 'string' ? value.trim() : '';
}
