import shutil
from pathlib import Path
from typing import Optional, Any

from talktome.epubparser import EpubParser
from talktome.models import Chapter, BookInfo
from talktome.tagger import AudioTagger
from talktome.tts import TextToSpeech


class TalkToMe:
    @classmethod
    def _log(cls, *args: Any):
        print("[TalkToMe]", *args)

    @classmethod
    def _on_generate_tts(
        cls,
        work_folder: Path,
        output_file: Path,
        langauge: str,
        voice_model: str,
        book: BookInfo,
        chapter: Chapter,
    ):
        TextToSpeech.text_to_speech(
            work_folder=work_folder,
            output_file=output_file,
            language=langauge,
            voice_model=voice_model,
            chapter=chapter,
        )
        AudioTagger.save_tags(output_file, book, chapter)

    @classmethod
    def _cleanup(cls, work_folder: Optional[Path]):
        cls._log("Cleanup")
        if work_folder:
            cls._log("Remove work_folder: ", work_folder)
            # Remove work folder
            shutil.rmtree(
                work_folder,
                ignore_errors=True,
            )

    @classmethod
    def epub_to_audiobook(
        cls,
        input_file: str,
        output_folder: Path,
        language: str,
        voice_model: str,
        newline_mode: str,
        chapter_start: int,
        chapter_end: int,
        remove_endnotes: bool,
    ) -> None:
        work_folder: Optional[Path] = None
        try:
            # Prepare output
            work_folder = Path(f"{str(input_file)}.work")

            # Make the work directory
            work_folder.mkdir(
                mode=0o755,
                parents=True,
                exist_ok=True,
            )

            EpubParser.epub_to_audiobook(
                input_file=input_file,
                output_folder=output_folder,
                work_folder=work_folder,
                language=language,
                voice_model=voice_model,
                newline_mode=newline_mode,
                chapter_start=chapter_start,
                chapter_end=chapter_end,
                remove_endnotes=remove_endnotes,
                on_generate_media=cls._on_generate_tts,
            )
        finally:
            cls._cleanup(work_folder)

    def destroy(self):
        pass
