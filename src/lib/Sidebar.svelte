<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import type { Artwork } from "./api";

  const dispatch = createEventDispatcher<{ close: void }>();

  export let artwork: Artwork;
</script>

<div class="text-stone-200 p-6">
  <div class="flex justify-end mb-4">
    <button
      on:click={() => dispatch("close")}
      class="p-1 rounded-md hover:bg-stone-800"
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="feather feather-x"
        ><line x1="18" y1="6" x2="6" y2="18" /><line
          x1="6"
          y1="6"
          x2="18"
          y2="18"
        /></svg
      >
    </button>
  </div>

  <div class="mb-8">
    <h2 class="text-2xl fontvar-heading mb-1">{artwork.title}</h2>
    <p class="text-stone-500">{artwork.objectnumber}</p>

    <a
      href={artwork.url}
      target="_blank"
      rel="noopener noreferrer"
      class="inline-block px-2.5 py-1 bg-stone-800 hover:bg-stone-700 rounded-md mt-4"
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="inline -mt-1 mr-1 feather feather-external-link"
        ><path
          d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"
        /><polyline points="15 3 21 3 21 9" /><line
          x1="10"
          y1="14"
          x2="21"
          y2="3"
        /></svg
      >
      View Source
    </a>
  </div>

  <dl>
    <dt>
      Artist{#if artwork.people.length > 1}s{/if}
    </dt>
    <dd>
      {#each artwork.people as name}<p>{name}</p>{:else}None{/each}
    </dd>

    <dt>Date</dt>
    <dd>{artwork.dated}</dd>

    {#if artwork.description?.trim()}
      <dt>Description</dt>
      <dd class="whitespace-pre-wrap">{artwork.description}</dd>
    {/if}

    {#if artwork.labeltext?.trim()}
      <dt>Label Text</dt>
      <dd class="whitespace-pre-wrap">{artwork.labeltext}</dd>
    {/if}

    <dt>Museum Department</dt>
    <dd>{artwork.department}</dd>

    {#if artwork.division}
      <dt>Museum Division</dt>
      <dd>{artwork.division}</dd>
    {/if}

    {#if artwork.culture}
      <dt>Culture</dt>
      <dd>{artwork.culture}</dd>
    {/if}

    <dt>Technique / Medium</dt>
    <dd>
      {#if artwork.technique && artwork.medium}
        {artwork.technique} / {artwork.medium}
      {:else if artwork.technique}
        {artwork.technique}
      {:else if artwork.medium}
        {artwork.medium}
      {:else}
        N/A
      {/if}
    </dd>

    <dt>Classification</dt>
    <dd>{artwork.classification}</dd>

    <dt>Dimensions</dt>
    <dd class="whitespace-pre-wrap">{artwork.dimensions}</dd>

    {#if artwork.accessionyear}
      <dt>Accession Year</dt>
      <dd>{artwork.accessionyear}</dd>
    {/if}

    {#if artwork.copyright}
      <dt>Copyright</dt>
      <dd>{artwork.copyright}</dd>
    {/if}

    <dt>Credits</dt>
    <dd>{artwork.creditline}</dd>
  </dl>
</div>

<style lang="postcss">
  dt {
    @apply text-xs font-semibold uppercase text-stone-400;
  }

  dd {
    @apply text-stone-300 text-sm;
  }

  dd:not(:last-of-type) {
    @apply mb-5;
  }
</style>
