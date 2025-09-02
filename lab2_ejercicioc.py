def shunting_yard(regex):
    """Infix to postfix"""
    precedence = {
        '|': 1,     # alternation (lowest precedence)
        '.': 2,     # concatenation
        '?': 3,     # zero or one
        '+': 3,     # one or more
        '*': 3,     # zero or more
    }
    
    output = []     
    ops = []        
    i = 0           
    
    def needs_concat(prev_token, next_token):
        """Identifica si se necesita concatenación"""
        left_tokens = {'operand', ')', '*', '+', '?'}
        
        right_tokens = {'operand', '('}
        
        return (prev_token in left_tokens and 
                next_token in right_tokens)

    last_token_type = None  # None, 'operand', 'unary', '(', ')', '|'
    
    while i < len(regex):
        char = regex[i]
        print(ops, output)
        
        # Escapadas
        if char == '\\':
            if i + 1 < len(regex):
                token = regex[i:i+2]
                output.append(token)
                last_token_type = 'operand'
                i += 2
                continue
            else:
                raise ValueError("Invalid escape sequence at end of input")
        
        # Parentesis
        if char == '(':
            # Check if we need concatenation before '('
            if last_token_type in {'operand', 'unary', ')'}:
                # Insert concatenation operator
                while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence['.']:
                    output.append(ops.pop())
                ops.append('.')
                last_token_type = '.'
            
            ops.append(char)
            last_token_type = '('
            i += 1
            continue
        
        if char == ')':
            # Operadores hasta cerrar ")"
            while ops and ops[-1] != '(':
                output.append(ops.pop())
            
            if not ops:
                raise ValueError("Mismatched parentheses")
            
            ops.pop()  # Remove '('
            last_token_type = ')'
            i += 1
            continue
        
        # Operadores
        if char in precedence:
            if char in {'*', '+', '?'}:
                output.append(char)
                last_token_type = 'unary'
                i += 1
                continue
            
            if char == '|':
                while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence[char]:
                    output.append(ops.pop())
                
                ops.append(char)
                last_token_type = '|'
                i += 1
                continue
        
        # Operandos
        if last_token_type in {'operand', 'unary', ')'}:
            # Insert concatenation operator
            while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence['.']:
                output.append(ops.pop())
            ops.append('.')
            last_token_type = '.'
        
        output.append(char)
        last_token_type = 'operand'
        i += 1
    
    while ops:
        if ops[-1] == '(':
            raise ValueError("Mismatched parentheses")
        output.append(ops.pop())
    
    return ''.join(output)


def validate_regex(regex):
    """Valida la expresión regular antes de ser procesada"""
    stack = []
    escape = False
    
    for i, char in enumerate(regex):
        if escape:
            escape = False
            continue
        
        if char == '\\':
            escape = True
            if i == len(regex) - 1:
                raise ValueError("Invalid escape at end of input")
            continue
        
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack[-1] != '(':
                raise ValueError("Mismatched parentheses")
            stack.pop()
    
    if escape:
        raise ValueError("Incomplete escape sequence")
    
    if stack:
        raise ValueError("Mismatched parentheses")
    
    for i in range(len(regex) - 1):
        curr = regex[i]
        next_char = regex[i+1]
        
        if curr in ('*', '+', '?') and next_char in ('*', '+', '?'):
            raise ValueError(f"Consecutive operators at position {i}")
        
        if curr == '|' and next_char == '|':
            raise ValueError(f"Empty alternative at position {i}")
    
    return True

def process_regex(filename):
    """Procesa la expresión regular"""
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if line:  
                    try:
                        validate_regex(line)
                        postfix = shunting_yard(line)
                        print(f"Original: {line}")
                        print(f"Postfix: {postfix}")
                    except ValueError as e:
                        print(f"Expresión regular inválida: {e}")
                        return None
                    print("="*30)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    

# Example usage
if __name__ == "__main__":
    filename = input("Nombre del archivo: ")
    process_regex(filename)