<script lang="ts">
  import Dropzone from 'dropzone';
  import 'dropzone/dist/dropzone.css';
  import ImagePlusIcon from '@lucide/svelte/icons/image-plus';

  let {
    tempVenueId,
    uploadUrl = '/venues/photo-upload',
    onCountChange
  }: {
    tempVenueId: string;
    uploadUrl?: string;
    onCountChange?: (count: number) => void;
  } = $props();

  let el: HTMLDivElement;
  let uploaded = $state(0);
  let failed = $state(0);

  $effect(() => {
    Dropzone.autoDiscover = false;
    const dz = new Dropzone(el, {
      url: uploadUrl,
      paramName: 'file',
      maxFilesize: 10, // MB
      acceptedFiles: 'image/*',
      addRemoveLinks: true,
      parallelUploads: 3,
      timeout: 120000,
      params: { temp_venue_id: tempVenueId },
      dictDefaultMessage: '',
      dictRemoveFile: 'Remove',
      dictFileTooBig: 'Image is larger than 10MB.',
      dictInvalidFileType: 'Only image files are allowed.'
    });

    dz.on('success', () => {
      uploaded += 1;
      onCountChange?.(uploaded);
    });
    dz.on('error', (file, message) => {
      failed += 1;
      const node = file.previewElement?.querySelector('[data-dz-errormessage]');
      if (node) node.textContent = typeof message === 'string' ? message : 'Upload failed';
    });
    dz.on('removedfile', (file) => {
      if (file.status === 'success') {
        uploaded = Math.max(0, uploaded - 1);
        onCountChange?.(uploaded);
      }
    });

    return () => dz.destroy();
  });
</script>

<div
  bind:this={el}
  class="dropzone group relative flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/30 p-6 text-center transition hover:border-brand hover:bg-muted/50"
>
  <div class="dz-message pointer-events-none flex flex-col items-center gap-2">
    <span
      class="flex size-11 items-center justify-center rounded-full bg-brand/10 text-brand"
    >
      <ImagePlusIcon class="size-5" />
    </span>
    <p class="text-sm font-medium">Drop venue photos here</p>
    <p class="text-xs text-muted-foreground">or click to browse · JPG / PNG / WebP up to 10MB</p>
  </div>
</div>

{#if uploaded > 0 || failed > 0}
  <p class="mt-3 text-xs text-muted-foreground">
    {#if uploaded > 0}
      <span class="font-medium text-emerald-600">{uploaded} uploaded</span>
    {/if}
    {#if failed > 0}
      <span class="ml-2 font-medium text-destructive">{failed} failed</span>
    {/if}
    — photos attach to the venue when you click <span class="font-medium">Create venue</span>.
  </p>
{/if}

<style>
  /* Tame Dropzone's default look so it fits the shadcn theme. */
  :global(.dropzone .dz-preview .dz-image) {
    border-radius: 0.5rem;
  }
  :global(.dropzone .dz-preview .dz-error-message) {
    background: var(--destructive, #b42318);
  }
</style>
