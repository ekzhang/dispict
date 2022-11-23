<script lang="ts">
  import { fade } from "svelte/transition";

  import SearchInput from "./SearchInput.svelte";
  import { loadSuggestions, type SearchResult } from "./api";
  import { layoutArtwork } from "./geometry";

  export let active: boolean;

  $: _ = active;

  const PIXELS_PER_CM = 5;

  let query = ""; // @hmr:keep

  let results: SearchResult[] = [];
  let searching = 0;
  let abortController = new AbortController();

  async function updateResults(query: string) {
    if (!query) {
      results = [];
      return;
    }
    searching++;
    abortController.abort();
    const ctrl = new AbortController();
    abortController = ctrl;
    results = [];
    try {
      results = await loadSuggestions(query, undefined, ctrl.signal);
    } catch (error: any) {
      if (!ctrl.signal.aborted) {
        alert("an error occured: " + error.toString());
      }
    } finally {
      searching--;
    }
  }

  $: updateResults(query);
  $: positions = layoutArtwork(results.map((r) => r.artwork));
</script>

<main
  class="absolute inset-0 cursor-crosshair overflow-hidden flex justify-center items-center bg-gray-50"
>
  <SearchInput bind:value={query} searching={searching > 0} />

  {#each results.slice(0, 50) as result, i (result)}
    <div
      class="absolute"
      transition:fade
      style:transform="translate(
      {positions[i][0] * PIXELS_PER_CM}px,
      {positions[i][1] * PIXELS_PER_CM}px)"
    >
      <a href={result.artwork.url}>
        <img
          class="inline-block object-contain bg-gray-100 hover:ring hover:ring-black"
          style:width="{result.artwork.dimwidth * PIXELS_PER_CM}px"
          style:height="{result.artwork.dimheight * PIXELS_PER_CM}px"
          src={result.artwork.image_url + "?width=800"}
          alt={result.artwork.title}
        />
      </a>
    </div>
  {/each}
</main>
