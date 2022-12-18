<script lang="ts">
  import { onMount } from "svelte";
  import { cubicOut } from "svelte/easing";
  import { fade, fly } from "svelte/transition";
  import debounce from "lodash.debounce";

  import SearchInput from "./SearchInput.svelte";
  import Sidebar from "./Sidebar.svelte";
  import { loadSuggestions, type Artwork, type SearchResult } from "./api";
  import { layoutArtwork } from "./geometry";
  import { TouchZoom } from "./touchZoom";

  const PIXELS_PER_CM = 8;
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
    "rainbow dreams",
    "urban planning",
    "oil paint flowers",
    "tender arguments",
  ];

  function randomInput(exclude?: string) {
    while (true) {
      const value =
        STARTER_INPUTS[Math.floor(Math.random() * STARTER_INPUTS.length)];
      if (value !== exclude) return value;
    }
  }

  let query = randomInput(); // @hmr:keep

  let frame: HTMLDivElement;
  let touchZoom: TouchZoom;
  let center = [0, 0];
  let zoom = 1;
  let lastMove = 0;

  let selected: Artwork | null = null;

  onMount(() => {
    touchZoom = new TouchZoom(frame);
    touchZoom.onMove((manual) => {
      center = touchZoom.center;
      zoom = touchZoom.zoom;
      if (manual) {
        if (document.activeElement instanceof HTMLElement) {
          document.activeElement.blur();
        }
        lastMove = Date.now();
        selected = null;
      }
    });
  });

  function getTransform(pos: number[], center: number[], zoom: number): string {
    return `scale(${(zoom * 100).toFixed(3)}%) translate(
      ${pos[0] * PIXELS_PER_CM - center[0]}px,
      ${pos[1] * PIXELS_PER_CM - center[1]}px
    )`;
  }

  /** Adaptively adjust image size based on visibility and screen size. */
  function getDetail(
    artwork: Artwork,
    pos: number[],
    center: number[],
    zoom: number
  ): string {
    const pxBounding = [
      zoom * ((pos[0] - artwork.dimwidth / 2) * PIXELS_PER_CM - center[0]),
      zoom * ((pos[0] + artwork.dimwidth / 2) * PIXELS_PER_CM - center[0]),
      zoom * ((pos[1] - artwork.dimheight / 2) * PIXELS_PER_CM - center[1]),
      zoom * ((pos[1] + artwork.dimheight / 2) * PIXELS_PER_CM - center[1]),
    ];
    const windowSize = [
      -frame.clientWidth / 2,
      frame.clientWidth / 2,
      -frame.clientHeight / 2,
      frame.clientHeight / 2,
    ];
    const physicalWidth =
      window.devicePixelRatio * zoom * artwork.dimwidth * PIXELS_PER_CM;
    // Not visible, outside the window.
    if (
      pxBounding[0] > 1.15 * windowSize[1] ||
      pxBounding[1] < 1.15 * windowSize[0] ||
      pxBounding[2] > 1.15 * windowSize[3] ||
      pxBounding[3] < 1.15 * windowSize[2]
    ) {
      return "?width=400";
    } else if (physicalWidth < 400) {
      return "?width=400";
    } else if (physicalWidth < 800) {
      return "?width=800";
    } else {
      return "";
    }
  }

  /** Handle when an artwork is selected for more details. */
  function handleSelect(artwork: Artwork, pos: [number, number]) {
    if (lastMove < Date.now() - 50 && !touchZoom.isPinching) {
      const sidebarOffset =
        frame.clientWidth > SIDEBAR_WIDTH ? SIDEBAR_WIDTH : 0;
      const desiredZoom =
        0.8 *
        Math.min(
          frame.clientHeight / (artwork.dimheight * PIXELS_PER_CM),
          (frame.clientWidth - sidebarOffset) /
            (artwork.dimwidth * PIXELS_PER_CM)
        );

      touchZoom.moveTo(
        [
          pos[0] * PIXELS_PER_CM + (0.5 * sidebarOffset) / desiredZoom,
          pos[1] * PIXELS_PER_CM,
        ],
        desiredZoom
      );
      selected = artwork;
    }
  }

  let results: SearchResult[] = [];
  let apiError: string | null = null;
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
      apiError = null;
    } catch (error: any) {
      if (!ctrl.signal.aborted) {
        apiError = "There was an error finding the artwork.";
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
  <div
    class="w-full h-full flex justify-center items-center touch-none"
    bind:this={frame}
  >
    <div style:transform={getTransform([0, 0], center, zoom)}>
      <SearchInput
        bind:value={query}
        searching={searching > 0}
        on:refresh={() => (query = randomInput(query))}
      />
      {#if apiError}
        <p
          class="absolute text-center w-80 mt-3 p-1 rounded bg-red-500/20 text-red-800"
        >
          {apiError}
        </p>
      {/if}
    </div>

    {#each results as result, i (result)}
      <div
        class="absolute"
        style:transform={getTransform(positions[i], center, zoom)}
        transition:fade
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
            draggable="false"
            src={result.artwork.image_url +
              getDetail(result.artwork, positions[i], center, zoom)}
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
    border: 3px solid theme("colors.gray.50");
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
