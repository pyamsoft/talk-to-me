from pathlib import Path

from talktome.epubparser import EpubParser
from talktome.models import Chapter
from talktome.tts import TextToSpeech


class TalkToMe:
    @classmethod
    def _on_generate_tts(
        cls,
        work_folder: Path,
        output_file: Path,
        langauge: str,
        voice_model: str,
        chapter: Chapter,
    ):
        TextToSpeech.text_to_speech(
            work_folder=work_folder,
            output_file=output_file,
            language=langauge,
            voice_model=voice_model,
            chapter=chapter,
        )

    def epub_to_audiobook(
        self,
        input_file: str,
        output_folder: Path,
        language: str,
        voice_model: str,
        newline_mode: str,
        chapter_start: int,
        chapter_end: int,
        remove_endnotes: bool,
    ) -> None:
        EpubParser.epub_to_audiobook(
            input_file=input_file,
            output_folder=output_folder,
            language=language,
            voice_model=voice_model,
            newline_mode=newline_mode,
            chapter_start=chapter_start,
            chapter_end=chapter_end,
            remove_endnotes=remove_endnotes,
            on_generate_media=self._on_generate_tts,
        )

    def destroy(self):
        pass
