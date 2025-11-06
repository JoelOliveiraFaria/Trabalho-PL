import pandas as pd

class TableManager:
    """Gerencia tabelas e procedimentos em memória."""
    def __init__(self):
        self.tables = {}
        self.procedures = {}

    def add_table(self, name, df):
        """Adiciona uma tabela ao gerenciador."""
        if name in self.tables:
            print(f"Erro: Tabela '{name}' já existe")
            return False
        self.tables[name] = df
        print(f"Tabela '{name}' adicionada")
        return True

    def get_table(self, name):
        """Obtém uma tabela pelo nome."""
        if name not in self.tables:
            print(f"Tabela '{name}' não encontrada")
            return None
        return self.tables[name]

    def remove_table(self, name):
        """Remove uma tabela do gerenciador."""
        if name in self.tables:
            del self.tables[name]
            print(f"Tabela '{name}' removida")
            return True
        print(f"Tabela '{name}' não encontrada")
        return False

    def rename_table(self, old_name, new_name):
        """Renomeia uma tabela."""
        if old_name in self.tables:
            self.tables[new_name] = self.tables[old_name]
            del self.tables[old_name]
            print(f"Tabela '{old_name}' renomeada para '{new_name}'")
            return True
        print(f"Tabela '{old_name}' não encontrada")
        return False

    def add_procedure(self, name, statements):
        """Adiciona um procedimento ao gerenciador."""
        self.procedures[name] = statements
        print(f"Procedimento '{name}' definido")
        return True

    def get_procedure(self, name):
        """Obtém um procedimento pelo nome."""
        if name not in self.procedures:
            print(f"Procedimento '{name}' não encontrado")
            return None
        return self.procedures[name]

class Command:
    """Classe base para comandos."""
    def execute(self, table_manager):
        raise NotImplementedError("Subclasses devem implementar o método execute")

class ImportCommand(Command):
    """Comando para importar uma tabela de um arquivo CSV."""
    def __init__(self, table_name, filename):
        self.table_name = table_name
        self.filename = filename

    def execute(self, table_manager):
        try:
            filename = self.filename.strip('"\'')
            try:
                df = pd.read_csv(filename, comment='#', quotechar='"')
            except Exception as e:
                print(f"Aviso: Leitura padrão falhou, usando parser personalizado: {e}")
                df = self.read_csv_custom(filename)
            return table_manager.add_table(self.table_name, df)
        except Exception as e:
            print(f"Erro ao importar tabela: {e}")
            return None

    def read_csv_custom(self, filename):
        """Função personalizada para ler CSV com suporte a comentários e aspas."""
        rows = []
        header = None
        with open(filename, 'r') as file:
            for line in file:
                if line.strip().startswith('#'):
                    continue
                columns = []
                in_quotes = False
                current_value = ""
                for char in line:
                    if char == '"' and not in_quotes:
                        in_quotes = True
                    elif char == '"' and in_quotes:
                        in_quotes = False
                    elif char == ',' and not in_quotes:
                        columns.append(current_value)
                        current_value = ""
                    else:
                        current_value += char
                if current_value.endswith('\n'):
                    current_value = current_value[:-1]
                columns.append(current_value)
                if header is None:
                    header = columns
                else:
                    for i, val in enumerate(columns):
                        try:
                            if '.' in val:
                                columns[i] = float(val)
                            else:
                                columns[i] = int(val)
                        except ValueError:
                            pass
                    rows.append(columns)
        return pd.DataFrame(rows, columns=header)

class ExportCommand(Command):
    """Comando para exportar uma tabela para um arquivo CSV."""
    def __init__(self, table_name, filename):
        self.table_name = table_name
        self.filename = filename

    def execute(self, table_manager):
        df = table_manager.get_table(self.table_name)
        if df is None:
            return None
        try:
            filename = self.filename.strip('"\'')
            df.to_csv(filename, index=False, quoting=1)
            print(f"Tabela '{self.table_name}' exportada para '{filename}'")
            return True
        except Exception as e:
            print(f"Erro ao exportar tabela: {e}")
            return None

class DiscardCommand(Command):
    """Comando para remover uma tabela."""
    def __init__(self, table_name):
        self.table_name = table_name

    def execute(self, table_manager):
        return table_manager.remove_table(self.table_name)

class RenameCommand(Command):
    """Comando para renomear uma tabela."""
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def execute(self, table_manager):
        return table_manager.rename_table(self.old_name, self.new_name)

class PrintCommand(Command):
    """Comando para imprimir uma tabela."""
    def __init__(self, table_name):
        self.table_name = table_name

    def execute(self, table_manager):
        df = table_manager.get_table(self.table_name)
        if df is not None:
            print(f"\nTabela: {self.table_name}")
            print(df)
        return df

class SelectCommand(Command):
    """Comando para selecionar dados de uma tabela."""
    def __init__(self, columns, table_name, condition, limit):
        self.columns = columns
        self.table_name = table_name
        self.condition = condition
        self.limit = limit

    def execute(self, table_manager):
        df = table_manager.get_table(self.table_name)
        if df is None:
            return None
        df = df.copy()
        if self.condition:
            filtered_rows = []
            for _, row in df.iterrows():
                if self.evaluate_condition(row, self.condition):
                    filtered_rows.append(row)
            if filtered_rows:
                df = pd.DataFrame(filtered_rows)
            else:
                df = pd.DataFrame(columns=df.columns)
        if self.columns != '*':
            valid_columns = [col for col in self.columns if col in df.columns]
            if valid_columns:
                df = df[valid_columns]
            else:
                print("Aviso: Nenhuma coluna válida especificada")
                return pd.DataFrame()
        if self.limit is not None:
            df = df.head(int(self.limit))
        print("\nResultado da consulta:")
        print(df)
        return df

    def evaluate_condition(self, row, condition):
        if condition[0] == 'cond':
            column, op, value = condition[1], condition[2], condition[3]
            if column not in row:
                print(f"Aviso: Coluna '{column}' não encontrada")
                return False
            cell_value = row[column]
            if op == '>':
                return cell_value > value
            elif op == '<':
                return cell_value < value
            elif op == '>=':
                return cell_value >= value
            elif op == '<=':
                return cell_value <= value
            elif op == '=':
                return cell_value == value
            elif op == '<>':
                return cell_value != value
        elif condition[0] == 'and':
            return self.evaluate_condition(row, condition[1]) and self.evaluate_condition(row, condition[2])
        return False

class CreateSelectCommand(Command):
    """Comando para criar uma tabela a partir de um SELECT."""
    def __init__(self, new_table, select_stmt):
        self.new_table = new_table
        self.select_stmt = select_stmt

    def execute(self, table_manager):
        executor = CommandExecutor(table_manager)
        result_df = executor.execute_statement(self.select_stmt)
        if result_df is not None and not result_df.empty:
            table_manager.add_table(self.new_table, result_df)
            print(f"Tabela '{self.new_table}' criada com sucesso")
            return True
        print(f"Não foi possível criar a tabela '{self.new_table}'")
        return False

class CreateJoinCommand(Command):
    """Comando para criar uma tabela a partir de um JOIN."""
    def __init__(self, new_table, table1, table2, join_column):
        self.new_table = new_table
        self.table1 = table1
        self.table2 = table2
        self.join_column = join_column

    def execute(self, table_manager):
        df1 = table_manager.get_table(self.table1)
        df2 = table_manager.get_table(self.table2)
        if df1 is None or df2 is None:
            return False
        if self.join_column not in df1.columns:
            print(f"Coluna '{self.join_column}' não encontrada em '{self.table1}'")
            return False
        if self.join_column not in df2.columns:
            print(f"Coluna '{self.join_column}' não encontrada em '{self.table2}'")
            return False
        try:
            joined_df = pd.merge(df1, df2, on=self.join_column)
            table_manager.add_table(self.new_table, joined_df)
            print(f"Tabela '{self.new_table}' criada da junção de '{self.table1}' e '{self.table2}'")
            return True
        except Exception as e:
            print(f"Erro ao criar tabela da junção: {e}")
            return False

class ProcedureDefCommand(Command):
    """Comando para definir um procedimento."""
    def __init__(self, proc_name, statements):
        self.proc_name = proc_name
        self.statements = statements

    def execute(self, table_manager):
        return table_manager.add_procedure(self.proc_name, self.statements)

class CallProcedureCommand(Command):
    """Comando para chamar um procedimento."""
    def __init__(self, proc_name):
        self.proc_name = proc_name

    def execute(self, table_manager):
        statements = table_manager.get_procedure(self.proc_name)
        if statements is None:
            return False
        print(f"Executando procedimento '{self.proc_name}'...")
        executor = CommandExecutor(table_manager)
        for stmt in statements:
            executor.execute_statement(stmt)
        print(f"Procedimento '{self.proc_name}' executado com sucesso")
        return True

class CommandExecutor:
    """Executa comandos CQL."""
    def __init__(self, table_manager):
        self.table_manager = table_manager

    def execute_statement(self, statement):
        """Executa um comando representado por uma estrutura de dados."""
        if not statement:
            return None
        cmd_type = statement[0]
        if cmd_type == 'import_table':
            cmd = ImportCommand(statement[1], statement[2])
        elif cmd_type == 'export_table':
            cmd = ExportCommand(statement[1], statement[2])
        elif cmd_type == 'discard_table':
            cmd = DiscardCommand(statement[1])
        elif cmd_type == 'rename_table':
            cmd = RenameCommand(statement[1], statement[2])
        elif cmd_type == 'print_table':
            cmd = PrintCommand(statement[1])
        elif cmd_type == 'select':
            cmd = SelectCommand(statement[1], statement[2], statement[3], statement[4])
        elif cmd_type == 'create_select':
            cmd = CreateSelectCommand(statement[1], statement[2])
        elif cmd_type == 'create_join':
            cmd = CreateJoinCommand(statement[1], statement[2], statement[3], statement[4])
        elif cmd_type == 'procedure_def':
            cmd = ProcedureDefCommand(statement[1], statement[2])
        elif cmd_type == 'call_procedure':
            cmd = CallProcedureCommand(statement[1])
        else:
            print(f"Comando desconhecido: {cmd_type}")
            return None
        return cmd.execute(self.table_manager)