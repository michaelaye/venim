from pathlib import Path

from .config import config

storage_root = Path(config["venim_path"]).expanduser()


class PathManager:
    def __init__(self, mission, instr):
        self.mission = mission
        self.instr = instr

    @property
    def instr_savedir(self):
        return storage_root / self.mission / self.instr
