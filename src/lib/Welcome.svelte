<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { sineInOut } from "svelte/easing";

  const dispatch = createEventDispatcher<{ close: void }>();

  export let open: boolean;

  let height: number;

  function handleWheel(event: WheelEvent) {
    if (open) {
      event.preventDefault();
      if (event.deltaY > 0) {
        dispatch("close");
      }
    }
  }
</script>

{#if open}
  <div
    class="fixed z-40 inset-6 md:inset-8 rounded-2xl
    backdrop-blur-lg border border-rose-200
    bg-gradient-to-br from-pink-200/75 to-orange-200/75
    flex flex-col justify-between items-center px-4 sm:px-6"
    on:wheel={handleWheel}
    in:fade={{ duration: 200 }}
    out:fly={{ y: -height, duration: 1000, easing: sineInOut }}
    bind:clientHeight={height}
  >
    <div class="py-8">
      <h1 class="text-center text-4xl sm:text-5xl fontvar-heading mb-2 sm:mb-4">
        dispict
      </h1>
      <p class="sm:text-xl">
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://github.com/ekzhang/dispict#readme">details + code</a
        >
        <span class="mx-0.5 sm:mx-1.5">|</span>
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://harvardartmuseums.org">museum</a
        >
        <span class="mx-0.5 sm:mx-1.5">|</span>
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://twitter.com/ekzhang1">author</a
        >
      </p>
    </div>

    <p
      class="tagline text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl text-center"
    >
      A growing <span class="text-[105%] font-serif italic"
        >artistic exhibit</span
      ><br />
      of your <span class="text-[105%] font-serif">own making</span>
    </p>

    <div class="py-10">
      <button
        class="rounded-full px-5 py-2 bg-black text-white text-lg
        hover:bg-white hover:text-black hover:ring-1 hover:ring-black
        active:bg-rose-100 active:text-black active:ring-1 active:ring-black transition-colors"
        on:click={() => dispatch("close")}
      >
        Explore the Gallery
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="inline pb-0.5 ml-1 -mr-1"
          ><line x1="12" y1="5" x2="12" y2="19" /><polyline
            points="19 12 12 19 5 12"
          /></svg
        >
      </button>
    </div>
  </div>
{/if}

<style lang="postcss">
  p.tagline {
    font-variation-settings: "GRAD" 150, "YOPQ" 50, "XTRA" 500, "YTLC" 570;
    @apply tracking-tight;
  }

  a {
    @apply font-light hover:underline hover:decoration-1 hover:underline-offset-2;
  }
</style>
