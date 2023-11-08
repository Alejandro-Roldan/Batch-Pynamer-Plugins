"""This has some extra metadata plugin utilities. That use extra dependencies or are specific to my own setup"""

import magic
import re

from batchpynamer.data.metadata_data_tools import meta_img_get
from batchpynamer.data.rename_data_tools import rename_ext_split_action
from batchpynamer.plugins.plugins_base import BasePlugin
from batchpynamer.plugins.plugins.Metadata.metadata import (
    _MetadataPluginBaseClass,
)


# A bit specific to how i order my music
RE_DISC_NUMER = re.compile(r".+\/Disc\s(\d+)")


class TitleAndTrackFromFilename(_MetadataPluginBaseClass):
    """
    Sets the title and tracknumber metadata getting its values from the
    filename. It splits the filename at the first apparition of "-" and
    sets the left part to be the tracknumber and the right part to be
    the title.
    """

    short_desc = 'Set "title" and "tracknumber" from filename'
    finish_msg = 'Changed "title" and "tracknumber" according to filename'

    def meta_changes(self, meta_audio, item):
        # Get the filename
        name = os.path.basename(item)

        # Split filename
        n, title = name.split("-", 1)
        # Remove the extension from the title
        title, ext = rename_ext_split_action(title)

        # Set the new metadata values
        meta_audio["title"] = title.strip()
        meta_audio["tracknumber"] = n.strip()

        return meta_audio


class SetDiscNumber(_MetadataPluginBaseClass):
    """Adds discnumber metadata if there are discs to be numbered"""

    short_desc = 'Set "discnumber" metadata'
    finish_msg = 'Added "discnumber" metadata'

    def meta_changes(self, meta_audio, item):
        try:
            disc_num = RE_DISC_NUMER.match(item)[1]
        except TypeError:
            pass
        else:
            meta_audio["discnumber"] = disc_num

        return meta_audio


class SaveMetadataImg(BasePlugin):
    """Extracts the cover image from metadata and saves it

    It doesnt overwrite images.
    """

    short_desc = "Save metadata Image"

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
