import sys
import re
import os
import html

# Definición de tokens por lenguaje
class TokenTypes:
    # Tokens comunes
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    WHITESPACE = 'WHITESPACE'
    COMMENT = 'COMMENT'
    OPERATOR = 'OPERATOR'
    DELIMITER = 'DELIMITER'
    ERROR = 'ERROR'
    EOF = 'EOF'

    # Palabras reservadas por lenguaje
    PYTHON_KEYWORDS = {
        'def', 'class', 'if', 'else', 'elif', 'while', 'for', 'in', 'return',
        'True', 'False', 'None', 'and', 'or', 'not', 'import', 'from', 'as'
    }

    SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE',
        'DROP', 'TABLE', 'INTO', 'VALUES', 'JOIN', 'GROUP', 'BY', 'HAVING'
    }

    JS_KEYWORDS = {
        'function', 'var', 'let', 'const', 'if', 'else', 'while', 'for',
        'return', 'true', 'false', 'null', 'undefined', 'class', 'new'
    }

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

class LexicalAnalyzer:
    def __init__(self, language):
        self.language = language.lower()
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        
        # Patrones de tokens por lenguaje
        self.patterns = {
            'python': {
                'string': r'("[^"]*"|\'[^\']*\')',
                'number': r'\d*\.?\d+',
                'identifier': r'[a-zA-Z_]\w*',
                'operator': r'[+\-*/=<>!]=?|[%&|^~]',
                'delimiter': r'[\[\]{}(),;:]',
                'comment': r'#.*$|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
                'whitespace': r'\s+'
            },
            'sql': {
                'string': r'\'[^\']*\'',
                'number': r'\d+\.?\d*',
                'identifier': r'[a-zA-Z_]\w*',
                'operator': r'[+=<>!]=?|<>|[-*/]',
                'delimiter': r'[(),;.]',
                'comment': r'--.*$|/\*[\s\S]*?\*/',
                'whitespace': r'\s+'
            },
            'javascript': {
                'string': r'("[^"]*"|\'[^\']*\'|`[^`]*`)',
                'number': r'\d*\.?\d+',
                'identifier': r'[a-zA-Z_$]\w*',
                'operator': r'[+\-*/=<>!]=?|[%&|^~]|\+\+|--',
                'delimiter': r'[\[\]{}(),;:]',
                'comment': r'//.*$|/\*[\s\S]*?\*/',
                'whitespace': r'\s+'
            }
        }

    def tokenize(self, text):
        self.tokens = []
        position = 0
        
        while position < len(text):
            match = None
            token_type = None
            
            # Saltar espacios en blanco
            whitespace_match = re.match(self.patterns[self.language]['whitespace'], text[position:])
            if whitespace_match:
                position += len(whitespace_match.group(0))
                self.current_column += len(whitespace_match.group(0))
                continue
            
            # Buscar coincidencias con los patrones
            for pattern_name, pattern in self.patterns[self.language].items():
                regex = re.compile(pattern)
                match = regex.match(text[position:])
                
                if match:
                    value = match.group(0)
                    if pattern_name == 'identifier':
                        # Verificar si es una palabra reservada
                        upper_value = value.upper()
                        if self.language == 'python' and value in TokenTypes.PYTHON_KEYWORDS:
                            token_type = 'KEYWORD'
                        elif self.language == 'sql' and upper_value in TokenTypes.SQL_KEYWORDS:
                            token_type = 'KEYWORD'
                        elif self.language == 'javascript' and value in TokenTypes.JS_KEYWORDS:
                            token_type = 'KEYWORD'
                        else:
                            token_type = TokenTypes.IDENTIFIER
                    else:
                        token_type = pattern_name.upper()
                    
                    self.tokens.append(Token(token_type, value, self.current_line, self.current_column))
                    position += len(value)
                    
                    if '\n' in value:
                        newlines = value.count('\n')
                        self.current_line += newlines
                        self.current_column = len(value.split('\n')[-1]) + 1
                    else:
                        self.current_column += len(value)
                    break
            
            if not match:
                # Carácter no reconocido
                self.tokens.append(Token(TokenTypes.ERROR, text[position], self.current_line, self.current_column))
                position += 1
                self.current_column += 1

        self.tokens.append(Token(TokenTypes.EOF, '', self.current_line, self.current_column))
        return self.tokens

    def generate_html(self, output_file):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: monospace; background-color: #f5f5f5; }
        pre { background-color: white; padding: 20px; border-radius: 5px; }
        .keyword { color: #0000ff; font-weight: bold; }
        .string { color: #008000; }
        .number { color: #ff4500; }
        .operator { color: #a52a2a; }
        .delimiter { color: #666666; }
        .identifier { color: #000000; }
        .comment { color: #808080; font-style: italic; }
        .error { color: #ff0000; text-decoration: underline wavy; }
    </style>
</head>
<body>
    <pre>"""

        for token in self.tokens:
            if token.type == TokenTypes.EOF:
                continue
                
            css_class = token.type.lower()
            escaped_value = html.escape(token.value)
            html_content += f'<span class="{css_class}">{escaped_value}</span>'

        html_content += """
    </pre>
</body>
</html>"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

def process_file(input_file, language):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analyzer = LexicalAnalyzer(language)
    tokens = analyzer.tokenize(content)
    
    output_file = f"{os.path.splitext(input_file)[0]}_highlighted.html"
    analyzer.generate_html(output_file)
    
    return tokens

# Archivos de prueba
test_files = {
    'python': """
def calculate_sum(a, b):
    # This is a comment
    return a + b  # Return the sum

result = calculate_sum(10, 20.5)
print(f"The sum is: {result}")
""",
    'sql': """
-- Select all users
SELECT user_id, username
FROM users
WHERE age >= 18
    AND status = 'active'
ORDER BY username;
""",
    'javascript': """
function calculateProduct(a, b) {
    // This is a comment
    let result = a * b;
    return result;
}

const numbers = [1, 2, 3];
numbers.forEach(num => console.log(num));
"""
}

def main():
    # Crear archivos de prueba
    for lang, content in test_files.items():
        test_file = f"test_{lang}.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nProcessing {lang.upper()} file:")
        tokens = process_file(test_file, lang)
        
        print(f"\nTokens encontrados en {test_file}:")
        for token in tokens:
            if token.type != TokenTypes.WHITESPACE and token.type != TokenTypes.EOF:
                print(f"Línea {token.line}, Columna {token.column}: {token.type} = '{token.value}'")

if __name__ == "__main__":
    main()