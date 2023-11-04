#!/usr/bin/env python3
import os
import sys

from pathlib import Path
from traceback import print_exc
from typing import Any, List, Callable

from talktome.talktome import TalkToMe

_HOME_CACHE = Path.home() / ".cache"
_XDG_CACHE_HOME = os.getenv("XDG_CACHE_HOME", f"{str(_HOME_CACHE)}")


class Locker:
    _LOCK_FILE_PATH = f"{_XDG_CACHE_HOME}/talk-to-me.lock"

    @classmethod
    def _log(cls, *args: Any):
        print("[Locker]: ", *args)

    @classmethod
    def with_lock(
        cls,
        files: List[str],
        on_lock_claimed: Callable[[Path, List[str]], None],
    ) -> bool:
        p = Path(cls._LOCK_FILE_PATH)
        if p.exists():
            cls._log("Lock file is already claimed by a different process")
            current_status = p.read_text()
            cls._log("Current Status === ")
            print(current_status)
            return False

        # noinspection PyBroadException
        try:
            cls._log("Claim lock file", cls._LOCK_FILE_PATH)
            p.touch()

            on_lock_claimed(p, files)
            return True
        except Exception as _:
            print_exc()
            return False
        finally:
            p.unlink()


class Main:
    @classmethod
    def _log(cls, *args: Any):
        print("[Main]: ", *args)

    @classmethod
    def _run_generator(
        cls,
        lockfile: Path,
        paths: List[str],
    ):
        voice_model = Path("/models") / "en_US-lessac-medium.onnx"

        with lockfile.open(mode="a") as status:
            model = TalkToMe()
            try:
                cls._log("Processing possible EPUB files: ", paths)
                for file_path in paths:
                    status.write(f"Processing EPUB: {file_path}\n")
                    status.flush()

                    model.epub_to_audiobook(
                        input_file=file_path,
                        language="en-US",
                        remove_endnotes=False,
                        newline_mode="double",
                        chapter_start=1,
                        chapter_end=-1,
                        voice_model=str(voice_model),
                        output_folder=Path(file_path).parent,
                    )
                    status.write("\n")
                    status.flush()
            finally:
                model.destroy()

    @classmethod
    def main(cls, paths: List[str]) -> bool:
        return Locker.with_lock(paths, cls._run_generator)


if __name__ == "__main__":
    # Remove ourself
    args = sys.argv[1:]

    if not args or len(args) <= 0:
        print("TalkToMe: Must provide at least one file path to an EPUB file.")
    else:
        if Main.main(args):
            sys.exit(0)
        else:
            sys.exit(1)
