#!/usr/bin/env python3
from pathlib import Path

from mutagen.id3 import TIT2, TPE1, TALB, TRCK
from mutagen.mp3 import MP3

from talktome.models import BookInfo, Chapter


class AudioTagger:
    @classmethod
    def save_tags(
        cls,
        output_file: Path,
        book: BookInfo,
        chapter: Chapter,
    ):
        # Add ID3 tags to the generated MP3 file
        audio = MP3(output_file)
        audio["TIT2"] = TIT2(encoding=3, text=chapter.title)
        audio["TPE1"] = TPE1(encoding=3, text=book.author)
        audio["TALB"] = TALB(encoding=3, text=book.title)
        audio["TRCK"] = TRCK(encoding=3, text=str(chapter.number))
        audio.save()
