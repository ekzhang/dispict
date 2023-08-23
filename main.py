"""Deep learning and backend code for dispict.

See the README for more information. You need a Modal account to run this, and
you also need to download the dataset using the notebooks in this repository
first. This program downloads and embeds 25,000 images from the Harvard Art
Museums, then hosts recommendations at a serverless web endpoint.
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from modal import Image, Mount, Stub, web_endpoint

stub = Stub("dispict")

stub.image = Image.debian_slim(python_version="3.11")

def load_clip():
    import clip

    return clip.load("ViT-B/32")

stub.clip_image = (
    stub.image.apt_install("git")
    .pip_install("ftfy", "regex", "tqdm", "numpy", "torch")
    .pip_install("git+https://github.com/openai/CLIP.git")
    .run_function(load_clip)
)

stub.webhook_image = stub.image.pip_install("numpy", "h5py")


if stub.is_inside(stub.clip_image):
    import clip
    import torch

    model, preprocess = load_clip()
    model.eval()


@stub.function(
    image=stub.clip_image,
    concurrency_limit=20,
    keep_warm=1,
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
    people: list[str]  # information about artists
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


def read_data(filename: str) -> list[Artwork]:
    with open(filename, "r") as f:
        return [Artwork(**row) for row in json.load(f)]


def read_embeddings(filename: str):
    import h5py

    print("Loading embeddings")
    with h5py.File(filename, "r") as f:
        ids: h5py.Dataset = f["ids"]  # type: ignore
        matrix: h5py.Dataset = f["embeddings"]  # type: ignore
        embeddings = np.array(matrix)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings_ids = list(ids)
    print("Finished loading embeddings")
    return embeddings, embeddings_ids


@dataclass
class SearchResult:
    score: float
    artwork: Artwork


if stub.is_inside(stub.webhook_image):
    data = read_data("/data/catalog.json")
    data_by_id: dict[int, Artwork] = {}
    for row in data:
        data_by_id[row.id] = row
    embeddings, embeddings_ids = read_embeddings("/data/embeddings.hdf5")


@stub.function(
    image=stub.webhook_image,
    mounts=[
        Mount.from_local_file("data/artmuseums-clean.json", "/data/catalog.json"),
        Mount.from_local_file("data/embeddings.hdf5", "/data/embeddings.hdf5"),
    ],
    keep_warm=1,
)
@web_endpoint()
def suggestions(text: str, n: int = 50) -> list[SearchResult]:
    """Return a list of artworks that are similar to the given text."""
    features = run_clip_text.remote([text])[0, :]
    features /= np.linalg.norm(features)
    scores = embeddings @ features
    index_array = np.argsort(scores)
    return [
        SearchResult(score=50 * (1 + scores[i]), artwork=data_by_id[embeddings_ids[i]])
        for i in reversed(index_array[-n:])
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("dispict")
    subparsers = parser.add_subparsers(dest="sub")

    subparsers.add_parser("embed-images")
    subparsers.add_parser("webhook")

    args = parser.parse_args()
    if args.sub == "embed-images":
        import h5py

        data = read_data("data/artmuseums-clean.json")

        chunk_size = 32
        chunked_ids = []
        chunked_urls = []
        for idx in range(0, len(data), chunk_size):
            chunked_ids.append([row.id for row in data[idx : idx + chunk_size]])
            chunked_urls.append([row.image_url for row in data[idx : idx + chunk_size]])

        with stub.run():
            results = list(run_clip_images.map(chunked_urls))

        all_embeddings: dict[int, np.ndarray] = {}
        for ids, (missing, embeddings) in zip(chunked_ids, results):
            assert len(ids) == len(missing) + len(embeddings)
            embeddings_idx = 0
            for i, id in enumerate(ids):
                if i not in missing:
                    all_embeddings[id] = embeddings[embeddings_idx, :]
                    embeddings_idx += 1

        print(f"Finished embedding {len(all_embeddings)} images out of {len(data)}")

        ids, embedding_matrix = zip(*all_embeddings.items())
        embedding_matrix = np.vstack(embedding_matrix)
        with h5py.File("data/embeddings.hdf5", "w") as f:
            f.create_dataset("embeddings", data=embedding_matrix)
            f.create_dataset("ids", data=ids)
        print("Saved to hdf5 file")

    elif args.sub == "webhook":
        print("Serving webhook at a temporary URL. Use `modal app deploy` to deploy.")
        stub.serve()

    else:
        parser.print_help()
        sys.exit(1)
