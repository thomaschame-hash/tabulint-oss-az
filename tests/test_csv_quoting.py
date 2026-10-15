import pytest

from tabulint import TabulintError, load_csv
from tabulint.cli import EXIT_ERROR, EXIT_OK, main


def test_unterminated_quote_at_end_of_file_is_rejected(write):
    path = write("bad.csv", 'name,age\nAda,"36\n')
    with pytest.raises(TabulintError) as excinfo:
        load_csv(path)
    message = str(excinfo.value)
    assert str(path) in message
    assert "malformed CSV" in message


def test_unterminated_quote_does_not_swallow_following_rows(write):
    # Without a check, the open quote silently absorbs every later row.
    path = write("bad.csv", 'name,note\nAda,"never closed\nGrace,fine\nLin,fine\n')
    with pytest.raises(TabulintError, match="malformed CSV"):
        load_csv(path)


def test_unterminated_quote_with_custom_delimiter_is_rejected(write):
    with pytest.raises(TabulintError, match="malformed CSV"):
        load_csv(write("bad.csv", 'name;age\nAda;"36\n'), delimiter=";")


def test_text_after_closing_quote_is_rejected(write):
    with pytest.raises(TabulintError, match="malformed CSV"):
        load_csv(write("bad.csv", 'name,age\n"Ada"x,36\n'))


def test_quoted_field_containing_delimiter_still_loads(write):
    rows = load_csv(write("ok.csv", 'name,city\nAda,"London, UK"\n'))
    assert rows == [{"name": "Ada", "city": "London, UK"}]


def test_quoted_field_containing_newline_still_loads(write):
    rows = load_csv(write("ok.csv", 'name,note\nAda,"line one\nline two"\n'))
    assert len(rows) == 1
    assert rows[0]["name"] == "Ada"
    # Windows may store the line break as "\r\n"; it must survive either way.
    assert rows[0]["note"].splitlines() == ["line one", "line two"]

def test_escaped_double_quote_still_loads(write):
    rows = load_csv(write("ok.csv", 'name,quote\nAda,"she said ""hi"""\n'))
    assert rows == [{"name": "Ada", "quote": 'she said "hi"'}]


def test_quoted_field_with_custom_delimiter_still_loads(write):
    rows = load_csv(write("ok.csv", 'name;city\nAda;"Paris; France"\n'), delimiter=";")
    assert rows == [{"name": "Ada", "city": "Paris; France"}]


def test_cli_unterminated_quote_exits_two_with_readable_message(write, capsys):
    assert main([write("bad.csv", 'name,age\nAda,"36\n')]) == EXIT_ERROR
    captured = capsys.readouterr()
    assert "malformed CSV" in captured.err
    assert "no issues found" not in captured.out


def test_cli_valid_quoted_csv_still_exits_zero(write):
    assert main([write("ok.csv", 'name,city\nAda,"London, UK"\n')]) == EXIT_OK
