"""
Interpreter for the NooCrush programming language.
"""
from typing import Any, Dict, List, Optional, Callable
import operator
import sys

from noocrush.core.ast.nodes import *
from noocrush.core.lexer.tokens import Token, TokenType
from noocrush.core.interpreter.environment import Environment, ReturnException, BreakException, ContinueException
from noocrush.core.interpreter.utils import is_truthy, is_equal, stringify, is_callable, is_iterable

class Interpreter:
    """Tree-walking interpreter for NooCrush."""
    
    def __init__(self, debug: bool = False):
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Node, int] = {}
        self.debug = debug
        self._init_builtins()
    
    def _init_builtins(self) -> None:
        """Initialize built-in functions and constants."""
        from noocrush.core.interpreter.builtins import create_builtins
        for name, func in create_builtins().items():
            self.globals.define(name, func)
        
        self.globals.define("None", None)
        self.globals.define("True", True)
        self.globals.define("False", False)
    
    def interpret(self, statements: List[Stmt]) -> None:
        """Execute a list of statements."""
        try:
            for stmt in statements:
                self._execute(stmt)
        except RuntimeError as e:
            self._runtime_error(str(e))
    
    def _execute(self, stmt: Stmt) -> None:
        """Execute a single statement."""
        method_name = f"_execute_{stmt.__class__.__name__.lower()}"
        method = getattr(self, method_name, self._generic_execute)
        return method(stmt)
    
    def _generic_execute(self, stmt: Stmt) -> None:
        """Handle unsupported statement types."""
        raise RuntimeError(f"Unsupported statement: {stmt.__class__.__name__}")
    
    def _evaluate(self, expr: Expr) -> Any:
        """Evaluate an expression."""
        method_name = f"_evaluate_{expr.__class__.__name__.lower()}"
        method = getattr(self, method_name, self._generic_evaluate)
        return method(expr)
    
    def _generic_evaluate(self, expr: Expr) -> Any:
        """Handle unsupported expression types."""
        raise RuntimeError(f"Unsupported expression: {expr.__class__.__name__}")
    
    # Statement execution methods
    
    def _execute_expressionstmt(self, stmt: ExprStmt) -> None:
        self._evaluate(stmt.expression)
    
    def _execute_printstmt(self, stmt: PrintStmt) -> None:
        values = [str(self._evaluate(expr)) for expr in stmt.expressions]
        print(" ".join(values))
    
    def _execute_variabledeclaration(self, stmt: VariableDeclaration) -> None:
        value = self._evaluate(stmt.initializer) if stmt.initializer else None
        self.environment.define(stmt.name.lexeme, value, stmt.is_constant)
    
    def _execute_block(self, stmt: Block) -> None:
        self._execute_block_internal(stmt.statements, Environment(self.environment))
    
    def _execute_block_internal(self, stmts: List[Stmt], env: Environment) -> None:
        previous = self.environment
        try:
            self.environment = env
            for stmt in stmts:
                self._execute(stmt)
        finally:
            self.environment = previous
    
    def _execute_ifstmt(self, stmt: IfStmt) -> None:
        if is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)
    
    def _execute_whilestmt(self, stmt: WhileStmt) -> None:
        try:
            while is_truthy(self._evaluate(stmt.condition)):
                try:
                    self._execute(stmt.body)
                except ContinueException:
                    continue
                except BreakException:
                    break
        except ReturnException:
            raise
    
    def _execute_functiondeclaration(self, stmt: FunctionDeclaration) -> None:
        func = Function(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, func)
    
    def _execute_returnstmt(self, stmt: ReturnStmt) -> None:
        value = self._evaluate(stmt.value) if stmt.value else None
        raise ReturnException(value)
    
    def _execute_breakstmt(self, stmt: BreakStmt) -> None:
        raise BreakException()
    
    def _execute_continuestmt(self, stmt: ContinueStmt) -> None:
        raise ContinueException()
    
    # Expression evaluation methods
    
    def _evaluate_literalexpr(self, expr: LiteralExpr) -> Any:
        return expr.value
    
    def _evaluate_variableexpr(self, expr: VariableExpr) -> Any:
        return self._lookup_variable(expr.name, expr)
    
    def _evaluate_assignexpr(self, expr: AssignExpr) -> Any:
        value = self._evaluate(expr.value)
        
        if isinstance(expr.target, VariableExpr):
            self._assign_variable(expr.target.name, value)
        elif isinstance(expr.target, GetExpr):
            obj = self._evaluate(expr.target.obj)
            setattr(obj, expr.target.name.lexeme, value)
        else:
            raise RuntimeError("Invalid assignment target")
        
        return value
    
    def _evaluate_binaryexpr(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        
        op = expr.operator.type
        
        # Arithmetic operations
        if op == TokenType.PLUS:
            return left + right
        elif op == TokenType.MINUS:
            return left - right
        elif op == TokenType.STAR:
            return left * right
        elif op == TokenType.SLASH:
            return left / right
        elif op == TokenType.PERCENT:
            return left % right
        elif op == TokenType.CARET:
            return left ** right
        
        # Comparisons
        elif op == TokenType.GREATER:
            return left > right
        elif op == TokenType.GREATER_EQUAL:
            return left >= right
        elif op == TokenType.LESS:
            return left < right
        elif op == TokenType.LESS_EQUAL:
            return left <= right
        elif op == TokenType.EQUAL_EQUAL:
            return is_equal(left, right)
        elif op == TokenType.BANG_EQUAL:
            return not is_equal(left, right)
        
        raise RuntimeError(f"Unknown operator: {op}")
    
    def _evaluate_logicalexpr(self, expr: LogicalExpr) -> Any:
        left = self._evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if is_truthy(left):
                return left
        else:  # AND
            if not is_truthy(left):
                return left
        
        return self._evaluate(expr.right)
    
    def _evaluate_unaryexpr(self, expr: UnaryExpr) -> Any:
        right = self._evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not is_truthy(right)
        
        raise RuntimeError(f"Unknown operator: {expr.operator.lexeme}")
    
    def _evaluate_callexpr(self, expr: CallExpr) -> Any:
        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]
        
        if not is_callable(callee):
            raise RuntimeError("Can only call functions and classes.")
        
        return callee(*arguments)
    
    def _evaluate_getexpr(self, expr: GetExpr) -> Any:
        obj = self._evaluate(expr.obj)
        
        if hasattr(obj, expr.name.lexeme):
            return getattr(obj, expr.name.lexeme)
        
        method = self._get_method(obj, expr.name.lexeme)
        if method is not None:
            return method
        
        raise Runtime.error(f"Undefined property: {expr.name.lexeme}")
    
    # Helper methods
    
    def _lookup_variable(self, name: Token, expr: Expr) -> Any:
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name.lexeme)
    
    def _assign_variable(self, name: Token, value: Any) -> None:
        distance = self.locals.get(name)
        if distance is not None:
            self.environment.assign_at(distance, name.lexeme, value)
        else:
            self.globals.assign(name.lexeme, value)
    
    def _get_method(self, obj: Any, name: str) -> Optional[Callable]:
        if hasattr(obj, name):
            method = getattr(obj, name)
            if callable(method):
                return method
        return None
    
    def _runtime_error(self, message: str) -> None:
        print(f"Runtime error: {message}", file=sys.stderr)


class Function:
    """Function object for NooCrush."""
    
    def __init__(self, declaration: FunctionDeclaration, closure: Environment, is_initializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    def bind(self, instance: Any) -> 'Function':
        env = Environment(self.closure)
        env.define("this", instance)
        return Function(self.declaration, env, self.is_initializer)
    
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        env = Environment(self.closure)
        
        for i, param in enumerate(self.declaration.params):
            env.define(param.name.lexeme, arguments[i] if i < len(arguments) else None)
        
        try:
            interpreter._execute_block(self.declaration.body, env)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class Class:
    """Class object for NooCrush."""
    
    def __init__(self, name: str, superclass: Optional['Class'], methods: Dict[str, Function]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def find_method(self, name: str) -> Optional[Function]:
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None
    
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> 'Instance':
        instance = Instance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
    
    def __str__(self) -> str:
        return f"<class {self.name}>"


class Instance:
    """Instance of a class in NooCrush."""
    
    def __init__(self, klass: Class):
        self.klass = klass
        self.fields: Dict[str, Any] = {}
    
    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        
        raise RuntimeError(f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"<{self.klass.name} instance>"
