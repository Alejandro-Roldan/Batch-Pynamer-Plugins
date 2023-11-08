"""
This has some extra metadata plugin utilities. That use extra dependencies or
are specific to my own setup
"""

import magic
import re
import os
from batchpynamer.data.metadata_data_tools import meta_img_get
from batchpynamer.data.rename_data_tools import rename_ext_split_action
from batchpynamer.plugins.plugins_base import BasePlugin
from batchpynamer.plugins.plugins.Metadata.metadata import (
    _MetadataPluginBaseClass,
)
import logging

# A bit specific to how i order my music
RE_DISC_NUMER = re.compile(r".+\/Disc\s(\d+)")
RE_ALBUM_NAME = re.compile(
    r".+?(\d{4})\s-\s(.+?)(?>\[(?>Live|EP|Single|mp3).+)*$"
)
RE_ARTIST = re.compile(r".+\/([^\/]+)\/\d{4}")


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

        meta_audio["title"] = title.strip()
        meta_audio["tracknumber"] = n.strip()

        return meta_audio


class ArtistFromDirectory(_MetadataPluginBaseClass):
    short_desc = 'Set "artist" from directory'
    finish_msg = 'Changed "artist" according to directory'

    def meta_changes(self, meta_audio, item):
        # Get the filename
        try:
            artist = RE_ARTIST.match(item)[1]
        except TypeError:
            logging.warning(
                f'Couldn\'t change "artist" metadata for "{item}". F'
                "ailed regex match"
            )
        else:
            meta_audio["artist"] = artist.strip()

        return meta_audio


class YearAndAlbumFromDirectory(_MetadataPluginBaseClass):
    """
    Sets the title and tracknumber metadata getting its values from the
    filename. It splits the filename at the first apparition of "-" and
    sets the left part to be the tracknumber and the right part to be
    the title.
    """

    short_desc = 'Set "year" and "album" from directory'
    finish_msg = 'Changed "year" and "album" according to directory'

    def meta_changes(self, meta_audio, item):
        # Get the filename
        try:
            year, album = RE_ALBUM_NAME.match(item).groups()
        except AttributeError:
            logging.warning(
                f'Couldn\'t change "year" and "album" metadata for "{item}". F'
                "ailed regex match"
            )
        else:
            meta_audio["album"] = album.strip()
            meta_audio["date"] = year.strip()

        return meta_audio


class SetDiscNumber(_MetadataPluginBaseClass):
    """Adds discnumber metadata if there are discs to be numbered"""

    short_desc = 'Set "discnumber" metadata'
    finish_msg = 'Added "discnumber" metadata'

    def meta_changes(self, meta_audio, item):
        try:
            disc_num = RE_DISC_NUMER.match(item)[1]
        except TypeError:
            logging.warning(
                f'Couldn\'t change "discnumber" metadata for "{item}". Failed '
                "regex match"
            )
        else:
            meta_audio["discnumber"] = disc_num

        return meta_audio


class RemoveExtraMetadata(_MetadataPluginBaseClass):
    """Adds discnumber metadata if there are discs to be numbered"""

    short_desc = "Remove extra metadata"
    finish_msg = "Removed extra metadata"
    keep_keys = {
        "title",
        "tracknumber",
        "artist",
        "album",
        "date",
        "genre",
        "discnumber",
    }

    def meta_changes(self, meta_audio, item):
        for key in meta_audio.keys():
            if key not in self.keep_keys:
                meta_audio.pop(key)

        return meta_audio


class ChangeMetadataFromPath(
    TitleAndTrackFromFilename,
    ArtistFromDirectory,
    YearAndAlbumFromDirectory,
    SetDiscNumber,
    RemoveExtraMetadata,
):
    short_desc = "Set all metadata from path"
    finish_msg = "Changed all metadata according to path"

    def meta_changes(self, meta_audio, item):
        meta_audio = TitleAndTrackFromFilename.meta_changes(
            self, meta_audio, item
        )
        meta_audio = ArtistFromDirectory.meta_changes(self, meta_audio, item)
        meta_audio = YearAndAlbumFromDirectory.meta_changes(
            self, meta_audio, item
        )
        meta_audio = SetDiscNumber.meta_changes(self, meta_audio, item)
        meta_audio = RemoveExtraMetadata.meta_changes(self, meta_audio, item)

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
