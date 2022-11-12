<script lang="ts">
  import { loadSuggestions, type SearchResult } from "./api";

  let query: string = "";
  let searching = false;
  let results: SearchResult[] = [];

  async function submit() {
    searching = true;
    try {
      results = await loadSuggestions(query);
    } catch (error: any) {
      alert("an error occured: " + error.toString());
    } finally {
      searching = false;
    }
  }
</script>

<form on:submit|preventDefault={submit} class="mb-12">
  <input
    class="border hover:border-gray-400 transition-colors px-2 py-1 w-60"
    placeholder="creative aesthetics tool"
    bind:value={query}
  />
  <button
    class="border hover:border-gray-400 disabled:opacity-60 transition-colors px-2 py-1"
    type="submit"
    disabled={searching}>Search</button
  >
</form>

<div class="space-y-4">
  {#each results.slice(0, 40) as result}
    <div class="py-2">
      <a href={result.artwork.url}>
        <img
          class="max-w-[min(36rem,100%)]"
          src={result.artwork.image_url}
          alt={result.artwork.title}
        />
      </a>
      <p class="py-4 text-medium">
        {result.artwork.title} ({result.artwork.dated})
      </p>
    </div>
  {/each}
</div>
