from textx import metamodel_from_file
from model.classes import (PropertyDef, NodeDef, CardinalityDef, EdgeDef,
    DataAmount, ClassPercentage, SharingSpec, GenerateSpec, GraphGenModel,
    IntType, FloatType, StringType, EnumType, BoolType, DateType
)
from interpreter.validator import validate_model, ValidationError
from interpreter.generat_data import generate_dataset_streaming

from export.mongo_exporter import export_to_files as mongo_export_to_files
from export.mongo_exporter import run_against_mongo
from export.neo4j_exporter import run_against_neo4j
from export.postgres_exporter import run_against_postgres
from export.neo4j_exporter import export_to_file as neo4j_export_to_file
from export.postgres_exporter import export_to_file as postgres_export_to_file
import time

EXPORTERS = {
    "MongoDB": {
        "to_file": lambda model, stream, output_path, add_index: mongo_export_to_files(
            model, stream, output_path
        ),
        "to_db": lambda model, stream, add_index: run_against_mongo(
            model, stream,
            uri="mongodb://localhost:27017",
            db_name="graphgen_test",  #ovo treba prilagoditi svojoj bazi
            add_index=add_index,
        ),
    },

    "Neo4J": {
        "to_file": lambda model, stream, output_path, add_index: neo4j_export_to_file(
            model, stream, output_path, add_index=add_index
        ),
        "to_db": lambda model, stream, add_index: run_against_neo4j(
            model, stream,
            uri="neo4j://127.0.0.1:7687",
            user="neo4j", #ovo treba prilagoditi svojoj bazi
            password="graphgen",
            add_index=add_index,
        ),
    },

    "PostgreSQL": {
        "to_file": lambda model, stream, output_path, add_index: postgres_export_to_file(
            model, stream, output_path, add_index=add_index
        ),
        "to_db": lambda model, stream, add_index: run_against_postgres(
            model, stream,
            dsn="dbname=graphgen user=postgres password=postgres host=localhost", #ovo treba prilagoditi svojoj bazi
            add_index=add_index,
        ),
    },
}


def measure_generation(model, seed=42, batch_size=10):
    node_counts = {}
    edge_counts = {}
    batch_log = []

    start = time.perf_counter()
    for kind, type_name, batch in generate_dataset_streaming(model, seed=seed, batch_size=batch_size):
        batch_log.append((kind, type_name, len(batch)))
        if kind == "node":
            node_counts[type_name] = node_counts.get(type_name, 0) + len(batch)
        else:
            edge_counts[type_name] = edge_counts.get(type_name, 0) + len(batch)
    duration = time.perf_counter() - start

    print(f"\n[Generating] Duration: {duration:.4f} sec")

    # print("\nUkupno po tipu (streaming):") #if you need uncomment this part
    # for t, c in node_counts.items():
    #     print(f"  Node {t}: {c}")
    # for t, c in edge_counts.items():
    #     print(f"  Edge {t}: {c}")

    return duration


def export_for_targets(model, targets, output_dir="output", seed=42,
                        batch_size=500, to_file=False, to_db=True):
    add_index = model.spec.add_index
    timings = {}
    for target in targets:
        exporter = EXPORTERS.get(target)
        if exporter is None:
            print(f"[WARNING] Unknown or unsupported target '{target}', skipping.")
            continue

        print(f"\n--- Export for target: {target} ---")
        timings[target] = {}

        if to_file:
            start = time.perf_counter()
            stream = generate_dataset_streaming(model, seed=seed, batch_size=batch_size)
            path = f"{output_dir}/{target.lower()}"
            print(f"  writing into files: {path}")
            exporter["to_file"](model, stream, path, add_index)
            timings[target]["to_file"] = time.perf_counter() - start
            print(f"  [time] to_file: {timings[target]['to_file']:.4f}s")

        if to_db:
            start = time.perf_counter()
            stream = generate_dataset_streaming(model, seed=seed, batch_size=batch_size)
            print(f"  Writing in database {target}...")
            exporter["to_db"](model, stream, add_index)
            timings[target]["to_db_total"] = time.perf_counter() - start
            print(f"  [time] generating + writing (to_db): {timings[target]['to_db_total']:.4f}s")

    return timings


def main():
    mm = metamodel_from_file(
        "grammar/graphGenBase.tx",
        classes=[
            GraphGenModel, NodeDef, PropertyDef,
            IntType, FloatType, StringType, EnumType, BoolType, DateType,
            EdgeDef, CardinalityDef, DataAmount, GenerateSpec,
            ClassPercentage, SharingSpec,
        ]
    )

    model = mm.model_from_file("examples/example1.gg")

    print("\nMODEL:")
    print(model)

    try:
        validate_model(model)
        print("Model is valid.\n")
    except ValidationError as e:
        print(e)
        raise SystemExit(1)

    print("=" * 50)
    print("TEST: only generating")
    print("=" * 50)
    measure_generation(model, seed=42, batch_size=10)

    print("\n" + "=" * 50)
    print("EXPORT: generating + writing, into targets")
    print("=" * 50)
    timings = export_for_targets(model, model.spec.targets)

    print("\n" + "=" * 50)
    print("Time:")
    print("=" * 50)
    for target, t in timings.items():
        for key, duration in t.items():
            print(f"  {target} [{key}]: {duration:.4f}s")


if __name__ == "__main__":
    main()