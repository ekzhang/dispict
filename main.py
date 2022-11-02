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


@stub.function(image=stub.clip_image, shared_volumes={"/root/.cache": sv})
def run_clip(*, texts: list[str] = [], image_urls: list[str] = []):
    """Run pretrained CLIP on a list of texts or image URLs.

    Returns a numpy array containing the concatenated 512-dimensional embedding
    outputs for each provided input, evaluated as a batch.
    """
    if texts and image_urls:
        raise ValueError("Only one of texts or image_urls can be provided.")

    if texts:
        text_tokens = clip.tokenize(texts)
        with torch.no_grad():
            return model.encode_text(text_tokens).float().numpy()
    elif image_urls:
        from io import BytesIO
        from concurrent.futures import ThreadPoolExecutor

        import requests
        from PIL import Image

        with ThreadPoolExecutor(max_workers=10) as executor:
            responses = list(executor.map(requests.get, image_urls))

        original_images = [Image.open(BytesIO(resp.content)) for resp in responses]
        images: list[torch.Tensor] = [preprocess(img) for img in original_images]  # type: ignore
        image_input = torch.stack(images)
        with torch.no_grad():
            return model.encode_image(image_input).float().numpy()
    else:
        return np.empty((0, 512))


if __name__ == "__main__":
    with stub.run():
        print(
            run_clip(
                image_urls=[
                    "https://nrs.harvard.edu/urn-3:HUAM:COIN00538_dynmc",
                    "https://nrs.harvard.edu/urn-3:HUAM:COIN00538_dynmc",
                ]
            )
        )
