import re
import os
import time

class TokenTypes:
    # Categorías léxicas comunes entre los tres lenguajes
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    OPERATOR = 'OPERATOR'
    LITERAL = 'LITERAL'  # números y strings
    COMMENT = 'COMMENT'
    DELIMITER = 'DELIMITER'

class LexicalAnalyzer:
    def __init__(self):
        # Expresiones regulares para las categorías léxicas
        self.patterns = {
            'python': {
                'keyword': r'\b(def|class|if|else|while|for|return|import|from|as)\b',
                'identifier': r'[a-zA-Z_]\w*',
                'operator': r'[+\-*/=<>]|==|!=|<=|>=',
                'literal': r'\d+(\.\d+)?|"[^"]*"|\'[^\']*\'',
                'comment': r'#.*$',
                'delimiter': r'[():,\[\]{}]'
            },
            'sql': {
                'keyword': r'\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|DROP)\b',
                'identifier': r'[a-zA-Z_]\w*',
                'operator': r'=|<>|<|>|<=|>=',
                'literal': r'\d+|\'\w+\'',
                'comment': r'--.*$',
                'delimiter': r'[,;()]'
            },
            'javascript': {
                'keyword': r'\b(function|var|let|if|else|while|for|return)\b',
                'identifier': r'[a-zA-Z_$]\w*',
                'operator': r'[+\-*/=<>]|==|===|!=|!==|<=|>=',
                'literal': r'\d+(\.\d+)?|"[^"]*"|\'[^\']*\'',
                'comment': r'//.*$',
                'delimiter': r'[();,{}]'
            }
        }
    
    def tokenize(self, text, language):
        tokens = []
        lines = text.split('\n')
        
        start_time = time.time()
        
        for line_num, line in enumerate(lines, 1):
            position = 0
            while position < len(line):
                match = None
                
                # Ignorar espacios en blanco
                if line[position].isspace():
                    position += 1
                    continue
                
                # Buscar coincidencias con los patrones
                for token_type, pattern in self.patterns[language].items():
                    regex = re.compile(pattern)
                    match = regex.match(line[position:])
                    if match:
                        value = match.group(0)
                        tokens.append((token_type.upper(), value, line_num))
                        position += len(value)
                        break
                
                if not match:
                    position += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return tokens, processing_time

    def generate_html(self, filename, tokens, language, processing_time):
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis Léxico - {filename}</title>
    <style>
        body {{ 
            font-family: 'Arial', sans-serif; 
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .keyword {{ color: #0000ff; font-weight: bold; }}
        .identifier {{ color: #000000; }}
        .operator {{ color: #a52a2a; }}
        .literal {{ color: #008000; }}
        .comment {{ color: #808080; font-style: italic; }}
        .delimiter {{ color: #666666; }}
        .stats {{ 
            margin-top: 20px; 
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border: 1px solid #dee2e6;
        }}
        .code {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            overflow-x: auto;
            margin: 20px 0;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        h2, h3 {{
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Análisis Léxico del archivo: {filename}</h2>
        <h3>Lenguaje: {language.upper()}</h3>
        <div class="code">"""

        current_line = 1
        for token_type, value, line in tokens:
            if line > current_line:
                html += '<br>' * (line - current_line)
                current_line = line
            css_class = token_type.lower()
            html += f'<span class="{css_class}">{value}</span> '
        
        token_count = len(tokens)
        html += f"""
        </div>
        <div class="stats">
            <h3>Estadísticas:</h3>
            <p>Tokens encontrados: {token_count}</p>
            <p>Tiempo de procesamiento: {processing_time:.4f} segundos</p>
            <p>Complejidad del algoritmo: O(n), donde n es el número de caracteres</p>
        </div>
    </div>
</body>
</html>
"""
        return html

def process_file(input_file, input_dir='codigos', output_dir='resultados'):
    # Determinar el lenguaje por la extensión del archivo
    ext = input_file.split('.')[-1].lower()
    language_map = {'py': 'python', 'sql': 'sql', 'js': 'javascript'}
    language = language_map.get(ext)
    
    if not language:
        print(f"Extensión no soportada: {ext}")
        return
    
    try:
        # Leer el archivo con codificación UTF-8
        input_path = os.path.join(input_dir, input_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analyzer = LexicalAnalyzer()
        tokens, processing_time = analyzer.tokenize(content, language)
        
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{os.path.splitext(input_file)[0]}_{language}_resultado.html")
        html_content = analyzer.generate_html(input_file, tokens, language, processing_time)
        
        # Escribir el archivo HTML con codificación UTF-8
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Archivo procesado: {input_file}")
        print(f"Resultado guardado en: {output_file}")
        print(f"Tiempo de procesamiento: {processing_time:.4f} segundos")
        print(f"Tokens encontrados: {len(tokens)}")
        
    except Exception as e:
        print(f"Error procesando {input_file}: {str(e)}")

def main():
    # Verificar que existe el directorio codigos
    if not os.path.exists('codigos'):
        print("Error: No se encontró la carpeta 'codigos'")
        return
    
    # Procesar todos los archivos en la carpeta codigos
    files = [f for f in os.listdir('codigos') if f.endswith(('.py', '.sql', '.js'))]
    
    if not files:
        print("No se encontraron archivos para procesar en la carpeta 'codigos'")
        return
    
    print(f"Encontrados {len(files)} archivos para procesar")
    for file in files:
        print(f"\nProcesando {file}...")
        process_file(file)

if __name__ == "__main__":
    main()