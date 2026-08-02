<script lang="ts">
  import { onMount, untrack } from 'svelte';

  /**
   * Quill wrapper for article bodies.
   *
   * The HTML is mirrored into a hidden input so the surrounding <form> posts it
   * like any other field -- no client-side submit handler required. Quill is
   * imported dynamically because it touches `document` at module scope and
   * would break server rendering.
   */
  let {
    value = '',
    name = 'content',
    id = 'content',
    uploadUrl = ''
  }: {
    value?: string;
    name?: string;
    id?: string;
    /** POST target for inline images. Without it the image button is hidden. */
    uploadUrl?: string;
  } = $props();

  let uploading = $state(false);
  let uploadError = $state('');

  let host = $state<HTMLDivElement>();
  // The prop seeds the editor once; Quill owns the content from then on.
  let html = $state(untrack(() => value));

  // Quill's default image handler inlines the file as a base64 data URI, which
  // would store the whole image inside the article HTML. Upload it instead and
  // insert the resulting URL.
  function pickAndUploadImage() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file || !quillInstance) return;

      uploading = true;
      uploadError = '';
      try {
        const body = new FormData();
        body.set('file', file);
        const response = await fetch(uploadUrl, { method: 'POST', body });
        if (!response.ok) {
          uploadError = 'Upload failed. Try a smaller image or check storage settings.';
          return;
        }
        const { url } = (await response.json()) as { url: string };
        const range = quillInstance.getSelection(true);
        quillInstance.insertEmbed(range?.index ?? 0, 'image', url, 'user');
        html = quillInstance.root.innerHTML;
      } catch {
        uploadError = 'Upload failed. Check your connection and try again.';
      } finally {
        uploading = false;
      }
    };
    input.click();
  }

  let quillInstance: {
    root: HTMLElement;
    getSelection: (focus?: boolean) => { index: number } | null;
    insertEmbed: (index: number, type: string, value: string, source?: string) => void;
  } | undefined;

  onMount(() => {
    let quill: { root: HTMLElement; on: (e: string, cb: () => void) => void } | undefined;

    (async () => {
      const { default: Quill } = await import('quill');
      if (!host) return;

      quill = new Quill(host, {
        theme: 'snow',
        modules: {
          toolbar: {
            container: [
              [{ header: [2, 3, false] }],
              ['bold', 'italic', 'underline'],
              [{ list: 'ordered' }, { list: 'bullet' }],
              ['blockquote', 'link', ...(uploadUrl ? ['image'] : [])],
              ['clean']
            ],
            handlers: uploadUrl ? { image: pickAndUploadImage } : {}
          }
        }
      }) as never;

      const instance = quill as unknown as {
        root: HTMLElement;
        on: (event: string, cb: () => void) => void;
        getSelection: (focus?: boolean) => { index: number } | null;
        insertEmbed: (index: number, type: string, value: string, source?: string) => void;
      };
      quillInstance = instance;
      instance.root.innerHTML = value ?? '';
      instance.on('text-change', () => {
        html = instance.root.innerHTML;
      });
    })();
  });
</script>

<div class="rounded-md border bg-background">
  <div bind:this={host} {id} class="min-h-72"></div>
</div>
{#if uploading}
  <p class="mt-2 text-xs text-muted-foreground">Uploading image…</p>
{/if}
{#if uploadError}
  <p class="mt-2 text-xs font-medium text-destructive">{uploadError}</p>
{/if}
<input type="hidden" {name} value={html} />

<style>
  /* Quill's snow theme zeroes paragraph margins, so body text renders as one
     dense block and is hard to read while editing. Restore spacing that roughly
     matches the public article layout. :global is required because Quill builds
     this DOM itself, outside Svelte's scoping. */
  :global(.ql-editor) {
    font-size: 15px;
    line-height: 1.7;
    padding: 16px 18px;
  }

  :global(.ql-editor p) {
    margin-bottom: 0.9em;
  }

  :global(.ql-editor p:last-child) {
    margin-bottom: 0;
  }

  :global(.ql-editor h2),
  :global(.ql-editor h3) {
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    line-height: 1.3;
    font-weight: 600;
  }

  :global(.ql-editor h2:first-child),
  :global(.ql-editor h3:first-child) {
    margin-top: 0;
  }

  :global(.ql-editor ul),
  :global(.ql-editor ol) {
    margin-bottom: 0.9em;
  }

  :global(.ql-editor li) {
    margin-bottom: 0.3em;
  }

  :global(.ql-editor blockquote) {
    margin: 1em 0;
    padding-left: 1em;
    border-left: 3px solid var(--border);
    color: var(--muted-foreground);
  }

  :global(.ql-editor img) {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    margin: 0.6em 0;
  }
</style>
