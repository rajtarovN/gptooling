from typing import Dict, List, Any, Iterator, Tuple

from model.classes import IntType, FloatType, StringType, EnumType, BoolType, DateType
import psycopg2
from psycopg2.extras import execute_batch

def _sql_type(prop_type):
    if isinstance(prop_type, IntType):
        return "INTEGER"
    if isinstance(prop_type, FloatType):
        return "DOUBLE PRECISION"
    if isinstance(prop_type, StringType) or isinstance(prop_type, EnumType):
        return "VARCHAR(255)"
    if isinstance(prop_type, BoolType):
        return "BOOLEAN"
    if isinstance(prop_type, DateType):
        return "TIMESTAMP"
    raise ValueError(f"Unknown property type: {prop_type}")

def build_schema_ddl(model):
    statements = []

    for node in model.nodes:
        columns = ["gen_id VARCHAR(255) PRIMARY KEY"]
        for prop in node.properties:
            columns.append(f"{prop.name} {_sql_type(prop.type)}")
        ddl = f"CREATE TABLE IF NOT EXISTS \"{node.name}\" (\n    " + ",\n    ".join(columns) + "\n)"
        statements.append(ddl)

    for edge in model.edges:
        columns = [
            "source_id VARCHAR(255) NOT NULL",
            "target_id VARCHAR(255) NOT NULL",
        ]
        for prop in edge.properties:
            columns.append(f"{prop.name} {_sql_type(prop.type)}")
        columns.append(f'FOREIGN KEY (source_id) REFERENCES "{edge.source.name}"(gen_id)')
        columns.append(f'FOREIGN KEY (target_id) REFERENCES "{edge.target.name}"(gen_id)')

        table_name = f"{edge.source.name}_{edge.name}_{edge.target.name}"
        ddl = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" (\n    " + ",\n    ".join(columns) + "\n)"
        statements.append(ddl)

    return statements


def _junction_table_name(edge):
    return f"{edge.source.name}_{edge.name}_{edge.target.name}"


def build_node_insert(node_name, batch):
    if not batch:
        return None, []

    columns = ["gen_id"] + [k for k in batch[0].keys() if k != "_id"]
    placeholders = ", ".join(["%s"] * len(columns))
    query = f'INSERT INTO "{node_name}" ({", ".join(columns)}) VALUES ({placeholders})'

    values = []
    for record in batch:
        row = [record["_id"]] + [record[k] for k in columns[1:]]
        values.append(tuple(row))

    return query, values


def build_edge_insert(edge, batch):
    if not batch:
        return None, []

    table_name = _junction_table_name(edge)
    prop_names = [k for k in batch[0].keys() if k not in ("from", "to")]
    columns = ["source_id", "target_id"] + prop_names
    placeholders = ", ".join(["%s"] * len(columns))
    query = f'INSERT INTO "{table_name}" ({", ".join(columns)}) VALUES ({placeholders})'

    values = []
    for record in batch:
        row = [record["from"], record["to"]] + [record[p] for p in prop_names]
        values.append(tuple(row))

    return query, values

def build_index_queries(model):
    queries = []
    for edge in model.edges:
        table_name = _junction_table_name(edge)
        queries.append(
            f'CREATE INDEX IF NOT EXISTS idx_{table_name}_source '
            f'ON "{table_name}" (source_id)'
        )
        queries.append(
            f'CREATE INDEX IF NOT EXISTS idx_{table_name}_target '
            f'ON "{table_name}" (target_id)'
        )
    return queries

def export_to_file(model, dataset_stream, output_path, add_index = False):
    edge_lookup = {e.name: e for e in model.edges}

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("-- ==== SCHEMA ====\n")
        for ddl in build_schema_ddl(model):
            f.write(ddl + ";\n\n")

        if add_index:
            f.write("-- ==== INDEX ====\n")
            for q in build_index_queries(model):
                f.write(q + ";\n")
            f.write("\n")

        f.write("-- ==== DATA ====\n")
        for kind, type_name, batch in dataset_stream:
            if kind == "node":
                query, values = build_node_insert(type_name, batch)
            else:
                edge = edge_lookup[type_name]
                query, values = build_edge_insert(edge, batch)

            if query is None:
                continue

            f.write(f"-- batch with {len(values)} - {type_name}\n")
            for row in values:
                formatted = query.replace("%s", "{}").format(
                    *[_sql_literal(v) for v in row]
                )
                f.write(formatted + ";\n")
            f.write("\n")

    print(f"SQL saved at: {output_path}")


def _sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"

def run_against_postgres(model, dataset_stream, dsn, add_index= False):
    edge_lookup = {e.name: e for e in model.edges}
    conn = psycopg2.connect(dsn)

    try:
        with conn.cursor() as cur:
            for ddl in build_schema_ddl(model):
                cur.execute(ddl)
            conn.commit()
            print(f"Created {len(model.nodes) + len(model.edges)} tables.")

            if add_index:
                for q in build_index_queries(model):
                    cur.execute(q)
                conn.commit()

            node_total = 0
            edge_total = 0

            for kind, type_name, batch in dataset_stream:
                if kind == "node":
                    query, values = build_node_insert(type_name, batch)
                    if query:
                        execute_batch(cur, query, values)
                        conn.commit()
                        node_total += len(values)
                else:
                    edge = edge_lookup[type_name]
                    query, values = build_edge_insert(edge, batch)
                    if query:
                        execute_batch(cur, query, values)
                        conn.commit()
                        edge_total += len(values)

        print(f"\nFinished. Total: {node_total} nodes, {edge_total} edges.")
    finally:
        conn.close()