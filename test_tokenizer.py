from tokenizer import Tokenizer, TokenType, TokenizerState
import unittest

class TestTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_basic_assignment(self):
        text = "x = 1"
        tokens, state = self.tokenizer.tokenize(text)
        expected = [
            (TokenType.TEXT, "x"),
            (TokenType.TEXT, " "),
            (TokenType.OP, "="),
            (TokenType.TEXT, " "),
            (TokenType.NUMBER, "1")
        ]
        self.assertEqual(tokens, expected)
        self.assertEqual(state, TokenizerState.ROOT)

    def test_string(self):
        text = 'print("Hello # world")'
        tokens, state = self.tokenizer.tokenize(text)
        # print (BUILTIN)
        # ( (OP)
        # " (STRING)
        # Hello # world (STRING)
        # " (STRING)
        # ) (OP)
        
        # Note: My implementation splits quote char and content
        self.assertEqual(tokens[0], (TokenType.BUILTIN, "print"))
        self.assertEqual(tokens[2], (TokenType.STRING, '"'))
        self.assertEqual(tokens[3], (TokenType.STRING, "Hello # world"))
        self.assertEqual(tokens[4], (TokenType.STRING, '"'))
    
    def test_keyword_masking(self):
        # "in" inside string should be string
        text = '"in"'
        tokens, _ = self.tokenizer.tokenize(text)
        self.assertEqual(tokens[1], (TokenType.STRING, "in"))
        
        # keyword properly detected
        text = "if x in y:"
        tokens, _ = self.tokenizer.tokenize(text)
        types = [t[0] for t in tokens if t[1].strip()]
        self.assertIn(TokenType.KEYWORD, types) # if
        self.assertIn(TokenType.KEYWORD, types) # in are counted

    def test_function_def(self):
        text = "def my_func():"
        tokens, _ = self.tokenizer.tokenize(text)
        # def -> KEYWORD
        # space
        # my_func -> FUNCTION_DEF
        self.assertEqual(tokens[0], (TokenType.KEYWORD, "def"))
        self.assertEqual(tokens[2], (TokenType.FUNCTION_DEF, "my_func"))

    def test_escaped_quote(self):
        text = r'"Escaped \" quote"'
        tokens, _ = self.tokenizer.tokenize(text)
        # "
        # Escaped \" quote
        # "
        self.assertEqual(tokens[0], (TokenType.STRING, '"'))
        self.assertEqual(tokens[1], (TokenType.STRING, 'Escaped \\" quote'))
        self.assertEqual(tokens[2], (TokenType.STRING, '"'))

if __name__ == '__main__':
    unittest.main()
