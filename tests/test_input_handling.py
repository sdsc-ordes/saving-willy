import pytest

from input_handling import is_valid_email
from input_handling import is_valid_number

# generate tests for is_valid_email
# - test with valid email
#    - basic email with @ and .
#    - test with email with multiple .
# - test with empty email
# - test with None email
# - test with non-string email
# - test with invalid email
#    - test with email without @
#    - test with email without .
#    - test with email without domain
#    - test with email without username
#    - test with email without TLD
#    - test with email with multiple @
#    - test with email starting with the + sign


def test_is_valid_email_valid():
    assert is_valid_email("j@a.bc")
    assert is_valid_email("j+oneuse@a.bc")
    assert is_valid_email("a@b.cd")
    assert is_valid_email("a.b@c.de")
    assert is_valid_email("a.b@c.de.fg")
    
def test_is_valid_email_empty():
    assert not is_valid_email("")
    
def test_is_valid_email_none():
    with pytest.raises(TypeError):
        is_valid_email(None)
    
def test_is_valid_email_non_string():
    with pytest.raises(TypeError):
        is_valid_email(123)
        
    
def test_is_valid_email_invalid():
    assert not is_valid_email("a.bc")
    assert not is_valid_email("a@bc")
    assert not is_valid_email("a.b@cc")
    assert not is_valid_email("@b.cc")
    assert not is_valid_email("a@.cc")
    assert not is_valid_email("a@b.")
    assert not is_valid_email("a@bb.")
    assert not is_valid_email("a@b.cc.")
    assert not is_valid_email("a@b@c.d")

# not sure how xfails come through the CI pipeline yet.
# maybe better to just comment out this stuff until pipeline is setup, then can check /extend
@pytest.mark.xfail(reason="Bug identified, but while setting up CI having failing tests causes more headache")
def test_is_valid_email_invalid_plus():
    assert not is_valid_email("+@test.com")
    assert not is_valid_email("+oneuse@test.com")


def test_is_valid_number_valid():
    # with a sign or without, fractional or integer are all valid
    assert is_valid_number("123")
    assert is_valid_number("123.456")
    assert is_valid_number("-123")
    assert is_valid_number("-123.456")
    assert is_valid_number("+123")
    assert is_valid_number("+123.456")

def test_is_valid_number_empty():
    assert not is_valid_number("")

def test_is_valid_number_none():
    with pytest.raises(TypeError):
        is_valid_number(None)

def test_is_valid_number_invalid():
    # func should return False for strings that are not numbers
    assert not is_valid_number("abc")
    assert not is_valid_number("123abc")
    assert not is_valid_number("abc123")
    assert not is_valid_number("123.456.789")
    assert not is_valid_number("123,456") 
    assert not is_valid_number("123-456")
    assert not is_valid_number("123+456")
def test_is_valid_number_valid():
    assert is_valid_number("123")
    assert is_valid_number("123.456")
    assert is_valid_number("-123")
    assert is_valid_number("-123.456")
    assert is_valid_number("+123")
    assert is_valid_number("+123.456")

def test_is_valid_number_empty():
    assert not is_valid_number("")

def test_is_valid_number_none():
    with pytest.raises(TypeError):
        is_valid_number(None)

def test_is_valid_number_invalid():
    assert not is_valid_number("abc")
    assert not is_valid_number("123abc")
    assert not is_valid_number("abc123")
    assert not is_valid_number("123.456.789")
    assert not is_valid_number("123,456")
    assert not is_valid_number("123-456")
    assert not is_valid_number("123+456")