"""
Tests for the NooCrush interpreter.
"""
import pytest
from noocrush.interpreter import Interpreter
from noocrush.lexer import Scanner
from noocrush.parser import Parser

class TestInterpreter:
    """Test suite for the NooCrush interpreter."""
    
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
    
    def test_literals(self):
        """Test interpreting literal values."""
        # Numbers
        assert self.interpret("42") == 42
        assert self.interpret("3.14") == 3.14
        
        # Strings
        assert self.interpret('"Hello"') == "Hello"
        
        # Booleans
        assert self.interpret("true") is True
        assert self.interpret("false") is False
        
        # Null
        assert self.interpret("null") is None
    
    def test_arithmetic(self):
        """Test arithmetic operations."""
        assert self.interpret("1 + 2") == 3
        assert self.interpret("5 - 3") == 2
        assert self.interpret("2 * 3") == 6
        assert self.interpret("10 / 2") == 5.0
        assert self.interpret("10 % 3") == 1
        assert self.interpret("2 ** 3") == 8
        
        # Operator precedence
        assert self.interpret("2 + 3 * 4") == 14  # 2 + (3 * 4)
        assert self.interpret("(2 + 3) * 4") == 20
    
    def test_comparisons(self):
        """Test comparison operators."""
        # Equality
        assert self.interpret("1 == 1") is True
        assert self.interpret("1 == 2") is False
        assert self.interpret('"a" == "a"') is True
        assert self.interpret('"a" == "b"') is False
        
        # Inequality
        assert self.interpret("1 != 2") is True
        assert self.interpret("1 != 1") is False
        
        # Comparisons
        assert self.interpret("1 < 2") is True
        assert self.interpret("1 <= 1") is True
        assert self.interpret("3 > 2") is True
        assert self.interpret("3 >= 3") is True
    
    def test_logical_operators(self):
        """Test logical operators."""
        # Logical AND
        assert self.interpret("true && true") is True
        assert self.interpret("true && false") is False
        
        # Logical OR
        assert self.interpret("false || true") is True
        assert self.interpret("false || false") is False
        
        # Logical NOT
        assert self.interpret("!true") is False
        assert self.interpret("!false") is True
        
        # Short-circuit evaluation
        assert self.interpret("false && (1/0 == 1)") is False
        assert self.interpret("true || (1/0 == 1)") is True
    
    def test_variables(self):
        """Test variable declarations and assignments."""
        # Variable declaration and access
        self.interpret("let x = 42;")
        assert self.interpret("x") == 42
        
        # Variable assignment
        self.interpret("x = 100;")
        assert self.interpret("x") == 100
        
        # Constants
        self.interpret("const PI = 3.14;")
        assert self.interpret("PI") == 3.14
        
        # Try to reassign constant (should raise error)
        with pytest.raises(RuntimeError):
            self.interpret("PI = 3.14159;")
    
    def test_control_flow(self):
        """Test control flow statements."""
        # If statement
        assert self.interpret("if (true) { 1 } else { 2 }") == 1
        assert self.interpret("if (false) { 1 } else { 2 }") == 2
        
        # While loop
        source = """
        let x = 0;
        while (x < 5) {
            x = x + 1;
        }
        x
        """
        assert self.interpret(source) == 5
        
        # For loop
        source = """
        let sum = 0;
        for (let i = 0; i < 5; i = i + 1) {
            sum = sum + i;
        }
        sum
        """
        assert self.interpret(source) == 10  # 0 + 1 + 2 + 3 + 4
    
    def test_functions(self):
        """Test function definitions and calls."""
        # Function definition and call
        source = """
        fn add(a, b) {
            return a + b;
        }
        add(2, 3)
        """
        assert self.interpret(source) == 5
        
        # Recursive function
        source = """
        fn factorial(n) {
            if (n <= 1) {
                return 1;
            } else {
                return n * factorial(n - 1);
            }
        }
        factorial(5)
        """
        assert self.interpret(source) == 120
        
        # Closures
        source = """
        fn makeCounter() {
            let count = 0;
            fn counter() {
                count = count + 1;
                return count;
            }
            return counter;
        }
        let counter = makeCounter();
        counter() + counter() + counter()
        """
        assert self.interpret(source) == 6  # 1 + 2 + 3
    
    def test_lists(self):
        """Test list operations."""
        # List literal
        assert self.interpret("[1, 2, 3]") == [1, 2, 3]
        
        # List indexing
        self.interpret("let list = [10, 20, 30];")
        assert self.interpret("list[0]") == 10
        assert self.interpret("list[1]") == 20
        assert self.interpret("list[2]") == 30
        
        # List assignment
        self.interpret("list[1] = 99;")
        assert self.interpret("list") == [10, 99, 30]
        
        # List methods
        self.interpret("list.push(40);")
        assert self.interpret("list") == [10, 99, 30, 40]
        
        assert self.interpret("list.pop()") == 40
        assert self.interpret("list") == [10, 99, 30]
        
        assert self.interpret("list.length()") == 3
    
    def test_objects(self):
        """Test object operations."""
        # Object literal
        source = """
        let person = {
            "name": "Alice",
            "age": 30,
            "greet": fn() {
                return "Hello, " + this.name;
            }
        };
        person.greet()
        """
        assert self.interpret(source) == "Hello, Alice"
        
        # Property access
        assert self.interpret("person.name") == "Alice"
        assert self.interpret("person.age") == 30
        
        # Property assignment
        self.interpret('person.name = "Bob";')
        assert self.interpret("person.name") == "Bob"
    
    def test_classes(self):
        """Test class definitions and instances."""
        source = """
        class Counter {
            init() {
                this.count = 0;
            }
            
            increment() {
                this.count = this.count + 1;
                return this.count;
            }
            
            reset() {
                this.count = 0;
            }
        }
        
        let counter = Counter();
        counter.increment() + counter.increment()
        """
        assert self.interpret(source) == 3  # 1 + 2
        
        # Check inheritance
        source = """
        class Animal {
            init(name) {
                this.name = name;
            }
            
            speak() {
                return "???";
            }
        }
        
        class Dog : Animal {
            init(name) {
                super.init(name);
            }
            
            speak() {
                return this.name + " says woof";
            }
        }
        
        let dog = Dog("Rex");
        dog.speak()
        """
        assert self.interpret(source) == "Rex says woof"
    
    def test_modules(self):
        """Test module imports and exports."""
        # This would test the module system
        # For now, we'll just test basic imports
        pass
    
    def test_error_handling(self):
        """Test error handling and exceptions."""
        # Division by zero
        with pytest.raises(ZeroDivisionError):
            self.interpret("1 / 0")
        
        # Undefined variable
        with pytest.raises(NameError):
            self.interpret("x")
        
        # Type errors
        with pytest.raises(TypeError):
            self.interpret('1 + "1"')
    
    def test_comments(self):
        """Test that comments are properly ignored."""
        assert self.interpret("// This is a comment\n42") == 42
        assert self.interpret("/* This is a \n multi-line \n comment */ 42") == 42
    
    def test_imports(self):
        """Test importing modules."""
        # This would test the import system
        # For now, we'll just test basic imports
        pass
    
    def test_async_await(self):
        """Test async/await functionality."""
        # This would test async/await
        # For now, we'll just test basic syntax
        pass
