import json
import os
from typing import Dict, List, Any, Iterator, Tuple

from pymongo import MongoClient
"""
uri primer: "mongodb://localhost:27017"
Zahteva: pip install pymongo
"""
def build_node_documents(batch):
    return [dict(record) for record in batch]


def _edge_collection_name(edge):
    return f"{edge.source.name}_{edge.name}_{edge.target.name}"


def build_edge_documents(batch):
    documents = []
    for record in batch:
        doc = {
            "source_id": record["from"],
            "target_id": record["to"],
        }
        for k, v in record.items():
            if k not in ("from", "to"):
                doc[k] = v
        documents.append(doc)
    return documents

def build_index_specs(model):
    specs = []
    for edge in model.edges:
        collection = _edge_collection_name(edge)
        specs.append((collection, [("source_id", 1)]))
        specs.append((collection, [("target_id", 1)]))
    return specs

def export_to_files(
    model,
    dataset_stream,
    output_dir,
):
    os.makedirs(output_dir, exist_ok=True)

    edge_lookup = {e.name: e for e in model.edges}
    open_files: Dict[str, Any] = {}

    try:
        for kind, type_name, batch in dataset_stream:
            if kind == "node":
                collection_name = type_name
                documents = build_node_documents(batch)
            else:
                edge = edge_lookup[type_name]
                collection_name = _edge_collection_name(edge)
                documents = build_edge_documents(batch)

            if collection_name not in open_files:
                path = os.path.join(output_dir, f"{collection_name}.json")
                open_files[collection_name] = open(path, "w", encoding="utf-8")
                open_files[collection_name].write("[\n")
                open_files[collection_name]._first_write = True

            f = open_files[collection_name]
            for doc in documents:
                if not f._first_write:
                    f.write(",\n")
                f.write(json.dumps(doc, default=str))
                f._first_write = False

        for f in open_files.values():
            f.write("\n]")

    finally:
        for f in open_files.values():
            f.close()

    print(f"JSON files are saved in: {output_dir}/")

def run_against_mongo(
    model,
    dataset_stream,
    uri,
    db_name,
    add_index = False,
) -> None:

    edge_lookup = {e.name: e for e in model.edges}
    client = MongoClient(uri)
    db = client[db_name]

    try:
        if add_index:
            for collection_name, index_spec in build_index_specs(model):
                db[collection_name].create_index(index_spec)
            print(f"Created indexes for {len(model.edges) * 2} cases.")

        node_total = 0
        edge_total = 0

        for kind, type_name, batch in dataset_stream:
            if kind == "node":
                documents = build_node_documents(batch)
                if documents:
                    db[type_name].insert_many(documents)
                    node_total += len(documents)
            else:
                edge = edge_lookup[type_name]
                collection_name = _edge_collection_name(edge)
                documents = build_edge_documents(batch)
                if documents:
                    db[collection_name].insert_many(documents)
                    edge_total += len(documents)

        print(f"\nFinihed. Total: {node_total} nodes, {edge_total} edges.")
    finally:
        client.close()