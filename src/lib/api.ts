// See main.py for the source of this type.
export type Artwork = {
  id: number;
  objectnumber: string;
  url: string;
  image_url: string;

  dimensions: string;
  dimheight: number;
  dimwidth: number;

  title: string | null;
  description: string | null;
  labeltext: string | null;
  people: string[];
  dated: string;
  datebegin: number;
  dateend: number;
  century: string | null;

  department: string;
  division: string | null;
  culture: string | null;
  classification: string;
  technique: string | null;
  medium: string | null;

  accessionyear: number | null;
  verificationlevel: number;
  totaluniquepageviews: number;
  totalpageviews: number;

  copyright: string | null;
  creditline: string;
};

export type SearchResult = {
  score: number;
  artwork: Artwork;
};

const API_URL =
  import.meta.env.VITE_APP_API_URL ??
  "https://ekzhang-dispict-suggestions.modal.run/";

/** Queries the dispict backend API for artwork matching a text phrase. */
export async function loadSuggestions(
  text: string,
  n?: number
): Promise<SearchResult[]> {
  let url = API_URL + "?text=" + encodeURIComponent(text);
  if (n) url += "&n=" + n;
  const resp = await fetch(url);
  return await resp.json();
}
