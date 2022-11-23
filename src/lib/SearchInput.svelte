<script lang="ts">
  export let value: string = "";
  export let searching: boolean = false;

  function handleKeydown(event: KeyboardEvent) {
    if (event.ctrlKey || event.metaKey) {
      // Disable formatting shortcuts.
      if (["b", "i", "u"].includes(event.key)) {
        event.preventDefault();
      }
    }
  }

  function handlePaste(event: ClipboardEvent) {
    event.preventDefault();
    var text = event.clipboardData.getData("text/plain");
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    range.deleteContents();
    range.insertNode(document.createTextNode(text));
    range.collapse();
  }
</script>

<div
  class="relative w-80 max-h-[200px] rounded z-10 bg-white border border-gray-100
  shadow hover:shadow-md transition-shadow overflow-y-auto"
  on:mousedown={(event) => event.stopPropagation()}
  on:touchstart={(event) => event.stopPropagation()}
  on:dblclick={(event) => event.stopPropagation()}
>
  <!-- svelte-ignore a11y-autofocus -->
  <div
    contenteditable
    autofocus
    class="search"
    bind:textContent={value}
    on:keydown={handleKeydown}
    on:paste={handlePaste}
  />

  {#if searching}
    <div
      class="absolute right-1.5 bottom-1.5 animate-spin pointer-events-none text-gray-400"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="feather feather-loader"
        ><line x1="12" y1="2" x2="12" y2="6" /><line
          x1="12"
          y1="18"
          x2="12"
          y2="22"
        /><line x1="4.93" y1="4.93" x2="7.76" y2="7.76" /><line
          x1="16.24"
          y1="16.24"
          x2="19.07"
          y2="19.07"
        /><line x1="2" y1="12" x2="6" y2="12" /><line
          x1="18"
          y1="12"
          x2="22"
          y2="12"
        /><line x1="4.93" y1="19.07" x2="7.76" y2="16.24" /><line
          x1="16.24"
          y1="7.76"
          x2="19.07"
          y2="4.93"
        /></svg
      >
    </div>
  {/if}
</div>

<style lang="postcss">
  .search {
    @apply font-serif italic text-2xl text-center outline-none p-5;
  }

  .search:empty::before {
    content: "what do you envision?";
    @apply text-gray-400;
  }

  [contenteditable] :global b {
    font-weight: inherit;
  }

  [contenteditable] :global i {
    font-style: inherit;
  }

  [contenteditable] :global img {
    display: none;
  }
</style>
