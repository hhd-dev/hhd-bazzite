import logging
import os
import subprocess
from typing import TYPE_CHECKING, Any, Sequence

from hhd.plugins import Context, HHDPlugin, HHDSettings, load_relative_yaml
from hhd.plugins.conf import Config

logger = logging.getLogger(__name__)


def get_changelog():
    try:
        out = subprocess.run(["ujust", "changelog"], capture_output=True)
        return str(out.stdout)
    except Exception as e:
        return f"Could not retrieve changelog with error:\n{e}"


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
        self.init = True

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
        self.init = True
        pass

    def update(self, conf: Config):
        if self.init:
            conf["bazzite.bazzite.changelog"] = get_changelog()
            self.init = False

        todo = []
        for cmd, val in conf["utilities.other"].to(dict).items():
            if val:
                todo.append(cmd)
                conf[f"utilities.other.{cmd}"] = False

        if conf["utilities.decky.apply"].to(bool):
            install = False
            conf["utilities.decky.apply"] = False
            for cmd, val in conf["utilities.decky"].to(dict).items():
                if cmd != "apply" and val:
                    todo.append(cmd)
                    conf[f"utilities.decky.{cmd}"] = False
                    install = True

            if install:
                todo.append("refresh-decky")

        if todo:
            logs = []
            for cmd in todo:
                out = execute_ujust(cmd)
                logs.append(f"Executing command '{cmd}'\n{out}")

            log = "\n".join(logs)
            logger.info(f"Executed ujust commands:\n{log}")
            conf["utilities.cmd.output"] = log

    def close(self):
        pass


def autodetect(existing: Sequence[HHDPlugin]) -> Sequence[HHDPlugin]:
    if len(existing):
        return existing

    return [Plugin()]
