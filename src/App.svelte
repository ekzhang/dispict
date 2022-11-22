<script lang="ts">
  import ArtSearch from "./lib/ArtSearch.svelte";
  import Welcome from "./lib/Welcome.svelte";

  const navigationType = (
    window.performance.getEntriesByType(
      "navigation"
    )[0] as PerformanceNavigationTiming
  )?.type;

  let welcome = !navigationType || navigationType === "navigate";
</script>

<Welcome open={welcome} on:close={() => (welcome = false)} />

<main class="max-w-screen-md mx-auto px-4 py-8">
  <h1 class="text-4xl mb-4">
    <button class="fontvar-heading" on:click={() => (welcome = true)}
      >dispict</button
    >
    <span class="text-gray-400 text-xl">(tech preview)</span>
  </h1>

  <p class="text-pink-700 border-l-4 border-pink-200 pl-3">
    where is the actual UI, there is no UI yet, graphic design takes time, but
    there will be a UI in the future I promise and it will be glorious –Eric
  </p>

  <div class="py-6">
    <ArtSearch />
  </div>
</main>
