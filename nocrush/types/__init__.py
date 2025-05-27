""
Type system for NooCrush language.
"""
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic, Callable
from dataclasses import dataclass
from enum import Enum, auto

class TypeKind(Enum):
    """Kinds of types in the NooCrush type system."""
    ANY = auto()
    NEVER = auto()
    VOID = auto()
    NULL = auto()
    BOOLEAN = auto()
    NUMBER = auto()
    STRING = auto()
    LIST = auto()
    FUNCTION = auto()
    STRUCT = auto()
    UNION = auto()
    INTERSECTION = auto()
    GENERIC = auto()
    TYPE_VARIABLE = auto()

@dataclass
class Type:
    """Base class for all types in the NooCrush type system."""
    kind: TypeKind
    name: str = ""
    
    def is_subtype_of(self, other: 'Type') -> bool:
        """Check if this type is a subtype of another type."""
        if self == other:
            return True
        
        # Any is a supertype of all types except Never
        if other.kind == TypeKind.ANY:
            return self.kind != TypeKind.NEVER
        
        # Never is a subtype of all types
        if self.kind == TypeKind.NEVER:
            return True
            
        # Handle union types
        if other.kind == TypeKind.UNION:
            return any(self.is_subtype_of(t) for t in other.types)
            
        # Handle intersection types
        if self.kind == TypeKind.INTERSECTION:
            return all(t.is_subtype_of(other) for t in self.types)
            
        # List covariance
        if (self.kind == TypeKind.LIST and 
            other.kind == TypeKind.LIST and 
            isinstance(self, ListType) and 
            isinstance(other, ListType)):
            return self.element_type.is_subtype_of(other.element_type)
            
        # Function parameter contravariance and return type covariance
        if (self.kind == TypeKind.FUNCTION and 
            other.kind == TypeKind.FUNCTION and
            isinstance(self, FunctionType) and 
            isinstance(other, FunctionType)):
            
            # Parameter types must be contravariant
            if len(self.parameter_types) != len(other.parameter_types):
                return False
                
            for self_param, other_param in zip(self.parameter_types, other.parameter_types):
                if not other_param.is_subtype_of(self_param):
                    return False
            
            # Return type must be covariant
            return self.return_type.is_subtype_of(other.return_type)
        
        # Struct subtyping (nominal typing)
        if self.kind == TypeKind.STRUCT and other.kind == TypeKind.STRUCT:
            # For now, we use nominal typing for structs
            return self.name == other.name
            
        return False
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Type):
            return False
        return self.kind == other.kind and self.name == other.name
    
    def __hash__(self) -> int:
        return hash((self.kind, self.name))
    
    def __str__(self) -> str:
        return self.name if self.name else self.kind.name.lower()

@dataclass
class PrimitiveType(Type):
    """Primitive type like number, string, boolean, etc."""
    pass

@dataclass
class ListType(Type):
    """List type with element type."""
    element_type: Type = Type(TypeKind.ANY)
    
    def __post_init__(self):
        self.kind = TypeKind.LIST
        if not self.name:
            self.name = f"List[{self.element_type}]"
    
    def __str__(self) -> str:
        return f"List[{self.element_type}]"

@dataclass
class FunctionType(Type):
    """Function type with parameter types and return type."""
    parameter_types: List[Type] = None
    return_type: Type = Type(TypeKind.VOID)
    type_parameters: List[str] = None
    
    def __post_init__(self):
        self.kind = TypeKind.FUNCTION
        if self.parameter_types is None:
            self.parameter_types = []
        if self.type_parameters is None:
            self.type_parameters = []
        if not self.name:
            params = ", ".join(str(t) for t in self.parameter_types)
            self.name = f"({params}) -> {self.return_type}"
    
    def __str__(self) -> str:
        params = ", ".join(str(t) for t in self.parameter_types)
        return f"({params}) -> {self.return_type}"

@dataclass
class StructType(Type):
    """Struct type with field types."""
    fields: Dict[str, Type] = None
    type_parameters: List[str] = None
    
    def __post_init__(self):
        self.kind = TypeKind.STRUCT
        if self.fields is None:
            self.fields = {}
        if self.type_parameters is None:
            self.type_parameters = []
    
    def get_field_type(self, name: str) -> Optional[Type]:
        """Get the type of a field by name."""
        return self.fields.get(name)
    
    def __str__(self) -> str:
        if self.name:
            return self.name
        fields = ", ".join(f"{name}: {typ}" for name, typ in self.fields.items())
        return f"{{ {fields} }}"

@dataclass
class UnionType(Type):
    """Union type representing multiple possible types."""
    types: List[Type] = None
    
    def __post_init__(self):
        self.kind = TypeKind.UNION
        if self.types is None:
            self.types = []
        if not self.name:
            self.name = " | ".join(str(t) for t in self.types)
    
    def __str__(self) -> str:
        return " | ".join(str(t) for t in self.types)

@dataclass
class IntersectionType(Type):
    """Intersection type representing types that must all be satisfied."""
    types: List[Type] = None
    
    def __post_init__(self):
        self.kind = TypeKind.INTERSECTION
        if self.types is None:
            self.types = []
        if not self.name:
            self.name = " & ".join(str(t) for t in self.types)
    
    def __str__(self) -> str:
        return " & ".join(str(t) for t in self.types)

@dataclass
class TypeVariable(Type):
    """Type variable for generic types."""
    def __post_init__(self):
        self.kind = TypeKind.TYPE_VARIABLE
    
    def __str__(self) -> str:
        return self.name if self.name else "T"

# Commonly used types
ANY_TYPE = Type(TypeKind.ANY, "any")
NEVER_TYPE = Type(TypeKind.NEVER, "never")
VOID_TYPE = Type(TypeKind.VOID, "void")
NULL_TYPE = Type(TypeKind.NULL, "null")
BOOLEAN_TYPE = PrimitiveType(TypeKind.BOOLEAN, "boolean")
NUMBER_TYPE = PrimitiveType(TypeKind.NUMBER, "number")
STRING_TYPE = PrimitiveType(TypeKind.STRING, "string")

# Type predicates
def is_primitive_type(typ: Type) -> bool:
    """Check if a type is a primitive type."""
    return typ.kind in {
        TypeKind.BOOLEAN,
        TypeKind.NUMBER,
        TypeKind.STRING,
        TypeKind.NULL,
        TypeKind.VOID,
        TypeKind.ANY,
        TypeKind.NEVER
    }

def is_assignable(target: Type, source: Type) -> bool:
    """Check if a value of source type can be assigned to a target of target type."""
    # Any type can be assigned to any (except never)
    if target.kind == TypeKind.ANY:
        return source.kind != TypeKind.NEVER
    
    # Never can be assigned to any type
    if source.kind == TypeKind.NEVER:
        return True
    
    # Check subtyping relationship
    return source.is_subtype_of(target)

def get_common_supertype(types: List[Type]) -> Type:
    """Find the most specific common supertype of the given types."""
    if not types:
        return NEVER_TYPE
    
    # If all types are the same, return that type
    if all(t == types[0] for t in types[1:]):
        return types[0]
    
    # For now, return the union of all types
    # In a more sophisticated type system, we would find the most specific common supertype
    return UnionType(types=list(set(types)))

def instantiate_generic(
    generic_type: Type,
    type_arguments: Dict[str, Type]
) -> Type:
    """
    Instantiate a generic type with the given type arguments.
    
    Args:
        generic_type: The generic type to instantiate
        type_arguments: Mapping from type parameter names to concrete types
        
    Returns:
        A new type with type parameters replaced by the given arguments
    """
    if not type_arguments:
        return generic_type
    
    if isinstance(generic_type, TypeVariable):
        return type_arguments.get(generic_type.name, generic_type)
    
    if isinstance(generic_type, ListType):
        return ListType(
            element_type=instantiate_generic(generic_type.element_type, type_arguments)
        )
    
    if isinstance(generic_type, FunctionType):
        return FunctionType(
            parameter_types=[
                instantiate_generic(t, type_arguments)
                for t in generic_type.parameter_types
            ],
            return_type=instantiate_generic(generic_type.return_type, type_arguments),
            type_parameters=[
                t for t in generic_type.type_parameters
                if t not in type_arguments
            ]
        )
    
    if isinstance(generic_type, StructType):
        return StructType(
            name=generic_type.name,
            fields={
                name: instantiate_generic(field_type, type_arguments)
                for name, field_type in generic_type.fields.items()
            },
            type_parameters=[
                t for t in generic_type.type_parameters
                if t not in type_arguments
            ]
        )
    
    if isinstance(generic_type, (UnionType, IntersectionType)):
        return type(generic_type)(
            types=[
                instantiate_generic(t, type_arguments)
                for t in generic_type.types
            ]
        )
    
    return generic_type
