import ply.lex as lex

class CQLLexer:
    def __init__(self):
        # Lista de tokens
        self.tokens = [
            'ID',           # Identificadores
            'STRING',       # Strings entre aspas
            'NUMBER',       # Números
            'SEMICOLON',    # ;
            'COMMA',        # ,
            'LPAREN',       # (
            'RPAREN',       # )
            'ASTERISK',     # *
            'GT',           # >
            'LT',           # <
            'GE',           # >=
            'LE',           # <=
            'EQ',           # =
            'NE',           # <>
        ]

        # Palavras reservadas
        self.reserved = {
            'import': 'IMPORT',
            'export': 'EXPORT',
            'table': 'TABLE',
            'from': 'FROM',
            'as': 'AS',
            'select': 'SELECT',
            'where': 'WHERE',
            'create': 'CREATE',
            'discard': 'DISCARD',
            'rename': 'RENAME',
            'print': 'PRINT',
            'join': 'JOIN',
            'using': 'USING',
            'limit': 'LIMIT',
            'and': 'AND',
            'procedure': 'PROCEDURE',
            'do': 'DO',
            'end': 'END',
            'call': 'CALL'
        }

        # Adicionar palavras reservadas aos tokens
        self.tokens += list(self.reserved.values())

        # Inicializar o lexer
        self.lexer = None
        self.build()

    def build(self, **kwargs):
        #Constrói o lexer com as regras definidas.
        self.lexer = lex.lex(module=self, **kwargs)

    # Regras para tokens
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ASTERISK = r'\*'
    t_GT = r'>'
    t_LT = r'<'
    t_GE = r'>='
    t_LE = r'<='
    t_EQ = r'='
    t_NE = r'<>'

    # Ignorar espaços e tabs
    t_ignore = ' \t\r'

    def t_STRING(self, t):
        r'"([^\\"]|\\.)*"'
        t.value = t.value[1:-1]  # Remove as aspas
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value.lower(), 'ID')
        return t

    def t_NUMBER(self, t):
        r'-?\d+\.\d+|-?\d+'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    def t_COMMENT(self, t):
        r'--.*|{-[\s\S]*?-}'
        pass  # Skip comentários

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)  # Conta o número de linhas

    def t_error(self, t):
        print(f"Caráter inválido: {t.value[0]}")
        t.lexer.skip(1)

    def input(self, text):
        #Define a entrada para o lexer.
        self.lexer.input(text)

    def token(self):
        #Retorna o próximo token da entrada.
        return self.lexer.token()

    def get_tokens(self):
        #Retorna a lista de tokens.
        return self.tokens

    def get_lexer(self):
        #Retorna a instância do lexer.
        return self.lexer