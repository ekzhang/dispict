/** @file Keeps track of images that have been loaded by the browser. */

import {
  derived,
  get,
  writable,
  type Readable,
  type Writable,
} from "svelte/store";

class MultisizeImage {
  url: string;
  widths: Writable<Map<number, string>>;

  constructor(url: string) {
    this.url = url;
    this.widths = writable(new Map());
  }

  /** Attempt to load images of a certain width, with retries. */
  load(width: number, retries = 5) {
    console.log("hello starting", this.url, width, retries);
    if (get(this.widths).has(width)) return;
    console.log("constructing image", this.url, width, retries);
    (async () => {
      try {
        const resp = await fetch(`${this.url}?width=${width}`);
        if (resp.status !== 200) {
          throw new Error(resp.statusText);
        }
        const blob = await resp.blob();
        this.widths.update(($widths) => {
          if (!$widths.has(width)) {
            $widths.set(width, URL.createObjectURL(blob));
          }
          return $widths;
        });
      } catch (error) {
        console.log("error: retrying", this.url, width, retries);
        if (retries > 0) {
          this.load(width, retries - 1);
        }
      }
    })();
  }

  /**
   * Reactive store for the blob URL with closest width to the requested one,
   * falling back on other sizes if necessary.
   */
  closestWidth(width: number): Readable<string | null> {
    return derived(this.widths, ($widths) => {
      let best: number | null = null;
      for (const w of $widths.keys()) {
        if (
          best === null ||
          (w >= width && (best < width || w < best)) ||
          (w < width && w > best)
        ) {
          best = w;
        }
      }
      return best ? $widths.get(best)! : null;
    });
  }
}

class ImageStore {
  /** Map of image URLs to a set of loaded "detail" strings. */
  map: Map<string, MultisizeImage>;

  constructor() {
    this.map = new Map();
  }

  /**
   * Request an image of a particular width, returning a store based on when it
   * loads and any previously-loaded sizes of this image.
   */
  requestSize(url: string, width: number): Readable<string | null> {
    let img = this.map.get(url);
    if (!img) {
      img = new MultisizeImage(url);
      this.map.set(url, img);
    }
    img.load(width);
    return img.closestWidth(width);
  }
}

export default ImageStore;
