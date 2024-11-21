import re
import os
import time
from concurrent.futures import ThreadPoolExecutor

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

        html += f"""
        </div>
        <div class="stats">
            <h3>Estadísticas:</h3>
            <p>Tokens encontrados: {len(tokens)}</p>
            <p>Tiempo de procesamiento: {processing_time:.4f} segundos</p>
        </div>
    </div>
</body>
</html>
"""
        return html

def process_file(input_file, input_dir='codigos', output_dir='resultados'):
    ext = input_file.split('.')[-1].lower()
    language_map = {'py': 'python', 'sql': 'sql', 'js': 'javascript'}
    language = language_map.get(ext)
    
    if not language:
        print(f"Extensión no soportada: {ext}")
        return
    
    try:
        input_path = os.path.join(input_dir, input_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analyzer = LexicalAnalyzer()
        tokens, processing_time = analyzer.tokenize(content, language)
        
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{os.path.splitext(input_file)[0]}_{language}_resultado.html")
        html_content = analyzer.generate_html(input_file, tokens, language, processing_time)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return processing_time, len(tokens)
        
    except Exception as e:
        print(f"Error procesando {input_file}: {str(e)}")

def main():
    if not os.path.exists('codigos'):
        print("Error: No se encontró la carpeta 'codigos'")
        return
    
    files = [f for f in os.listdir('codigos') if f.endswith(('.py', '.sql', '.js'))]
    
    if not files:
        print("No se encontraron archivos para procesar en la carpeta 'codigos'")
        return
    
    sequential_times = []
    parallel_times = []
    
    # Secuencial
    start_sequential = time.time()
    for file in files:
        sequential_time, _ = process_file(file, output_dir='resultados_secuencial')
        sequential_times.append(sequential_time)
    end_sequential = time.time()
    
    # Paralelo
    start_parallel = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file, output_dir='resultados_paralelo') for file in files]
        parallel_times = [future.result()[0] for future in futures]
    end_parallel = time.time()
    
    print(f"\nTiempo total secuencial: {end_sequential - start_sequential:.4f} segundos")
    print(f"Tiempo total paralelo: {end_parallel - start_parallel:.4f} segundos")

if __name__ == "__main__":
    main()
