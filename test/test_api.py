#!/usr/bin/env python
"""
Test functionality of API for books. Only exercise methods that are
available at the API level, so that we could change implementations
and it should still pass.
"""

import unittest
import os
import os.path
import json

from books.api import Resource, Reference
from books.books import BookResource
#from books.books import Book, Chapter, Lines, Line


DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/pp-sample.json")


class TestBooks(unittest.TestCase):

  @classmethod
  def setUpClass(cls): 
    TestBooks.data = json.load(open(DATA_FILE))
    print TestBooks.data

  def setUp(self):
    """ NOTE: Only necessary dependency on a specific implementation. 
    """
    self.res = BookResource.from_json(TestBooks.data)

  #---------------------------------------------------------------------------
  # reference
  #---------------------------------------------------------------------------
  def test_parse_chapter_reference(self):
    ref = self.res.reference("Chapter 2")
    self.assertIsInstance(ref, Reference)
    self.assertEquals(ref.pretty(), "Chapter 2")

  def test_parse_chapter_reference_lower(self):
    ref = self.res.reference("chapter 2")
    self.assertIsInstance(ref, Reference)
    self.assertEquals(ref.pretty(), "Chapter 2")

  def test_parse_chapter_reference_without_chapter(self):
    ref = self.res.reference("2")
    self.assertIsInstance(ref, Reference)
    self.assertEquals(ref.pretty(), "Chapter 2")

  def test_parse_chapter_reference_with_one_line(self):
    ref = self.res.reference("2:1")
    self.assertIsInstance(ref, Reference)
    self.assertEquals(ref.pretty(), "Chapter 2:1")

  def test_parse_chapter_reference_with_start_and_end_lines(self):
    ref = self.res.reference("2:1-3")
    self.assertIsInstance(ref, Reference)
    self.assertEquals(ref.pretty(), "Chapter 2:1-3")

  # XXX: move
  def test_chapter_refs(self):
    chaps = self.res.chapter_refs()
    self.assertEquals(len(chaps), 3)

  def test_chapter_length(self):
    chaps = self.res.chapter_refs()
    c3 = chaps[2]
    self.assertEquals(self.res.chapter_length(c3.num()), 7)

  def test_chapter_text_for_whole_chapter_default(self):
    chaps = self.res.chapter_refs()
    c3 = chaps[2]
    text = self.res.chapter_text(c3.num())
    self.assertEquals(len(text), 817)

  def test_chapter_text_for_whole_chapter_from_one(self):
    chaps = self.res.chapter_refs()
    c3 = chaps[2]
    text = self.res.chapter_text(c3.num(), first_line=1)
    self.assertEquals(len(text), 817)

  def test_chapter_text_for_whole_chapter_to_last(self):
    chaps = self.res.chapter_refs()
    c3 = chaps[2]
    last = self.res.chapter_length(c3.num())
    text = self.res.chapter_text(c3.num(), last_line=last)
    self.assertEquals(len(text), 817)

  def test_chapter_text_for_whole_chapter_from_first_to_last(self):
    chaps = self.res.chapter_refs()
    c3 = chaps[2]
    last = self.res.chapter_length(c3.num())
    text = self.res.chapter_text(c3.num(), first_line=1, last_line=last)
    self.assertEquals(len(text), 817)

  def test_book_refs(self):
    book = self.res.top_reference()
    self.assertIsInstance(book, Book)
    self.assertIsInstance(book, Reference)
    self.assertEquals(book.pretty(), "PRIDE AND PREJUDICE")
    # cannot get text on a book
    self.assertRaises(NotImplementedError, book.text)

    chaps = book.children()
    self.assertEquals(len(chaps), 3)
    c3 = chaps[2]
    self.assertIsInstance(c3, Reference)
    self.assertIsInstance(c3, Chapter)
    self.assertEquals(c3.pretty(), "Chapter 3")
    self.assertEquals(len(c3.text()), 817)

    lines = c3.children()
    self.assertIsInstance(lines, Lines)
    self.assertIsInstance(lines, Reference)
    self.assertEquals(lines.pretty(), "Chapter 3:1-7")
    self.assertEquals(len(lines.text()), 817)

    line_array = lines.children()
    self.assertEquals(len(line_array), 7)
    one_line = line_array[-1]
    self.assertIsInstance(one_line, Reference)
    self.assertIsInstance(one_line, Line)
    self.assertEquals(one_line.pretty(), "Chapter 3:7")
    self.assertEquals(len(one_line.text()), 128)

  def test_book_search(self):
    book = self.res.top_reference()
    hits = book.search("daughter")
    self.assertEquals(len(hits), 3)
    self.assertIsInstance(hits[0], Line)
    self.assertEquals(hits[0].pretty(), "Chapter 1:2")
    self.assertEquals(hits[1].pretty(), "Chapter 2:4")
    self.assertEquals(hits[2].pretty(), "Chapter 3:1")
    self.assertRaises(NotImplementedError, hits[0].children)
    self.assertTrue(hits[2].text().startswith("Not all that Mrs."))
    self.assertTrue(hits[2].text().endswith("of Mr. Bingley."))

  def test_book_search_one_chapter(self):
    book = self.res.top_reference()
    chaps = book.children()
    c3 = chaps[2]
    hits = c3.search("daughter")
    self.assertEquals(len(hits), 1)
    self.assertEquals(hits[0].pretty(), "Chapter 3:1")

  def test_book_search_from_chapter_to_end(self):
    hits = self.res.search("daughter", first_chapter=2)
    self.assertEquals(len(hits), 2)
    self.assertEquals(hits[0].pretty(), "Chapter 2:4")

  def test_book_search_to_chapter_to_end(self):
    hits = self.res.search("daughter", last_chapter=2)
    self.assertEquals(len(hits), 2)
    self.assertEquals(hits[0].pretty(), "Chapter 1:2")

  def test_book_search_line_range(self):
    hits = self.res.search("Mr\.", first_chapter=2, last_chapter=2, first_line=1, last_line=6)
    self.assertEquals(len(hits), 3)
    self.assertEquals(hits[0].pretty(), "Chapter 2:1")
    self.assertEquals(hits[1].pretty(), "Chapter 2:5")
    self.assertEquals(hits[2].pretty(), "Chapter 2:6")

  def test_book_search_from_line(self):
    hits = self.res.search("Mr\.", first_chapter=2, last_chapter=2, first_line=2, last_line=6)
    self.assertEquals(len(hits), 2)
    self.assertEquals(hits[0].pretty(), "Chapter 2:5")

  def test_book_search_to_line(self):
    hits = self.res.search("Mr\.", first_chapter=2, last_chapter=2, first_line=1, last_line=5)
    self.assertEquals(len(hits), 2)
    self.assertEquals(hits[1].pretty(), "Chapter 2:5")

  def test_book_search_of_lines(self):
    lines = self.res.reference("2:1-5")
    hits = lines.search("Mr\.")
    self.assertEquals(len(hits), 2)
    self.assertEquals(hits[1].pretty(), "Chapter 2:5")

  
if __name__ == "__main__":
  unittest.main()


