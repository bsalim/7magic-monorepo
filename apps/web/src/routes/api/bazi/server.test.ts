import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/api', () => ({ getApiBaseUrl: () => 'http://api.test' }));

const { POST } = await import('./+server');

type Event = Parameters<typeof POST>[0];

const call = (fetcher: typeof fetch, body: unknown = { partners: [] }) =>
  POST({
    request: new Request('http://web.test/api/bazi', { method: 'POST', body: JSON.stringify(body) }),
    fetch: fetcher
  } as unknown as Event);

describe('POST /api/bazi', () => {
  it('answers 502 when the API is unreachable', async () => {
    const failing = (async () => {
      throw new TypeError('fetch failed');
    }) as unknown as typeof fetch;
    expect((await call(failing)).status).toBe(502);
  });

  it('passes the body to the API and its answer back', async () => {
    let target = '';
    const fetcher = (async (url: string) => {
      target = url;
      return new Response(JSON.stringify({ tone: 'balanced' }), { status: 200 });
    }) as unknown as typeof fetch;
    const response = await call(fetcher);
    expect(target).toBe('http://api.test/api/v1/public/bazi');
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ tone: 'balanced' });
  });

  it('rejects a body that is not an object', async () => {
    const never = (async () => new Response('{}')) as unknown as typeof fetch;
    expect((await call(never, 'nope')).status).toBe(400);
  });
});
