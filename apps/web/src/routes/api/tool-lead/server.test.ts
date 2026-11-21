import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/api', () => ({ getApiBaseUrl: () => 'http://api.test' }));
vi.mock('$lib/server/api', () => ({ leadHeaders: () => ({ 'Content-Type': 'application/json' }) }));
vi.mock('$lib/server/turnstile', () => ({ rejectUnlessHuman: async () => null }));

const { POST } = await import('./+server');

type Event = Parameters<typeof POST>[0];

async function forward(body: unknown) {
  let seen: { url: string; body: unknown } | undefined;
  const fetcher = (async (url: string, init: RequestInit) => {
    seen = { url, body: JSON.parse(String(init.body)) };
    return new Response(JSON.stringify({ ok: true }), { status: 201 });
  }) as unknown as typeof fetch;
  const response = await POST({
    request: new Request('http://web.test/api/tool-lead', { method: 'POST', body: JSON.stringify(body) }),
    fetch: fetcher
  } as unknown as Event);
  return { response, seen };
}

describe('POST /api/tool-lead', () => {
  it('sends a mahar or hashtag lead to the shared endpoint', async () => {
    const { response, seen } = await forward({ tool: 'mahar', email: 'a@example.com' });
    expect(seen?.url).toBe('http://api.test/api/v1/public/tool-leads');
    expect(response.status).toBe(201);
  });

  it('sends a Ba Zi lead, calculation included, to the endpoint that emails the result', async () => {
    const body = { tool: 'bazi', email: 'a@example.com', calculation: { partners: [], dates: [], locale: 'id' } };
    const { seen } = await forward(body);
    expect(seen?.url).toBe('http://api.test/api/v1/public/bazi/leads');
    expect(seen?.body).toEqual(body);
  });
});
