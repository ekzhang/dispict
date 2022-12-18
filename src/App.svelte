<script lang="ts">
  import ArtSearch from "./lib/ArtSearch.svelte";
  import Welcome from "./lib/Welcome.svelte";

  const navigationType = (
    window.performance.getEntriesByType(
      "navigation"
    )[0] as PerformanceNavigationTiming
  )?.type;

  let welcome = !navigationType || navigationType === "navigate"; // @hmr:keep
</script>

<Welcome open={welcome} on:close={() => (welcome = false)} />

<ArtSearch />

<div class="absolute top-4 left-4 sm:top-8 sm:left-8">
  <button
    class="logo-btn text-3xl fontvar-heading"
    on:click={() => (welcome = true)}>dispict</button
  >
</div>

<style lang="postcss">
  .logo-btn {
    outline: none;
    transition: text-shadow 200ms;
  }

  .logo-btn:hover {
    text-shadow: 0 0 6px rgba(0, 0, 0, 25%);
  }
</style>
