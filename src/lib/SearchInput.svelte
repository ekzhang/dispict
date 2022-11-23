<script lang="ts">
  export let value: string = "";

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
  class="w-80 max-h-[200px] rounded z-10 bg-white border border-gray-100 shadow hover:shadow-md transition-shadow overflow-y-auto"
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
