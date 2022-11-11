import json
import time

import modal
import numpy as np

stub = modal.Stub()

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


if __name__ == "__main__":
    with open("data/artmuseums-clean.json", "r") as f:
        data = json.load(f)

    chunk_size = 32
    chunked_ids = []
    chunked_urls = []
    for idx in range(0, len(data), chunk_size):
        chunked_ids.append([row["id"] for row in data[idx : idx + chunk_size]])
        chunked_urls.append([row["image_url"] for row in data[idx : idx + chunk_size]])

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
