from batchpynamer.plugins.plugins_base import BasePlugin
from batchpynamer.gui.notebook.rename import rename


class DelayRename(BasePlugin):
    """Delays renaming action until all the changes are definitive"""

    short_desc = "Delay Rename"
    allow_no_selection = True

    def pre_hook(self):
        pass

    def selection(self):
        pass

    def run(self):
        """Redefine Renaming calls for the new ones in this class"""
        rename.rename_gui_apply_rename_action = (
            self.rename_gui_apply_rename_action
        )
        rename.rename_gui_undo_rename_call = self.rename_gui_undo_rename_call

    def post_hook(self):
        pass

    def rename_gui_apply_rename_action(self, command_rename=None):
        print("lol")

    def rename_gui_undo_rename_call(event=None):
        print("lmao")
