<script lang="ts">
  import { onMount } from "svelte";
  import { cubicOut } from "svelte/easing";
  import { fade, fly } from "svelte/transition";
  import panzoom, { type PanZoom } from "panzoom";
  import debounce from "lodash.debounce";

  import SearchInput from "./SearchInput.svelte";
  import Sidebar from "./Sidebar.svelte";
  import { loadSuggestions, type Artwork, type SearchResult } from "./api";
  import { layoutArtwork } from "./geometry";

  export let active: boolean;

  const PIXELS_PER_CM = 5;
  const SIDEBAR_WIDTH = 420;

  const STARTER_INPUTS = [
    "bright landscape",
    "drawing with freedom",
    "abstract painting",
    "muslim religious imagery",
    "everything I see is green",
    "friendship",
    "sunset over the ocean",
    "sturm und drang",
    "delicious fruit",
    "pablo picasso",
    "tokugawa japan",
    "turbulent waves",
    "tranquility",
    "vivid dreams",
    "baby jesus",
    "the light of god",
  ];

  let query = STARTER_INPUTS[Math.floor(Math.random() * STARTER_INPUTS.length)]; // @hmr:keep

  let frame: HTMLDivElement;
  let panzoomInstance: PanZoom;
  let moving = false;
  let lastPanzoom = 0;

  let selected: Artwork | null = null;

  onMount(() => {
    panzoomInstance = panzoom(frame, {
      zoomSpeed: 0.1,
      minZoom: 0.2,
      maxZoom: 10,
    });
    panzoomInstance.on("panstart", () => {
      (document.activeElement as HTMLElement).blur();
      moving = true;
      selected = null;
    });
    panzoomInstance.on("panend", () => {
      moving = false;
      lastPanzoom = Date.now();
    });
    panzoomInstance.on("zoom", () => {
      lastPanzoom = Date.now();
      selected = null;
    });
  });

  $: if (panzoomInstance) {
    if (active) panzoomInstance.resume();
    else panzoomInstance.pause();
  }

  /** Handle when an artwork is selected for more details. */
  function handleSelect(artwork: Artwork, position: [number, number]) {
    // Hack to prevent click events after panning is finished.
    if (!moving && lastPanzoom < Date.now() - 30) {
      const transform = panzoomInstance.getTransform();
      panzoomInstance.smoothMoveTo(
        -0.5 * frame.clientWidth * (transform.scale - 1) -
          transform.scale * PIXELS_PER_CM * position[0] -
          SIDEBAR_WIDTH / 2,
        -0.5 * frame.clientHeight * (transform.scale - 1) -
          transform.scale * PIXELS_PER_CM * position[1]
      );
      selected = artwork;
    }
  }

  let results: SearchResult[] = [];
  let searching = 0;
  let abortController = new AbortController();

  async function updateResults(query: string) {
    selected = null;
    searching++;
    abortController.abort();
    const ctrl = new AbortController();
    abortController = ctrl;
    results = [];
    try {
      if (!query) return;
      results = await loadSuggestions(query, 64, ctrl.signal);
    } catch (error: any) {
      if (!ctrl.signal.aborted) {
        alert("an error occured: " + error.toString());
      }
    } finally {
      searching--;
    }
  }

  const updateResultsDebounced = debounce(updateResults, 150);
  $: updateResultsDebounced(query);

  $: positions = layoutArtwork(results.map((r) => r.artwork));
</script>

<main class="absolute inset-0 overflow-hidden bg-gray-50">
  <div class="w-full h-full flex justify-center items-center" bind:this={frame}>
    <SearchInput bind:value={query} searching={searching > 0} />

    {#each results as result, i (result)}
      <div
        class="absolute"
        transition:fade
        style:transform="translate(
        {positions[i][0] * PIXELS_PER_CM}px,
        {positions[i][1] * PIXELS_PER_CM}px)"
      >
        <button
          class="cursor-default"
          on:click={() => handleSelect(result.artwork, positions[i])}
          on:touchend={() => handleSelect(result.artwork, positions[i])}
        >
          <img
            class="inline-block object-contain bg-gray-100 rainbow-hover-border transition-opacity"
            class:grayed={selected && selected !== result.artwork}
            style:width="{result.artwork.dimwidth * PIXELS_PER_CM}px"
            style:height="{result.artwork.dimheight * PIXELS_PER_CM}px"
            src={result.artwork.image_url + "?width=800"}
            alt={result.artwork.title}
          />
        </button>
      </div>
    {/each}
  </div>
</main>

{#if selected}
  <aside
    class="absolute z-20 inset-y-0 right-0 bg-stone-900 shadow-2xl overflow-y-auto"
    style:width="calc(min(100vw, {SIDEBAR_WIDTH}px))"
    transition:fly={{ x: SIDEBAR_WIDTH, y: 0, duration: 300, easing: cubicOut }}
  >
    <Sidebar artwork={selected} on:close={() => (selected = null)} />
  </aside>
{/if}

<style lang="postcss">
  .rainbow-hover-border {
    border: 3px solid transparent;
    box-sizing: content-box;
  }
  .rainbow-hover-border:hover {
    border-image: repeating-linear-gradient(
      to bottom right,
      #b827fc 0%,
      #2c90fc 12.5%,
      #b8fd33 25%,
      #fec837 37.5%,
      #fd1892 50%
    );
    border-image-slice: 1;
  }

  .grayed {
    opacity: 0.4;
  }
</style>
