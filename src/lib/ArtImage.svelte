<script lang="ts" context="module">
  import ImageStore from "./ImageStore";

  const imageStore = new ImageStore();
</script>

<script lang="ts">
  import type { Artwork } from "./api";
  import { PIXELS_PER_CM } from "./geometry";

  // This is a transparent 1x1 PNG, used as a placeholder for images that are
  // still loading.
  const TRANSPARENT_PNG =
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=";

  export let artwork: Artwork;
  export let detail: number;
  export let grayed = false;

  $: blobUrl = imageStore.requestSize(artwork.image_url, detail);
</script>

<img
  class="inline-block object-contain bg-gray-100 rainbow-hover-border transition-opacity"
  class:grayed
  style:width="{artwork.dimwidth * PIXELS_PER_CM}px"
  style:height="{artwork.dimheight * PIXELS_PER_CM}px"
  draggable="false"
  src={$blobUrl ?? TRANSPARENT_PNG}
  alt={artwork.title}
  on:error={() => {}}
/>

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
