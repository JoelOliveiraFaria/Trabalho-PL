from lexer import CQLLexer
from parser import CQLParser
from executor import CommandExecutor, TableManager
import sys

class CQLInterpreter:
    def __init__(self):
        self.lexer = CQLLexer()
        self.parser = CQLParser(lexer=self.lexer)
        self.table_manager = TableManager()
        self.executor = CommandExecutor(self.table_manager)
        self.buffer = ""

    def run_file(self, filename):
        if not filename.endswith('.fca'):
            print(f"Erro: O arquivo '{filename}' deve ter a extensão .fca")
            sys.exit(1)
        try:
            with open(filename, 'r') as file:
                content = file.read()
                print(f"Executando comandos do arquivo: {filename}")
                result = self.parser.parse(content)
                if result:
                    for stmt in result:
                        if stmt:
                            self.executor.execute_statement(stmt)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {filename}")
        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")

    def run_interactive(self):
        print("CQL Interpreter - Digite 'exit;' para sair")
        while True:
            try:
                line = input("CQL> " if not self.buffer else "... ")
                if line.lower() == "exit;":
                    break
                self.buffer += line + " "
                if ";" in line:
                    result = self.parser.parse(self.buffer)
                    if result:
                        for stmt in result:
                            if stmt:
                                self.executor.execute_statement(stmt)
                    self.buffer = ""
            except KeyboardInterrupt:
                print("\nSaindo...")
                break
            except Exception as e:
                print(f"Erro: {e}")
                self.buffer = ""

def main():
    interpreter = CQLInterpreter()
    if len(sys.argv) > 1:
        interpreter.run_file(sys.argv[1])
    else:
        interpreter.run_interactive()

if __name__ == "__main__":
    main()