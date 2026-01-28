import pytest
from tokenizer import Tokenizer, TokenType

def get_clean_tokens(code):
    t = Tokenizer()
    tokens, state = t.tokenize(code)
    # Filter out whitespace (TEXT with space matches)
    # Wait, TokenType.TEXT matches identifiers too. 
    # Tokenizer emits (TEXT, char) for space.
    # Keyword/Name is also TEXT or KEYWORD.
    # Let's simple check: val.strip()
    clean = [tok for tok in tokens if tok[1].strip()]
    return clean, state, tokens

def test_tokenizer_structure():
    clean, _, _ = get_clean_tokens("x = 1")
    assert len(clean) > 0

def test_tokenize_basic():
    clean, _, _ = get_clean_tokens("import os")
    vals = [x[1] for x in clean]
    assert "import" in vals
    assert "os" in vals

def test_tokenize_strings_variations():
    # Single Quote
    clean, _, _ = get_clean_tokens("s = 'Hello'")
    # s, =, ', Hello, '
    assert clean[2][1] == "'"     # Start quote
    assert clean[3][1] == "Hello" # Content
    assert clean[4][1] == "'"     # End quote
    
    # Double Quote
    clean, _, _ = get_clean_tokens('s = "World"')
    assert clean[2][1] == '"'
    
    # Triple Single
    clean, _, _ = get_clean_tokens("s = '''Doc'''")
    assert clean[2][1] == "'''"
    assert clean[3][1] == "Doc"
    assert clean[4][1] == "'''"
    
    # Triple Double
    clean, _, _ = get_clean_tokens('s = """Doc"""')
    assert clean[2][1] == '"""'

def test_tokenize_escapes():
    clean, _, _ = get_clean_tokens(r"s = 'Don\'t'")
    # s, =, ', Don\'t, '
    # The tokenizer logic for escapes inside string state handles it as content until next quote?
    # Actually tokenizer.py lines 66: checks for \'
    
    vals = "".join([x[1] for x in clean])
    assert "Don\\'t" in vals or "Don\'t" in vals

def test_tokenize_keywords_and_context():
    # def func
    clean, _, _ = get_clean_tokens("def my_func():")
    # def, my_func, (, )
    assert clean[0][0] == TokenType.KEYWORD
    assert clean[1][0] == TokenType.FUNCTION_DEF
    
    # class MyClass
    clean, _, _ = get_clean_tokens("class MyClass:")
    assert clean[0][0] == TokenType.KEYWORD
    assert clean[1][0] == TokenType.CLASS_DEF

def test_tokenize_builtins():
    clean, _, _ = get_clean_tokens("print(len(x))")
    # print, (, len, (, x, ), )
    assert clean[0][0] == TokenType.BUILTIN
    assert clean[2][0] == TokenType.BUILTIN

def test_tokenize_numbers():
    clean, _, raw = get_clean_tokens("x = 12345")
    # x, =, 12345
    assert clean[2][0] == TokenType.NUMBER
    assert clean[2][1] == "12345"

def test_tokenize_comment():
    # comments might have spaces, so raw tokens might be better
    t = Tokenizer()
    tokens, _ = t.tokenize("x=1 # Comment")
    last = tokens[-1]
    assert last[0] == TokenType.COMMENT
    assert "# Comment" in last[1]

def test_incomplete_string():
    t = Tokenizer()
    tokens, state = t.tokenize("s = 'Not Finished")
    assert state != 0
