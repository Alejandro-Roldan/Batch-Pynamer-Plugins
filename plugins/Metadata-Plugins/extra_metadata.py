import magic
from batchpynamer.data.metadata_data_tools import meta_audio_get, meta_img_get
from batchpynamer.plugins.plugins_base import BasePlugin


class SaveMetadataImg(BasePlugin):
    """Extracts the cover image from metadata and saves it

    It doesnt overwrite images.
    """

    def run(self, item, **kwargs):
        img = meta_img_get(item)

        mime = magic.from_buffer(img, mime=True)
        _, ext = mime.split("/")
        ext = ext.lower().replace("jpeg", "jpg")

        i = 0
        while True:
            save_path = os.path.dirname(item) + f"/cover_{i}.{ext}"
            if not os.path.exists(save_path):
                break
            i += 1

        # Open file as write bytes mode
        with open(save_path, "wb") as f:
            f.write(img)
