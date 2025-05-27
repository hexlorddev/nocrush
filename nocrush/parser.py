"""
Parser for the NooCrush language.
"""
from typing import List, Dict, Any, Optional, Union
from .lexer import Token, TokenType

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> List[Dict]:
        try:
            return self.program()
        except ParseError as e:
            print(f"Parse error: {e}")
            return []
    
    def program(self) -> List[Dict]:
        statements = []
        while not self.is_at_end():
            declaration = self.declaration()
            if declaration:
                statements.append(declaration)
        return statements
    
    def declaration(self) -> Optional[Dict]:
        try:
            if self.match(TokenType.FN):
                return self.function_declaration("function")
            if self.match(TokenType.STRUCT):
                return self.struct_declaration()
            if self.match(TokenType.LET, TokenType.CONST):
                return self.var_declaration()
            return self.statement()
        except ParseError as e:
            self.synchronize()
            return None
    
    def function_declaration(self, kind: str) -> Dict:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                
                # Handle parameter with optional type annotation
                param = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                
                if self.match(TokenType.COLON):
                    param_type = self.parse_type()
                    parameters.append({"name": param.lexeme, "type": param_type})
                else:
                    parameters.append({"name": param.lexeme})
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Return type annotation
        return_type = None
        if self.match(TokenType.MINUS, TokenType.GREATER):
            return_type = self.parse_type()
        
        # Function body
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block_statement()
        
        return {
            "type": "function",
            "name": name.lexeme,
            "parameters": parameters,
            "return_type": return_type,
            "body": body
        }
    
    def struct_declaration(self) -> Dict:
        name = self.consume(TokenType.IDENTIFIER, "Expect struct name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before struct body.")
        
        fields = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            fields.append(self.struct_field())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after struct body.")
        
        return {
            "type": "struct",
            "name": name.lexeme,
            "fields": fields
        }
    
    def struct_field(self) -> Dict:
        mutable = self.match(TokenType.MUT)
        name = self.consume(TokenType.IDENTIFIER, "Expect field name.")
        self.consume(TokenType.COLON, "Expect ':' after field name.")
        field_type = self.parse_type()
        self.consume(TokenType.SEMICOLON, "Expect ';' after field declaration.")
        
        return {
            "name": name.lexeme,
            "type": field_type,
            "mutable": mutable
        }
    
    def parse_type(self) -> str:
        if self.match(TokenType.NUMBER_TYPE):
            return "Number"
        elif self.match(TokenType.STRING_TYPE):
            return "String"
        elif self.match(TokenType.BOOL_TYPE):
            return "Bool"
        elif self.check(TokenType.IDENTIFIER):
            return self.advance().lexeme
        else:
            self.error(self.peek(), "Expect type.")
    
    def var_declaration(self) -> Dict:
        is_const = self.previous().type == TokenType.CONST
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        var_type = None
        if self.match(TokenType.COLON):
            var_type = self.parse_type()
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        
        return {
            "type": "var",
            "name": name.lexeme,
            "var_type": var_type,
            "initializer": initializer,
            "is_const": is_const
        }
    
    def statement(self) -> Dict:
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.LOOP):
            return self.loop_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return {"type": "block", "statements": self.block_statement()}
        else:
            return self.expression_statement()
    
    def if_statement(self) -> Dict:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return {
            "type": "if",
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch
        }
    
    def loop_statement(self) -> Dict:
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before loop body.")
        body = self.block_statement()
        
        return {
            "type": "loop",
            "body": body
        }
    
    def return_statement(self) -> Dict:
        keyword = self.previous()
        value = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return {
            "type": "return",
            "keyword": keyword,
            "value": value
        }
    
    def block_statement(self) -> List[Dict]:
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            decl = self.declaration()
            if decl:
                statements.append(decl)
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def expression_statement(self) -> Dict:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return {
            "type": "expression",
            "expression": expr
        }
    
    def expression(self) -> Dict:
        return self.assignment()
    
    def assignment(self) -> Dict:
        expr = self.or_()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if expr["type"] == "variable":
                return {
                    "type": "assign",
                    "name": expr["name"],
                    "value": value
                }
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def or_(self) -> Dict:
        expr = self.and_()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()
            expr = {
                "type": "logical",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def and_(self) -> Dict:
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = {
                "type": "logical",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def equality(self) -> Dict:
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = {
                "type": "binary",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def comparison(self) -> Dict:
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = {
                "type": "binary",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def term(self) -> Dict:
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = {
                "type": "binary",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def factor(self) -> Dict:
        expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = {
                "type": "binary",
                "left": expr,
                "operator": operator,
                "right": right
            }
        
        return expr
    
    def unary(self) -> Dict:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return {
                "type": "unary",
                "operator": operator,
                "right": right
            }
        
        return self.call()
    
    def call(self) -> Dict:
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: Dict) -> Dict:
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return {
            "type": "call",
            "callee": callee,
            "arguments": arguments,
            "paren": paren
        }
    
    def primary(self) -> Dict:
        if self.match(TokenType.FALSE):
            return {"type": "literal", "value": False, "value_type": "boolean"}
        if self.match(TokenType.TRUE):
            return {"type": "literal", "value": True, "value_type": "boolean"}
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return {
                "type": "literal",
                "value": self.previous().literal,
                "value_type": "number" if self.previous().type == TokenType.NUMBER else "string"
            }
        if self.match(TokenType.IDENTIFIER):
            return {"type": "variable", "name": self.previous().lexeme}
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return {"type": "grouping", "expression": expr}
        
        raise self.error(self.peek(), "Expect expression.")
    
    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str) -> ParseError:
        print(f"[line {token.line}] Error at {token.lexeme}: {message}")
        return ParseError()
    
    def synchronize(self) -> None:
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.FN, TokenType.STRUCT, TokenType.LET, 
                TokenType.IF, TokenType.LOOP, TokenType.RETURN
            ]:
                return
            
            self.advance()
