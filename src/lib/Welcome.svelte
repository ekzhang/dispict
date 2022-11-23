<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { sineInOut } from "svelte/easing";
  import { spring } from "svelte/motion";

  const dispatch = createEventDispatcher<{ close: void }>();

  export let open: boolean;

  let mouseX = spring<number>(-142);
  let mouseY = spring<number>(-142);
  let height: number;
  let welcomeEl: HTMLDivElement;

  function handleMouse(event: MouseEvent) {
    if ($mouseX == -142) {
      mouseX.set(event.clientX, { hard: true });
      mouseY.set(event.clientY, { hard: true });
    }
    mouseX.set(event.clientX - welcomeEl.offsetLeft);
    mouseY.set(event.clientY - welcomeEl.offsetTop);
  }

  function handleWheel(event: WheelEvent) {
    if (open) {
      event.preventDefault();
      if (event.deltaY > 0) {
        dispatch("close");
      }
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (open) {
      if (["Enter", " ", "Tab", "Escape"].includes(event.key)) {
        event.preventDefault();
        dispatch("close");
      }
    }
  }

  let init = false;
  onMount(() => {
    init = true;
    document.body.addEventListener("keydown", handleKeydown);
    return () => {
      document.body.removeEventListener("keydown", handleKeydown);
    };
  });
</script>

{#if open && $mouseX !== -142}
  <div
    class="fixed z-40 inset-3 sm:inset-6 md:inset-8 rounded-2xl overflow-hidden"
    in:fade={{ duration: 200, delay: 200 }}
    out:fade={{ duration: 150 }}
  >
    <div
      class="radial-gradient relative z-30 w-[360px] h-[360px] rounded-full"
      style:left="{$mouseX}px"
      style:top="{$mouseY}px"
      style:transform="translate(-50%, -50%)"
    />
  </div>
{/if}

{#if open}
  <div
    class="fixed z-40 inset-3 sm:inset-6 md:inset-8 rounded-2xl
    backdrop-blur-lg border border-gray-300 bg-gray-50/75
    flex flex-col justify-between items-center px-4 sm:px-6 overflow-y-auto"
    on:mousemove={handleMouse}
    on:wheel={handleWheel}
    in:fade={{ duration: 200 }}
    out:fly={{ y: -height, duration: 1000, easing: sineInOut }}
    bind:clientHeight={height}
    bind:this={welcomeEl}
  >
    {#if init}
      <div class="py-8">
        <h2
          class="text-center text-4xl sm:text-5xl fontvar-heading mb-2 sm:mb-4"
          in:fade={{ delay: 300 }}
        >
          dispict
        </h2>
        <p class="sm:text-xl" in:fade={{ delay: 600 }}>
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://github.com/ekzhang/dispict#readme">details + code</a
          >
          <span class="mx-1.5">|</span>
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://harvardartmuseums.org">museum</a
          >
          <span class="mx-1.5">|</span>
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://www.ekzhang.com">author</a
          >
        </p>
      </div>

      <p
        class="tagline text-5xl md:text-6xl lg:text-7xl xl:text-8xl text-center"
      >
        <span in:fade={{ delay: 1200 }}
          >A growing <span class="text-[105%] font-serif italic"
            >artistic exhibit</span
          ></span
        ><br />
        <span in:fade={{ delay: 1800 }}
          >of your <span class="text-[105%] font-serif">own making</span></span
        >
      </p>

      <div class="py-10" in:fade={{ delay: 2600 }}>
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
    {/if}
  </div>
{/if}

<style lang="postcss">
  .radial-gradient {
    background: radial-gradient(
      circle at center,
      theme(colors.indigo.600) 0,
      theme(colors.blue.700) 20%,
      theme(colors.green.600) 40%,
      theme(colors.orange.500) 50%,
      theme(colors.pink.500) 60%,
      #ffffff00 100%
    );
    opacity: 60%;
  }

  p.tagline {
    font-variation-settings: "GRAD" 150, "YOPQ" 50, "XTRA" 500, "YTLC" 570;
    @apply tracking-tight;
  }

  a {
    @apply font-light hover:underline hover:decoration-1 hover:underline-offset-2;
  }
</style>
