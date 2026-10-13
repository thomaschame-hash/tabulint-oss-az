import pytest

from tabulint import TabulintError, load_csv
from tabulint.cli import EXIT_ERROR, EXIT_OK, main


def test_duplicate_header_is_rejected(write):
    path = write("dup.csv", "id,id\nfirst,second\n")
    with pytest.raises(TabulintError) as excinfo:
        load_csv(path)
    message = str(excinfo.value)
    assert str(path) in message
    assert "duplicate" in message
    assert "'id'" in message


def test_duplicate_header_among_other_columns_is_rejected(write):
    with pytest.raises(TabulintError, match="duplicate.*'age'"):
        load_csv(write("dup.csv", "name,age,city,age\nAda,36,London,37\n"))


def test_duplicate_header_is_rejected_even_without_data_rows(write):
    with pytest.raises(TabulintError, match="duplicate"):
        load_csv(write("dup.csv", "id,id\n"))


def test_duplicate_header_with_custom_delimiter_is_rejected(write):
    path = write("dup.csv", "id;name;id\n1;Ada;2\n")
    with pytest.raises(TabulintError, match="duplicate.*'id'"):
        load_csv(path, delimiter=";")


def test_header_names_differing_only_by_case_are_not_duplicates(write):
    rows = load_csv(write("case.csv", "id,ID\n1,2\n"))
    assert rows == [{"id": "1", "ID": "2"}]


def test_valid_header_still_loads(write):
    rows = load_csv(write("ok.csv", "name,age\nAda,36\nGrace,45\n"))
    assert rows == [{"name": "Ada", "age": "36"}, {"name": "Grace", "age": "45"}]


def test_valid_header_with_custom_delimiter_still_loads(write):
    rows = load_csv(write("ok.csv", "name;age\nAda;36\n"), delimiter=";")
    assert rows == [{"name": "Ada", "age": "36"}]


def test_comma_inside_header_is_not_a_duplicate_with_custom_delimiter(write):
    # With ';' as delimiter the header is one column named "id,id", not two.
    rows = load_csv(write("ok.csv", "id,id;name\n1;Ada\n"), delimiter=";")
    assert rows == [{"id,id": "1", "name": "Ada"}]


def test_cli_duplicate_header_exits_two_with_readable_message(write, capsys):
    path = write("dup.csv", "id,id\nfirst,second\n")
    assert main([path]) == EXIT_ERROR
    captured = capsys.readouterr()
    assert "duplicate" in captured.err
    assert "'id'" in captured.err
    assert "no issues found" not in captured.out


def test_cli_valid_header_still_exits_zero(write):
    assert main([write("ok.csv", "name,age\nAda,36\n")]) == EXIT_OK
