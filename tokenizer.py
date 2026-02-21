# -*- coding: utf-8 -*-
"""
Lightweight, context-aware Python tokenizer.
"""

class TokenType:
    TEXT = "TEXT"
    KEYWORD = "KEYWORD"
    BUILTIN = "BUILTIN"
    STRING = "STRING"
    COMMENT = "COMMENT"
    NUMBER = "NUMBER"
    OP = "OP"
    FUNCTION_DEF = "FUNCTION_DEF"
    CLASS_DEF = "CLASS_DEF"

class TokenizerState:
    ROOT = 0
    STRING_SINGLE = 1     # '...'
    STRING_DOUBLE = 2     # "..."
    STRING_TRIPLE_S = 3   # '''...'''
    STRING_TRIPLE_D = 4   # """..."""
    DEF_FOUND = 5         # after 'def'
    CLASS_FOUND = 6       # after 'class'

class Tokenizer:
    KEYWORDS = {
        "def", "import", "from", "return", "if", "else", "elif",
        "for", "while", "class", "try", "except", "pass", "break",
        "continue", "and", "or", "not", "in", "is", "None", "True", "False",
        "as", "with", "lambda", "yield", "raise", "finally", "assert",
        "global", "nonlocal", "del"
    }

    BUILTINS = {
        "print", "len", "input", "str", "int", "float", "list",
        "dict", "set", "range", "enumerate", "open", "type",
        "super", "zip", "map", "filter", "bool", "tuple", "abs",
        "min", "max", "sum", "sorted", "reversed", "isinstance",
        "id", "chr", "ord", "hex", "bin", "oct"
    }

    def __init__(self):
        pass

    def tokenize(self, text, start_state=TokenizerState.ROOT):
        """
        Tokenizes a single line or text chunk.
        Returns (tokens, end_state).
        Each token is (TokenType, value).
        """
        tokens = []
        state = start_state
        i = 0
        length = len(text)
        
        while i < length:
            char = text[i]

            # --- Handling Strings (Stateful) ---
            if state in (TokenizerState.STRING_SINGLE, TokenizerState.STRING_DOUBLE, 
                         TokenizerState.STRING_TRIPLE_S, TokenizerState.STRING_TRIPLE_D):
                
                # Check for end of string
                if state == TokenizerState.STRING_SINGLE:
                    if char == "'" and (i == 0 or text[i-1] != '\\' or (i > 1 and text[i-2] == '\\')):
                        tokens.append((TokenType.STRING, "'"))
                        state = TokenizerState.ROOT
                        i += 1
                    else:
                        # Consume until next potential quote or EOL
                        start = i
                        while i < length:
                            if text[i] == "'" and (i == 0 or text[i-1] != '\\' or (i > 1 and text[i-2] == '\\')):
                                break
                            i += 1
                        tokens.append((TokenType.STRING, text[start:i]))

                elif state == TokenizerState.STRING_DOUBLE:
                    if char == '"' and (i == 0 or text[i-1] != '\\' or (i > 1 and text[i-2] == '\\')):
                        tokens.append((TokenType.STRING, '"'))
                        state = TokenizerState.ROOT
                        i += 1
                    else:
                        start = i
                        while i < length:
                            if text[i] == '"' and (i == 0 or text[i-1] != '\\' or (i > 1 and text[i-2] == '\\')):
                                break
                            i += 1
                        tokens.append((TokenType.STRING, text[start:i]))
                
                elif state == TokenizerState.STRING_TRIPLE_S:
                    if i + 2 < length and text[i:i+3] == "'''" and (i == 0 or text[i-1] != '\\'):
                        tokens.append((TokenType.STRING, "'''"))
                        state = TokenizerState.ROOT
                        i += 3
                    else:
                        start = i
                        while i < length:
                            if i + 2 < length and text[i:i+3] == "'''" and (i == 0 or text[i-1] != '\\'):
                                break
                            i += 1
                        tokens.append((TokenType.STRING, text[start:i]))
                        
                elif state == TokenizerState.STRING_TRIPLE_D:
                    if i + 2 < length and text[i:i+3] == '"""' and (i == 0 or text[i-1] != '\\'):
                        tokens.append((TokenType.STRING, '"""'))
                        state = TokenizerState.ROOT
                        i += 3
                    else:
                        start = i
                        while i < length:
                            if i + 2 < length and text[i:i+3] == '"""' and (i == 0 or text[i-1] != '\\'):
                                break
                            i += 1
                        tokens.append((TokenType.STRING, text[start:i]))
                continue

            # --- Handling Comments ---
            if char == '#':
                tokens.append((TokenType.COMMENT, text[i:]))
                # Comment terminates line, but we usually return to ROOT state unless inside multi-line string (handled above)
                # If we were in DEF_FOUND or CLASS_FOUND, a comment cancels it? 
                # e.g. def # comment \n foo() -> valid? Yes.
                # For simplicity, let's keep the state if it's structural, but usually safe to reset or keep.
                i = length
                continue

            # --- Starting Strings ---
            if char == '"' or char == "'":
                # Check for triple quotes
                is_triple = False
                if i + 2 < length and text[i:i+3] == char * 3:
                    is_triple = True
                
                quote_type = char * 3 if is_triple else char
                
                # Determine new state
                if quote_type == "'''":
                    new_state = TokenizerState.STRING_TRIPLE_S
                    token_val = "'''"
                    step = 3
                elif quote_type == '"""':
                    new_state = TokenizerState.STRING_TRIPLE_D
                    token_val = '"""'
                    step = 3
                elif quote_type == "'":
                    new_state = TokenizerState.STRING_SINGLE
                    token_val = "'"
                    step = 1
                else: # '"'
                    new_state = TokenizerState.STRING_DOUBLE
                    token_val = '"'
                    step = 1
                
                tokens.append((TokenType.STRING, token_val))
                state = new_state
                i += step
                continue

            # --- Identifiers / Keywords ---
            if char.isalpha() or char == '_':
                start = i
                while i < length and (text[i].isalnum() or text[i] == '_'):
                    i += 1
                word = text[start:i]
                
                token_type = TokenType.TEXT
                
                # Context Check
                if state == TokenizerState.DEF_FOUND:
                    token_type = TokenType.FUNCTION_DEF
                    state = TokenizerState.ROOT
                elif state == TokenizerState.CLASS_FOUND:
                    token_type = TokenType.CLASS_DEF
                    state = TokenizerState.ROOT
                elif word in self.KEYWORDS:
                    token_type = TokenType.KEYWORD
                    if word == "def":
                        state = TokenizerState.DEF_FOUND
                    elif word == "class":
                        state = TokenizerState.CLASS_FOUND
                elif word in self.BUILTINS:
                    token_type = TokenType.BUILTIN
                
                tokens.append((token_type, word))
                continue

            # --- Numbers ---
            if char.isdigit():
                start = i
                has_dot = False
                while i < length:
                    if text[i].isdigit():
                        i += 1
                    elif text[i] == '.' and not has_dot and i + 1 < length and text[i+1].isdigit():
                        has_dot = True
                        i += 1
                    else:
                        break
                tokens.append((TokenType.NUMBER, text[start:i]))
                continue

            # --- Whitespace ---
            if char.isspace():
                tokens.append((TokenType.TEXT, char))
                i += 1
                continue

            # --- Operators / Punctuation ---
            tokens.append((TokenType.OP, char))
            i += 1
            
            # Reset structural states on certain punctuation if needed
            # e.g. def name(:) -> ( resets? No, name does.
            # But "def (" is syntax error.
            # safe to leave logic as matches next word.
        
        return tokens, state
