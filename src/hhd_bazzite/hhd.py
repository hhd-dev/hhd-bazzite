import logging
import os
import subprocess
from typing import TYPE_CHECKING, Any, Sequence

from hhd.plugins import Context, HHDPlugin, HHDSettings, load_relative_yaml
from hhd.plugins.conf import Config

logger = logging.getLogger(__name__)


def execute_ujust(cmd: str):
    try:
        out = subprocess.run(["ujust", cmd], capture_output=True)
        if out.stdout and out.stderr:
            log = "Standard Output:\n"
            log += str(out.stdout)
            log += "\n"
            log += "Error Output:\n"
            log += str(out.stderr)
        elif out.stdout:
            log = str(out.stdout)
        elif out.stderr:
            log = str(out.stderr)
        else:
            log = ""
        return log
    except Exception as e:
        return f"Command failed with error:\n{e}"


class Plugin(HHDPlugin):
    def __init__(self) -> None:
        self.name = f"bazzite"
        self.priority = 70
        self.log = "bazz"

    def settings(self) -> HHDSettings:
        return {
            "utilities": load_relative_yaml("ujust.yml"),
            "bazzite": {"bazzite": load_relative_yaml("general.yml")},
        }

    def open(
        self,
        emit,
        context: Context,
    ):
        pass

    def update(self, conf: Config):
        todo = []
        for group in ("utilities.decky", "utilities.other"):
            for cmd, val in conf[group].to(dict).items():
                if val:
                    todo.append(cmd)
                    conf[f"{group}.{cmd}"] = False

        log = ""
        for cmd in todo:
            log += f"Executing command '{cmd}'\n"
            log += execute_ujust(cmd)

        conf["utilities.cmd.output"] = log

    def close(self):
        pass


def autodetect(existing: Sequence[HHDPlugin]) -> Sequence[HHDPlugin]:
    if len(existing):
        return existing

    return [Plugin()]
