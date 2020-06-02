from pathlib import Path

import toml


def set_venim_storage_path():
    path = input("Provide path where VENIM data should be stored:")
    config = {}
    config["venim_path"] = path
    with configpath.open("w") as f:
        toml.dump(config, f)


configpath = Path("~/.venim_config.toml").expanduser()

if not configpath.exists():
    set_venim_storage_path()

with configpath.open() as f:
    config = toml.load(f)
