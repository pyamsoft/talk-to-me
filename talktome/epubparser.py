import os
import re
from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Any, List, Callable

from ebooklib.epub import EpubBook

from talktome.models import Chapter, BookInfo, ChapterRange


class EpubParser:
    _MAGIC_BREAK_STRING = " @BRK#"  # leading blank is for text split

    @classmethod
    def _log(cls, *args: Any):
        print("[EpubParser]: ", *args)

    @classmethod
    def _sanitize_title(cls, title: str) -> str:
        # replace MAGIC_BREAK_STRING with a blank space
        # strip incase leading bank is missing
        title = title.replace(cls._MAGIC_BREAK_STRING.strip(), " ")
        sanitized_title = re.sub(r"[^\w\s]", "", title, flags=re.UNICODE)
        sanitized_title = re.sub(r"\s+", "_", sanitized_title.strip())
        return sanitized_title

    @classmethod
    def _extract_title_for_chapter(
        cls,
        soup: BeautifulSoup,
        cleaned_text: str,
    ) -> str:
        title = soup.title.string if soup.title else ""

        # fill in the title if it's missing
        if not title:
            title = cleaned_text[:60]
        title = cls._sanitize_title(title)
        return title

    @classmethod
    def _extract_chapter(
        cls,
        content: str,
        chapter_number: int,
        newline_mode: str,
        remove_endnotes: bool,
    ) -> Chapter:
        soup = BeautifulSoup(content, "lxml")
        try:
            cleaned_text = cls._extract_text_for_chapter(
                soup,
                newline_mode=newline_mode,
                remove_endnotes=remove_endnotes,
            )
            title = cls._extract_title_for_chapter(soup, cleaned_text)
            return Chapter(
                title=title,
                content=cleaned_text,
                number=chapter_number,
            )
        finally:
            soup.decompose()

    @classmethod
    def _extract_text_for_chapter(
        cls,
        soup: BeautifulSoup,
        newline_mode: str,
        remove_endnotes: bool,
    ) -> str:
        raw = soup.get_text(strip=False)

        # Replace excessive whitespaces and newline characters based on the mode
        if newline_mode == "single":
            # noinspection RegExpSimplifiable
            cleaned_text = re.sub(r"[\n]+", cls._MAGIC_BREAK_STRING, raw.strip())
        elif newline_mode == "double":
            # noinspection RegExpSimplifiable
            cleaned_text = re.sub(r"[\n]{2,}", cls._MAGIC_BREAK_STRING, raw.strip())
        else:
            raise ValueError(f"Invalid newline mode: {newline_mode}")

        cleaned_text = re.sub(r"\s+", " ", cleaned_text)

        # Removes endnote numbers
        if remove_endnotes:
            cleaned_text = re.sub(r'(?<=[a-zA-Z.,!?;”")])\d+', "", cleaned_text)
        return cleaned_text

    @classmethod
    def _extract_chapters(
        cls,
        epub_book: EpubBook,
        newline_mode: str,
        remove_endnotes: bool,
    ) -> List[Chapter]:
        """
        Extract chapter titles and text content from an ebook
        :param epub_book:
        :param newline_mode:
        :param remove_endnotes:
        :return:
        """
        chapters: List[Chapter] = []
        chapter_number = 1
        for item in epub_book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                chapter = cls._extract_chapter(
                    content=content,
                    newline_mode=newline_mode,
                    remove_endnotes=remove_endnotes,
                    chapter_number=chapter_number,
                )
                chapter_number += 1
                chapters.append(chapter)
        return chapters

    @classmethod
    def _extract_book_info(cls, book: EpubBook) -> BookInfo:
        # Get the book title and author from metadata or use fallback values
        book_title = "Untitled"
        author = "Unknown"
        if book.get_metadata("DC", "title"):
            book_title = book.get_metadata("DC", "title")[0][0]
        if book.get_metadata("DC", "creator"):
            author = book.get_metadata("DC", "creator")[0][0]
        return BookInfo(
            title=book_title,
            author=author,
        )

    @classmethod
    def _get_chapter_range(
        cls,
        chapter_count: int,
        start: int,
        end: int,
    ) -> ChapterRange:
        # Check chapter start and end args
        if start < 1 or start > chapter_count:
            raise ValueError(
                f"Chapter start index {start} is out of range. Check your input."
            )
        if end < -1 or end > chapter_count:
            raise ValueError(
                f"Chapter end index {end} is out of range. Check your input."
            )
        if end == -1:
            end = chapter_count

        if start > end:
            raise ValueError(
                f"Chapter start index {start} is larger than chapter end index {end}. Check your input."
            )

        return ChapterRange(
            start=start,
            end=end,
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
        on_generate_media: Callable[[Path, str, str, Chapter], None],
    ) -> None:
        book = epub.read_epub(input_file)

        chapters = cls._extract_chapters(book, newline_mode, remove_endnotes)
        chapter_count = len(chapters)

        chapter_range = cls._get_chapter_range(
            chapter_count=chapter_count,
            start=chapter_start,
            end=chapter_end,
        )
        book_info = cls._extract_book_info(book)

        os.makedirs(output_folder, exist_ok=True)

        cls._log(f"Book: {book_info}.")
        cls._log(f"Chapters count: {chapter_count}.")
        cls._log(f"Converting chapters {chapter_start} to {chapter_end}.")

        for chapter in chapters:
            chapter_number = chapter.number
            chapter_title = chapter.title

            if chapter_number < chapter_range.start:
                continue
            if chapter_number > chapter_range.end:
                continue

            output_name = f"{chapter_number:04d}_{chapter_title}.mp3"
            output_file = Path(output_folder / output_name)
            cls._log(
                f"{chapter_number}/{chapter_count}: {chapter_title} => {output_file}"
            )
            on_generate_media(
                output_file,
                language,
                voice_model,
                chapter,
            )
