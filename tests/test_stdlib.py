"""
Tests for the NooCrush standard library.
"""
import pytest
from noocrush.interpreter import Interpreter
from noocrush.lexer import Scanner
from noocrush.parser import Parser

class TestStandardLibrary:
    """Test suite for the NooCrush standard library."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.interpreter = Interpreter()
        
    def interpret(self, source):
        """Helper method to interpret source code."""
        scanner = Scanner()
        scanner.source = source
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        return self.interpreter.interpret(statements)
    
    # Math functions
    def test_math_functions(self):
        """Test mathematical functions."""
        # Basic math
        assert self.interpret("abs(-5)") == 5
        assert self.interpret("min(3, 1, 4, 2)") == 1
        assert self.interpret("max(3, 1, 4, 2)") == 4
        assert self.interpret("pow(2, 3)") == 8
        assert self.interpret("sqrt(16)") == 4.0
        assert self.interpret("round(3.14159, 2)") == 3.14
        
        # Trigonometry (values are approximate)
        assert abs(self.interpret("sin(0)")) < 1e-10
        assert abs(self.interpret("cos(0)") - 1) < 1e-10
        assert abs(self.interpret("tan(0)")) < 1e-10
        
        # Constants
        assert abs(self.interpret("PI") - 3.141592653589793) < 1e-10
        assert abs(self.interpret("E") - 2.718281828459045) < 1e-10
    
    # String functions
    def test_string_functions(self):
        """Test string manipulation functions."""
        # Basic string operations
        assert self.interpret('len("hello")') == 5
        assert self.interpret('"hello".upper()') == "HELLO"
        assert self.interpret('"HELLO".lower()') == "hello"
        assert self.interpret('" hello ".trim()') == "hello"
        
        # String searching
        assert self.interpret('"hello".index("e")') == 1
        assert self.interpret('"hello".contains("ll")') is True
        assert self.interpret('"hello".startsWith("he")') is True
        assert self.interpret('"hello".endsWith("lo")') is True
        
        # String manipulation
        assert self.interpret('"hello".replace("l", "x")') == "hexxo"
        assert self.interpret('"hello".substring(1, 3)"') == "el"
        assert self.interpret('"a,b,c".split(",")') == ["a", "b", "c"]
        assert self.interpret('" ".join(["a", "b", "c"])') == "a b c"
    
    # List functions
    def test_list_functions(self):
        """Test list manipulation functions."""
        # List creation and basic operations
        assert self.interpret("len([1, 2, 3])") == 3
        assert self.interpret("[1, 2, 3].length()") == 3
        
        # List manipulation
        self.interpret("let list = [1, 2];")
        self.interpret("list.push(3);")
        assert self.interpret("list") == [1, 2, 3]
        
        assert self.interpret("list.pop()") == 3
        assert self.interpret("list") == [1, 2]
        
        self.interpret("list.unshift(0);")
        assert self.interpret("list") == [0, 1, 2]
        
        assert self.interpret("list.shift()") == 0
        assert self.interpret("list") == [1, 2]
        
        # List operations
        self.interpret("let nums = [3, 1, 4, 1, 5];")
        assert self.interpret("nums.sort()") == [1, 1, 3, 4, 5]
        assert self.interpret("nums.reverse()") == [5, 4, 3, 1, 1]
        assert self.interpret("nums.includes(3)") is True
        assert self.interpret("nums.includes(9)") is False
        
        # List comprehension
        assert self.interpret("[x * 2 for x in [1, 2, 3] if x > 1]") == [4, 6]
    
    # Object/Map functions
    def test_object_functions(self):
        """Test object/map manipulation functions."""
        # Object creation and basic operations
        self.interpret('''
        let person = {
            "name": "Alice",
            "age": 30,
            "city": "Wonderland"
        };
        ''')
        
        assert self.interpret("Object.keys(person)") == ["name", "age", "city"]
        assert self.interpret("Object.values(person)") == ["Alice", 30, "Wonderland"]
        assert self.interpret('Object.hasOwn(person, "name"))') is True
        assert self.interpret('Object.hasOwn(person, "country"))') is False
        
        # Object manipulation
        self.interpret('Object.assign(person, { "country": "Unknown" });')
        assert self.interpret('person.country') == "Unknown"
        
        # Object from entries
        assert self.interpret('''
        let entries = [["a", 1], ["b", 2]];
        let obj = Object.fromEntries(entries);
        obj.a + obj.b
        ''') == 3
    
    # Functional programming
    def test_functional_programming(self):
        """Test functional programming utilities."""
        # Map, filter, reduce
        assert self.interpret("[1, 2, 3].map(fn(x) { return x * 2 })") == [2, 4, 6]
        assert self.interpret("[1, 2, 3, 4].filter(fn(x) { return x % 2 == 0 })") == [2, 4]
        assert self.interpret("[1, 2, 3, 4].reduce(fn(acc, x) { return acc + x }, 0)") == 10
        
        # Range
        assert self.interpret("range(5)") == [0, 1, 2, 3, 4]
        assert self.interpret("range(1, 4)") == [1, 2, 3]
        assert self.interpret("range(0, 10, 2)") == [0, 2, 4, 6, 8]
        
        # Zip
        assert self.interpret('zip([1, 2], ["a", "b"])') == [[1, "a"], [2, "b"]]
    
    # I/O functions (mocked)
    def test_io_functions(self, mocker):
        """Test I/O functions with mocks."""
        # Mock print
        mock_print = mocker.patch('builtins.print')
        self.interpret('print("Hello, World!");')
        mock_print.assert_called_once_with("Hello, World!")
        
        # Mock input
        mocker.patch('builtins.input', return_value="42")
        assert self.interpret('input("Enter a number: ")') == "42"
        
        # File I/O would be tested with temporary files in a real scenario
    
    # Date and time
    def test_datetime_functions(self):
        """Test date and time functions."""
        # Current timestamp (just check it's a number)
        timestamp = self.interpret("Date.now()")
        assert isinstance(timestamp, (int, float))
        assert timestamp > 0
        
        # Date formatting
        # Note: Exact output depends on the implementation and locale
        date_str = self.interpret('new Date(2000, 0, 1).toISOString()')
        assert isinstance(date_str, str)
        assert "2000" in date_str
    
    # JSON
    def test_json_functions(self):
        """Test JSON parsing and stringification."""
        # Stringify
        assert self.interpret('JSON.stringify({ "a": 1, "b": 2 })') == '{"a":1,"b":2}'
        
        # Parse
        assert self.interpret('JSON.parse("{\"a\":1,\"b\":2}")') == {"a": 1, "b": 2}
    
    # Error handling
    def test_error_handling(self):
        """Test error handling utilities."""
        # Try-catch
        source = """
        let result;
        try {
            throw "Something went wrong";
            result = "success";
        } catch (e) {
            result = "caught: " + e;
        }
        result
        """
        assert self.interpret(source) == "caught: Something went wrong"
        
        # Finally
        source = """
        let result = [];
        try {
            result.push("try");
            throw "error";
        } catch (e) {
            result.push("catch");
        } finally {
            result.push("finally");
        }
        result
        """
        assert self.interpret(source) == ["try", "catch", "finally"]
    
    # Concurrency
    def test_concurrency(self):
        """Test concurrency utilities."""
        # This would test async/await, promises, etc.
        # For now, we'll just test basic syntax
        pass
    
    # Modules
    def test_modules(self):
        """Test module system."""
        # This would test module imports and exports
        # For now, we'll just test basic syntax
        pass
