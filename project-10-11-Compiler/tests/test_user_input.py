from xml.etree.ElementTree import Element, ElementTree

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from analyzer import main


def test_main_should_take_single_file(fs: FakeFilesystem, mocker: MockerFixture):
    fake_file = fs.create_file("/fake_dir/fake_file.jack", contents="fake code")
    mock_analyze = mocker.patch("analyzer.analyze", return_value=(None, None, None))

    main(fake_file.path, token_xml=False, grammar_xml=False, vm=False)

    mock_analyze.assert_called_once_with(fake_file.contents)


def test_main_should_take_directory(fs: FakeFilesystem, mocker: MockerFixture):
    fake_dir = fs.create_dir("/fake_dir")
    fake_file_1 = fs.create_file("/fake_dir/file1.jack", contents="fake code 1")
    fake_file_2 = fs.create_file("/fake_dir/file2.jack", contents="fake code 2")
    mock_analyze = mocker.patch("analyzer.analyze", return_value=(None, None, None))

    main(fake_dir.path, token_xml=False, grammar_xml=False, vm=False)

    for file in (fake_file_1, fake_file_2):
        mock_analyze.assert_any_call(file.contents)


def test_main_should_raise_for_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        main("/does_not_exist")


@pytest.mark.parametrize("suffix", ["T", ""], ids=["Token file", "Grammar File"])
class TestXML:
    def test_should_write_xml_from_file(self, fs: FakeFilesystem, suffix):
        fake_file = fs.create_file("/fake_dir/fake_file.jack")
        main(
            fake_file.path,
            token_xml=suffix == "T",
            grammar_xml=suffix == "",
            vm=False,
        )
        assert fs.exists(f"/fake_dir/fake_file{suffix}.xml")

    def test_should_write_xml_from_directory(self, fs: FakeFilesystem, suffix):
        fake_dir = fs.create_dir("/fake_dir")
        fs.create_file("/fake_dir/file1.jack")
        fs.create_file("/fake_dir/file2.jack")
        main(
            fake_dir.path,
            token_xml=suffix == "T",
            grammar_xml=suffix == "",
            vm=False,
        )
        assert fs.exists(f"/fake_dir/file1{suffix}.xml")
        assert fs.exists(f"/fake_dir/file2{suffix}.xml")

    def test_should_have_trailing_newline(self, fs: FakeFilesystem, suffix):
        code = fs.create_file("/fake_dir/fake_file.jack")
        main(
            code.path,
            token_xml=suffix == "T",
            grammar_xml=suffix == "",
            vm=False,
        )
        with open(f"/fake_dir/fake_file{suffix}.xml") as f:
            assert f.read().endswith("\n")


class TestTokenFile:
    def test_should_have_root_element(self, fs: FakeFilesystem):
        code = fs.create_file("/fake_dir/fake_file.jack")
        main(code.path, token_xml=True, grammar_xml=False, vm=False)
        with open("/fake_dir/fake_fileT.xml") as f:
            assert "<tokens>\n</tokens>" in f.read()

    def test_should_pad_token_value_with_spaces(self, fs: FakeFilesystem):
        code = fs.create_file("/fake_dir/fake_file.jack", contents="class Main {}")
        main(code.path, token_xml=True, grammar_xml=False, vm=False)
        with open("/fake_dir/fake_fileT.xml") as f:
            assert "<keyword> class </keyword>" in f.read()

    def test_should_write_output_own_separate_lines_without_indentation(self, fs: FakeFilesystem):
        code = fs.create_file("/fake_dir/fake_file.jack", contents="class Main {}")
        main(code.path, token_xml=True, grammar_xml=False, vm=False)
        with open("/fake_dir/fake_fileT.xml") as f:
            assert f.read().strip() == "<tokens>\n<keyword> class </keyword>\n<identifier> Main </identifier>\n<symbol> { </symbol>\n<symbol> } </symbol>\n</tokens>"


class TestGrammarFile:
    def test_should_have_root_element(self, fs: FakeFilesystem):
        code = fs.create_file("/fake_dir/fake_file.jack")
        main(code.path, token_xml=False, grammar_xml=True, vm=False)
        with open("/fake_dir/fake_file.xml") as f:
            assert "<class>\n</class>" in f.read()
