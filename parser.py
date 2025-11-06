import ply.yacc as yacc
from lexer import CQLLexer

class CQLParser:
    def __init__(self, lexer=None):
        # Usar o lexer fornecido ou criar um novo
        self.lexer = lexer if lexer else CQLLexer()
        self.tokens = self.lexer.get_tokens()
        self.parser = None
        self.precedence = (
            ('left', 'AND'),     # Avalia da esquerda para a direita
            ('nonassoc', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE'),  # >, <, >=, <=, =, !=
        )
        self.build()

    def build(self, **kwargs):
        #Constrói o parser com as regras definidas.
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, text, **kwargs):
        #Parseia a entrada e retorna a árvore de sintaxe.
        return self.parser.parse(text, lexer=self.lexer.get_lexer(), **kwargs)

    # Regras de gramática
    def p_program(self, p):
        '''program : statement_list'''
        p[0] = p[1]

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement'''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] is not None else []
        else:
            if p[2] is not None:
                p[0] = p[1] + [p[2]]
            else:
                p[0] = p[1]

    def p_statement(self, p):
        '''statement : import_statement SEMICOLON
                     | export_statement SEMICOLON
                     | discard_statement SEMICOLON
                     | rename_statement SEMICOLON
                     | print_statement SEMICOLON
                     | select_statement SEMICOLON
                     | create_statement SEMICOLON
                     | procedure_definition SEMICOLON
                     | call_statement SEMICOLON'''
        p[0] = p[1]

    def p_empty_statement(self, p):
        'statement : SEMICOLON'
        p[0] = None

    def p_import_statement(self, p):
        'import_statement : IMPORT TABLE ID FROM STRING'
        p[0] = ('import_table', p[3], p[5])

    def p_export_statement(self, p):
        'export_statement : EXPORT TABLE ID AS STRING'
        p[0] = ('export_table', p[3], p[5])

    def p_discard_statement(self, p):
        'discard_statement : DISCARD TABLE ID'
        p[0] = ('discard_table', p[3])

    def p_rename_statement(self, p):
        'rename_statement : RENAME TABLE ID ID'
        p[0] = ('rename_table', p[3], p[4])

    def p_print_statement(self, p):
        'print_statement : PRINT TABLE ID'
        p[0] = ('print_table', p[3])

    def p_select_statement(self, p):
        '''select_statement : SELECT column_list FROM ID
                            | SELECT column_list FROM ID WHERE condition
                            | SELECT column_list FROM ID LIMIT NUMBER
                            | SELECT column_list FROM ID WHERE condition LIMIT NUMBER'''
        if len(p) == 5:
            p[0] = ('select', p[2], p[4], None, None)
        elif len(p) == 7:
            if p[5].lower() == 'where':
                p[0] = ('select', p[2], p[4], p[6], None)
            else:
                p[0] = ('select', p[2], p[4], None, p[6])
        elif len(p) == 9:
            p[0] = ('select', p[2], p[4], p[6], p[8])

    def p_column_list(self, p):
        '''column_list : ASTERISK
                       | column_id_list'''
        p[0] = p[1]

    def p_column_id_list(self, p):
        '''column_id_list : ID
                          | column_id_list COMMA ID'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_condition(self, p):
        '''condition : ID comparison_op expression
                     | condition AND condition'''
        if len(p) == 4 and p[2].lower() != 'and':
            p[0] = ('cond', p[1], p[2], p[3])
        else:
            p[0] = ('and', p[1], p[3])

    def p_comparison_op(self, p):
        '''comparison_op : GT
                         | LT
                         | GE
                         | LE
                         | EQ
                         | NE'''
        p[0] = p[1]

    def p_expression(self, p):
        '''expression : ID
                      | NUMBER
                      | STRING'''
        p[0] = p[1]

    def p_create_statement(self, p):
        '''create_statement : CREATE TABLE ID select_statement
                            | CREATE TABLE ID FROM ID JOIN ID USING LPAREN ID RPAREN'''
        if len(p) == 5:
            p[0] = ('create_select', p[3], p[4])
        else:
            p[0] = ('create_join', p[3], p[5], p[7], p[10])

    def p_procedure_definition(self, p):
        'procedure_definition : PROCEDURE ID DO proc_statement_list END'
        p[0] = ('procedure_def', p[2], p[4])

    def p_proc_statement_list(self, p):
        '''proc_statement_list : proc_statement
                               | proc_statement_list proc_statement'''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] is not None else []
        else:
            if p[2] is not None:
                p[0] = p[1] + [p[2]]
            else:
                p[0] = p[1]

    def p_proc_statement(self, p):
        '''proc_statement : import_statement SEMICOLON
                          | export_statement SEMICOLON
                          | discard_statement SEMICOLON
                          | rename_statement SEMICOLON
                          | print_statement SEMICOLON
                          | select_statement SEMICOLON
                          | create_statement SEMICOLON
                          | call_statement SEMICOLON
                          | SEMICOLON'''
        if len(p) > 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_call_statement(self, p):
        'call_statement : CALL ID'
        p[0] = ('call_procedure', p[2])

    def p_error(self, p):
        if p:
            print(f"Erro de sintaxe no token: {p.value} (tipo: {p.type})")
        else:
            print("Erro de sintaxe no final da entrada")