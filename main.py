import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Optional

import modal
import numpy as np

stub = modal.Stub("dispict")

stub.image = modal.Image.debian_slim().pip_install(["numpy"])

stub.clip_image = (
    modal.Image.debian_slim()
    .apt_install(["git"])
    .pip_install(["ftfy", "regex", "tqdm", "numpy", "torch"])
    .pip_install(["git+https://github.com/openai/CLIP.git"])
)

sv = modal.SharedVolume().persist("clip-cache")

if stub.is_inside(stub.clip_image):
    import clip
    import torch

    model, preprocess = clip.load("ViT-B/32")
    model.eval()


@stub.function(
    image=stub.clip_image,
    shared_volumes={"/root/.cache": sv},
    concurrency_limit=20,
    keep_warm=True,
)
def run_clip_text(texts: list[str]):
    """Run pretrained CLIP on a list of texts.

    Returns a numpy array containing the concatenated 512-dimensional embedding
    outputs for each provided input, evaluated as a batch.
    """
    text_tokens = clip.tokenize(texts, truncate=True)
    with torch.no_grad():
        return model.encode_text(text_tokens).float().numpy()


@stub.function(
    image=stub.clip_image,
    shared_volumes={"/root/.cache": sv},
    concurrency_limit=20,
)
def run_clip_images(image_urls: list[str]):
    """Run pretrained CLIP on a list of image URLs.

    Returns a numpy array containing the concatenated 512-dimensional embedding
    outputs for each provided input, evaluated as a batch.

    The first return value is a list of indices that had an error during fetch.
    """
    from io import BytesIO
    from concurrent.futures import ThreadPoolExecutor

    import requests
    from PIL import Image, UnidentifiedImageError

    def get_with_retry(url: str) -> requests.Response:
        request_num = 0
        while request_num < 5:
            try:
                resp = requests.get(url, timeout=8)
            except requests.exceptions.RequestException as exc:
                print("Retrying", url, "due to", exc)
                request_num += 1
                time.sleep(3.0)
                continue
            if resp.status_code not in (200, 403, 404):
                print("Retrying", url, "due to status code", resp.status_code)
                request_num += 1
                time.sleep(0.1)
            else:
                return resp
        return resp  # type: ignore

    with ThreadPoolExecutor(max_workers=10) as executor:
        responses = list(executor.map(get_with_retry, image_urls))

    missing_indices: list[int] = []
    original_images: list[Image.Image] = []
    for i, resp in enumerate(responses):
        if resp.status_code != 200:
            print(f"Received status code {resp.status_code} from URL:", image_urls[i])
            missing_indices.append(i)
            continue
        try:
            original_images.append(Image.open(BytesIO(resp.content)))
        except UnidentifiedImageError:
            print("Failed to load image from URL:", image_urls[i])
            missing_indices.append(i)
    images: list[torch.Tensor] = [preprocess(img) for img in original_images]  # type: ignore
    image_input = torch.stack(images)
    with torch.no_grad():
        return missing_indices, model.encode_image(image_input).float().numpy()


@dataclass
class Artwork:
    id: int
    objectnumber: str
    url: str
    image_url: str

    dimensions: str
    dimheight: float
    dimwidth: float

    title: Optional[str]  # plaintext title
    description: Optional[str]  # plaintext description
    labeltext: Optional[str]  # optional label text
    people: list  # information about artists
    dated: str  # "c. 1950" or "1967-68" or "18th century"
    datebegin: int  # numerical year or 0
    dateend: int  # numerical year or 0
    century: Optional[str]  # alternative to "dated" column

    department: str  # categorical, about a dozen departments
    division: Optional[str]  # modern, european/american, or asian/mediterranean
    culture: Optional[str]  # American, Dutch, German, ...
    classification: str  # Photographs or Prints or ...
    technique: Optional[str]  # Lithograph, Etching, Gelatin silver print, ...
    medium: Optional[str]  # Graphite on paper, Oil on canvas, ...

    accessionyear: Optional[int]  # when the item was added
    verificationlevel: int  # How verified a work is(?)
    totaluniquepageviews: int  # a proxy for popularity
    totalpageviews: int  # a proxy for popularity

    copyright: Optional[str]  # copyright status
    creditline: str  # who donated this artwork


data: list[Artwork] = []
data_by_id: dict[int, Artwork] = {}


def populate_data(filename: str) -> None:
    global data, data_by_id
    if not data:
        with open(filename, "r") as f:
            data = [Artwork(**row) for row in json.load(f)]
        for row in data:
            data_by_id[row.id] = row


embeddings: Optional[np.ndarray] = None  # [n_images, n_features]
embeddings_ids: list[int] = []


def populate_embeddings(filename: str) -> None:
    global embeddings, embeddings_ids
    if embeddings is None:
        with np.load(filename) as npz_file:
            ids = npz_file.files
            embeddings_ids = [int(x) for x in ids]
            embeddings = np.vstack([npz_file[x] for x in ids])
            embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)


@dataclass
class SearchResult:
    score: float
    artwork: Artwork


@stub.webhook(
    mounts=[
        modal.Mount("/data", local_file="data/artmuseums-clean.json"),
        modal.Mount("/data", local_file="data/embeddings.npz"),
    ],
    keep_warm=True,
)
def suggestions(text: str, n: int = 50) -> list[SearchResult]:
    """Return a list of artworks that are similar to the given text."""
    populate_data("/data/artmuseums-clean.json")
    populate_embeddings("/data/embeddings.npz")
    features = run_clip_text([text])[0, :]
    features /= np.linalg.norm(features)
    scores = embeddings @ features  # shape: [n_images]
    indices = np.flip(np.argsort(scores))[:n]
    return [
        SearchResult(score=scores[i], artwork=data_by_id[embeddings_ids[i]])
        for i in indices
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("dispict")
    subparsers = parser.add_subparsers(dest="sub")

    subparsers.add_parser("embed-images")
    subparsers.add_parser("webhook")

    args = parser.parse_args()
    if args.sub == "embed-images":
        populate_data("data/artmuseums-clean.json")

        chunk_size = 32
        chunked_ids = []
        chunked_urls = []
        for idx in range(0, len(data), chunk_size):
            chunked_ids.append([row.id for row in data[idx : idx + chunk_size]])
            chunked_urls.append([row.image_url for row in data[idx : idx + chunk_size]])

        with stub.run():
            results = list(run_clip_images.map(chunked_urls))

        all_embeddings: dict[str, np.ndarray] = {}
        for ids, (missing, embeddings) in zip(chunked_ids, results):
            assert len(ids) == len(missing) + len(embeddings)
            embeddings_idx = 0
            for i, id in enumerate(ids):
                if i not in missing:
                    all_embeddings[str(id)] = embeddings[embeddings_idx, :]
                    embeddings_idx += 1

        print(f"Finished embedding {len(all_embeddings)} images out of {len(data)}")
        np.savez_compressed("data/embeddings.npz", **all_embeddings)

    elif args.sub == "webhook":
        print("Serving webhook at a temporary URL. Use `modal app deploy` to deploy.")
        stub.serve()

    else:
        parser.print_help()
        sys.exit(1)
