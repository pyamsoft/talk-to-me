#!/usr/bin/env python3
import shutil
import wave
from pathlib import Path
from typing import List, NamedTuple, Optional, Any
from pydub import AudioSegment
import sh

from talktome.models import Chapter


class TextToSpeech:
    @classmethod
    def _log(cls, *args: Any):
        print("[TextToSpeech]: ", *args)

    @classmethod
    def _is_special_char(cls, char: str) -> bool:
        """
        Check if the character is a English letter, number or punctuation
        or a punctuation in Chinese, never split these characters.
        """
        ord_char = ord(char)
        result = (
            (33 <= ord_char <= 126)
            or (char in "。，、？！：；“”‘’（）《》【】…—～·「」『』〈〉〖〗〔〕")
            or (char in "∶")
        )  # special unicode punctuation
        return result

    @classmethod
    def _split_chinese_text(
        cls,
        chunks: List[str],
        text: str,
        max_chars: int,
    ):
        current_chunk = ""
        for char in text:
            if len(current_chunk) + 1 <= max_chars or cls._is_special_char(char):
                current_chunk += char
            else:
                chunks.append(current_chunk)
                current_chunk = char

        if current_chunk:
            chunks.append(current_chunk)

    @classmethod
    def _split_eng_text(
        cls,
        chunks: List[str],
        text: str,
        max_chars: int,
    ):
        current_chunk = ""

        words = text.split()

        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_chars:
                current_chunk += (" " if current_chunk else "") + word
            else:
                chunks.append(current_chunk)
                current_chunk = word

        if current_chunk:
            chunks.append(current_chunk)

    @classmethod
    def _split_text(
        cls,
        text: str,
        max_chars: int,
        language: str,
    ) -> List[str]:
        chunks: List[str] = []
        if language.startswith("zh"):  # Chinese
            cls._split_chinese_text(
                chunks=chunks,
                text=text,
                max_chars=max_chars,
            )
        else:
            cls._split_eng_text(
                chunks=chunks,
                text=text,
                max_chars=max_chars,
            )

        return chunks

    @classmethod
    def _process_chunk_to_wav(
        cls,
        output_file: str,
        chunk: str,
        onnx_file: str,
    ):
        # Call the piper script from the venv environment
        # Run the script, output a wav file
        # noinspection PyUnresolvedReferences
        modeled = sh.piper.bake(
            # Voice model
            model=onnx_file,
            # Output to WAV
            output_file=output_file,
            # Silence after sentence
            sentence_silence="1.25",
        )

        # Pipe the text to piper via stdin
        modeled(_in=chunk)

    @classmethod
    def _chunks_to_wavs(
        cls,
        work_folder: Path,
        voice_model: str,
        text_chunks: List[str],
    ) -> List[str]:
        wav_files: List[str] = []
        for i, chunk in enumerate(text_chunks):
            wav_path = Path(work_folder / f"{i}.wav")
            wav = str(wav_path)
            wav_files.append(wav)
            cls._process_chunk_to_wav(
                onnx_file=voice_model,
                output_file=wav,
                chunk=chunk,
            )
        return wav_files

    @classmethod
    def _combine_wavs(
        cls,
        output_file: Path,
        wav_files: List[str],
    ) -> str:
        wavdata: List[List[NamedTuple, int]] = []
        for wav in wav_files:
            with wave.open(wav, mode="rb") as wavfile:
                wavdata.append(
                    [wavfile.getparams(), wavfile.readframes(wavfile.getnframes())]
                )

        # Write the wav data to the one big path
        one_big_wav_path = str(output_file.with_suffix(".wav"))
        with wave.open(one_big_wav_path, mode="wb") as one_big_file:
            one_big_file.setparams(wavdata[0][0])
            for data in wavdata:
                one_big_file.writeframes(data[1])

        return one_big_wav_path

    @classmethod
    def _wav_to_mp3(cls, output_file: Path, one_big_file: str):
        sound = AudioSegment.from_wav(one_big_file)
        sound.export(str(output_file), format="mp3")

    @classmethod
    def _cleanup(
        cls,
        one_big_file: Optional[str],
    ):
        cls._log("Clean up")
        if one_big_file:
            cls._log("Remove one big file: ", one_big_file)
            # Remove big WAV
            Path(one_big_file).unlink(missing_ok=True)

    @classmethod
    def text_to_speech(
        cls,
        work_folder: Path,
        output_file: Path,
        language: str,
        voice_model: str,
        chapter: Chapter,
    ):
        one_big_file: Optional[str] = None
        try:
            # Adjust this value based on your testing
            max_chars: int = 1800 if language.startswith("zh") else 3000

            text_chunks: List[str] = cls._split_text(
                text=chapter.content,
                max_chars=max_chars,
                language=language,
            )

            if len(text_chunks) <= 0:
                cls._log("No text chunks for chapter", chapter)
                return

            wav_files = cls._chunks_to_wavs(
                work_folder,
                voice_model,
                text_chunks,
            )

            # Combine all the wav data
            one_big_file = cls._combine_wavs(output_file, wav_files)

            # Convert the WAV to MP3
            cls._wav_to_mp3(output_file, one_big_file)
        finally:
            cls._cleanup(one_big_file)
