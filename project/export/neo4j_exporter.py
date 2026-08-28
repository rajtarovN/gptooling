
from typing import Dict, List, Any, Iterator, Tuple
from neo4j import GraphDatabase
#Zahteva: pip install neo4j

def build_node_query(label, batch):

    query = (
        f"UNWIND $rows AS row "
        f"CREATE (n:{label}) "
        f"SET n = row"
    )
    rows = [_rename_id_field(r) for r in batch]
    return query, {"rows": rows}


def build_edge_query(edge_name, source_label, target_label, batch):
    query = (
        f"UNWIND $rows AS row "
        f"MATCH (a:{source_label} {{gen_id: row.from_id}}), "
        f"(b:{target_label} {{gen_id: row.to_id}}) "
        f"CREATE (a)-[r:{edge_name}]->(b) "
        f"SET r = row.props"
    )
    rows = [_edge_row_to_params(r) for r in batch]
    return query, {"rows": rows}


def _rename_id_field(record):
    new_record = dict(record)
    new_record["gen_id"] = new_record.pop("_id")
    return new_record


def _edge_row_to_params(record):
    props = {k: v for k, v in record.items() if k not in ("from", "to")}
    return {"from_id": record["from"], "to_id": record["to"], "props": props}

def build_index_queries(model):
    queries = []
    for node in model.nodes:
        queries.append(
            f"CREATE INDEX {node.name.lower()}_gen_id IF NOT EXISTS "
            f"FOR (n:{node.name}) ON (n.gen_id)"
        )
    return queries

def export_to_file(model, dataset_stream, output_path):
    add_index =True
    edge_lookup = {e.name: e for e in model.edges}

    with open(output_path, "w", encoding="utf-8") as f:
        if add_index:
            f.write("// ---- INDEX ----\n")
            for q in build_index_queries(model):
                f.write(q + ";\n")
            f.write("\n")

        f.write("// ---- NODES ----\n")
        for kind, type_name, batch in dataset_stream:
            if kind == "node":
                query, params = build_node_query(type_name, batch)
                f.write(f"// batch with{len(batch)} - {type_name}\n")
                f.write(f":params {params!r}\n")
                f.write(query + ";\n\n")
            else:
                edge = edge_lookup[type_name]
                query, params = build_edge_query(
                    type_name, edge.source.name, edge.target.name, batch
                )
                f.write(f"// batch with {len(batch)} - {type_name}\n")
                f.write(f":params {params!r}\n")
                f.write(query + ";\n\n")

    print(f"Queries are saved into: {output_path}")

def run_against_neo4j(model, dataset_stream, uri, user, password):
    add_index = True
    edge_lookup = {e.name: e for e in model.edges}
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            if add_index:
                for q in build_index_queries(model):
                    session.run(q)
                print(f"Created {len(model.nodes)} indexes.")

            node_total = 0
            edge_total = 0

            for kind, type_name, batch in dataset_stream:
                if kind == "node":
                    query, params = build_node_query(type_name, batch)
                    session.run(query, **params)
                    node_total += len(batch)
                else:
                    edge = edge_lookup[type_name]
                    query, params = build_edge_query(
                        type_name, edge.source.name, edge.target.name, batch
                    )
                    session.run(query, **params)
                    edge_total += len(batch)

        print(f"\nFinished. Total: {node_total} nodes, {edge_total} edges.")
    finally:
        driver.close()