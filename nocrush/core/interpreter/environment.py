"""
Environment for variable storage and scoping in the NooCrush interpreter.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum, auto

from noocrush.core.ast.nodes import Node, FunctionDef, ClassDef
from noocrush.core.lexer.tokens import Token


class VariableScope(Enum):
    """Enum for variable scope types."""
    GLOBAL = auto()
    LOCAL = auto()
    NONLOCAL = auto()
    CLASS = auto()
    INSTANCE = auto()
    FREE = auto()
    CELL = auto()


@dataclass
class Variable:
    """Represents a variable with its value and scope information."""
    name: str
    value: Any
    scope: VariableScope
    is_constant: bool = False
    type_annotation: Optional[Node] = None
    defined_at: Optional[Token] = None
    is_captured: bool = False
    is_used: bool = False
    
    def __post_init__(self):
        """Initialize the variable."""
        if self.scope == VariableScope.GLOBAL and self.is_constant:
            raise ValueError("Global variables cannot be constant")


@dataclass
class FunctionInfo:
    """Additional information about a function."""
    node: FunctionDef
    closure: Dict[str, Variable] = field(default_factory=dict)
    is_generator: bool = False
    is_async: bool = False
    is_method: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    is_property: bool = False


@dataclass
class ClassInfo:
    """Additional information about a class."""
    node: ClassDef
    bases: List[Any] = field(default_factory=list)
    namespace: Dict[str, Any] = field(default_factory=dict)
    mro: List[Any] = field(default_factory=list)
    is_frozen: bool = False


class Environment:
    """
    Environment for variable storage and scoping.
    
    This class implements a chain of scopes for variable lookup and assignment.
    """
    
    def __init__(self, enclosing=None, name: str = None):
        """
        Initialize the environment.
        
        Args:
            enclosing: The enclosing environment (for nested scopes).
            name: Optional name for the environment (for debugging).
        """
        self.enclosing = enclosing
        self.name = name or f"env_{id(self)}"
        self.values: Dict[str, Variable] = {}
        self.constants: Dict[str, Any] = {}
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.types: Dict[str, type] = {}
        self.modules: Dict[str, Any] = {}
        self.return_value = None
        self.loop_control = None  # For break/continue
        self.is_returning = False
        self.is_breaking = False
        self.is_continuing = False
    
    def define(self, name: str, value: Any, scope: VariableScope = VariableScope.LOCAL,
              is_constant: bool = False, type_annotation: Node = None,
              defined_at: Token = None) -> None:
        """
        Define a new variable in the current scope.
        
        Args:
            name: The name of the variable.
            value: The value to assign.
            scope: The scope of the variable.
            is_constant: Whether the variable is constant.
            type_annotation: Optional type annotation.
            defined_at: Token where the variable was defined (for error messages).
        """
        if name in self.values:
            # Variable already exists in this scope
            var = self.values[name]
            if var.scope == scope and not var.is_captured:
                raise NameError(f"Duplicate variable '{name}' in {scope.name} scope")
        
        self.values[name] = Variable(
            name=name,
            value=value,
            scope=scope,
            is_constant=is_constant,
            type_annotation=type_annotation,
            defined_at=defined_at
        )
    
    def assign(self, name: str, value: Any, is_nonlocal: bool = False) -> None:
        """
        Assign a value to a variable, looking up the scope chain.
        
        Args:
            name: The name of the variable.
            value: The value to assign.
            is_nonlocal: Whether this is a nonlocal assignment.
            
        Raises:
            NameError: If the variable is not found.
        """
        env = self._find_containing_env(name)
        
        if env is None:
            # Variable doesn't exist, create it in the global scope
            if is_nonlocal:
                raise NameError(f"no binding for nonlocal '{name}' found")
            self.define(name, value, VariableScope.GLOBAL)
            return
        
        # Check if the variable is constant
        var = env.values.get(name)
        if var and var.is_constant:
            raise TypeError(f"Cannot assign to constant '{name}'")
        
        # Update the variable's value
        if name in env.values:
            env.values[name].value = value
            env.values[name].is_used = True
        else:
            # This shouldn't happen due to _find_containing_env check
            env.define(name, value)
    
    def get(self, name: str) -> Any:
        """
        Get the value of a variable, looking up the scope chain.
        
        Args:
            name: The name of the variable.
            
        Returns:
            The value of the variable.
            
        Raises:
            NameError: If the variable is not found.
        """
        env = self._find_containing_env(name)
        if env is None:
            raise NameError(f"Name '{name}' is not defined")
        
        var = env.values.get(name)
        if var is None:
            # This shouldn't happen due to _find_containing_env check
            raise NameError(f"Name '{name}' is not defined")
        
        var.is_used = True
        return var.value
    
    def get_at(self, distance: int, name: str) -> Any:
        """
        Get a variable at a specific scope distance (for closures).
        
        Args:
            distance: The number of environments to traverse up.
            name: The name of the variable.
            
        Returns:
            The value of the variable.
        """
        return self._ancestor(distance).values[name].value
    
    def assign_at(self, distance: int, name: str, value: Any) -> None:
        """
        Assign to a variable at a specific scope distance (for closures).
        
        Args:
            distance: The number of environments to traverse up.
            name: The name of the variable.
            value: The value to assign.
        """
        self._ancestor(distance).values[name].value = value
    
    def define_function(self, name: str, function: FunctionDef, **kwargs) -> None:
        """
        Define a function in the current environment.
        
        Args:
            name: The name of the function.
            function: The function definition node.
            **kwargs: Additional function info.
        """
        self.functions[name] = FunctionInfo(node=function, **kwargs)
    
    def get_function(self, name: str) -> Optional[FunctionInfo]:
        """
        Get information about a function, looking up the scope chain.
        
        Args:
            name: The name of the function.
            
        Returns:
            FunctionInfo if found, None otherwise.
        """
        env = self
        while env is not None:
            if name in env.functions:
                return env.functions[name]
            env = env.enclosing
        return None
    
    def define_class(self, name: str, class_def: ClassDef, **kwargs) -> None:
        """
        Define a class in the current environment.
        
        Args:
            name: The name of the class.
            class_def: The class definition node.
            **kwargs: Additional class info.
        """
        self.classes[name] = ClassInfo(node=class_def, **kwargs)
    
    def get_class(self, name: str) -> Optional[ClassInfo]:
        """
        Get information about a class, looking up the scope chain.
        
        Args:
            name: The name of the class.
            
        Returns:
            ClassInfo if found, None otherwise.
        """
        env = self
        while env is not None:
            if name in env.classes:
                return env.classes[name]
            env = env.enclosing
        return None
    
    def define_type(self, name: str, type_obj: type) -> None:
        """
        Define a type in the current environment.
        
        Args:
            name: The name of the type.
            type_obj: The type object.
        """
        self.types[name] = type_obj
    
    def get_type(self, name: str) -> Optional[type]:
        """
        Get a type by name, looking up the scope chain.
        
        Args:
            name: The name of the type.
            
        Returns:
            The type object if found, None otherwise.
        """
        env = self
        while env is not None:
            if name in env.types:
                return env.types[name]
            env = env.enclosing
        return None
    
    def import_module(self, name: str, module: Any) -> None:
        """
        Import a module into the current environment.
        
        Args:
            name: The name to import the module as.
            module: The module object.
        """
        self.modules[name] = module
    
    def get_module(self, name: str) -> Any:
        """
        Get an imported module.
        
        Args:
            name: The name of the module.
            
        Returns:
            The module object if found, None otherwise.
        """
        return self.modules.get(name)
    
    def _find_containing_env(self, name: str) -> Optional['Environment']:
        """
        Find the environment that contains the given variable name.
        
        Args:
            name: The name of the variable.
            
        Returns:
            The environment containing the variable, or None if not found.
        """
        env = self
        while env is not None:
            if name in env.values:
                return env
            env = env.enclosing
        return None
    
    def _ancestor(self, distance: int) -> 'Environment':
        """
        Get an ancestor environment at the given distance.
        
        Args:
            distance: The number of environments to traverse up.
            
        Returns:
            The ancestor environment.
            
        Raises:
            RuntimeError: If the distance is invalid.
        """
        env = self
        for _ in range(distance):
            if env.enclosing is None:
                raise RuntimeError("Invalid environment distance")
            env = env.enclosing
        return env
    
    def child(self, name: str = None) -> 'Environment':
        """
        Create a new child environment.
        
        Args:
            name: Optional name for the child environment.
            
        Returns:
            A new child environment.
        """
        return Environment(enclosing=self, name=name)
    
    def fork(self) -> 'Environment':
        """
        Create a fork of the current environment.
        
        Returns:
            A new environment with the same values as this one.
        """
        new_env = Environment(enclosing=self.enclosing, name=f"{self.name}_fork")
        new_env.values = self.values.copy()
        new_env.functions = self.functions.copy()
        new_env.classes = self.classes.copy()
        new_env.types = self.types.copy()
        new_env.modules = self.modules.copy()
        return new_env
    
    def __contains__(self, name: str) -> bool:
        """Check if a variable is defined in this environment or its parents."""
        return self._find_containing_env(name) is not None
    
    def __getitem__(self, name: str) -> Any:
        """Get a variable's value, looking up the scope chain."""
        return self.get(name)
    
    def __setitem__(self, name: str, value: Any) -> None:
        """Set a variable's value, creating it if it doesn't exist."""
        self.assign(name, value)
    
    def __delitem__(self, name: str) -> None:
        """Delete a variable from the current scope."""
        if name in self.values:
            del self.values[name]
        else:
            raise KeyError(f"Name '{name}' is not defined in the current scope")
    
    def __str__(self) -> str:
        """String representation of the environment."""
        return f"<Environment {self.name}>"
    
    def __repr__(self) -> str:
        """Detailed string representation of the environment."""
        return (f"Environment(name='{self.name}', "
                f"enclosing={self.enclosing.name if self.enclosing else None}, "
                f"values={list(self.values.keys())}, "
                f"functions={list(self.functions.keys())}, "
                f"classes={list(self.classes.keys())})")


class ReturnException(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Exception used to implement break statements."""
    pass


class ContinueException(Exception):
    """Exception used to implement continue statements."""
    pass
