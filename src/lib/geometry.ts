/** @file Geometric layout for an ordered list of rectangles. */

import RBush, { type BBox } from "rbush";

import type { Artwork } from "./api";

const radiusChange = 5;
const angleChange = (Math.sqrt(5) - 1) * Math.PI;
const spaceBuffer = 3;

/**
 * Returns geometric positions (in cm) for the center of each artwork.
 *
 * This places most relevant artwork near the center and less relevant pieces
 * further away, in a spiral pattern. There are no overlaps.
 */
export function layoutArtwork(pieces: Artwork[]): [number, number][] {
  const positions: [number, number][] = [];
  const tree = new RBush<BBox>();
  tree.insert({
    minX: -36,
    minY: -24,
    maxX: 36,
    maxY: 24,
  });
  let iteration = 0;
  for (const artwork of pieces) {
    while (true) {
      const radius = radiusChange * Math.sqrt(iteration);
      const angle = angleChange * iteration;
      const x = radius * Math.cos(angle);
      const y = radius * Math.sin(angle);
      const bbox = {
        minX: x - (artwork.dimwidth + spaceBuffer) / 2,
        minY: y - (artwork.dimheight + spaceBuffer) / 2,
        maxX: x + (artwork.dimwidth + spaceBuffer) / 2,
        maxY: y + (artwork.dimheight + spaceBuffer) / 2,
      };
      if (!tree.collides(bbox)) {
        positions.push([x, y]);
        tree.insert(bbox);
        break;
      }
      iteration++;
    }
    iteration *= 0.5;
  }
  return positions;
}
