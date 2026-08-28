import random
import string
from typing import Dict, List, Any, Iterator, Optional, Tuple

from model.classes import GraphGenModel, NodeDef, EdgeDef
from model.classes import IntType, FloatType, StringType, EnumType, BoolType, DateType
#zahteva pip install exrex
def generate_value(prop_type, index, rng):

    if isinstance(prop_type, IntType):
        lo = prop_type.min if prop_type.min is not None else 0
        hi = prop_type.max if prop_type.max is not None else 1_000_000
        return rng.randint(lo, hi)

    if isinstance(prop_type, FloatType):
        lo = prop_type.min if prop_type.min is not None else 0.0
        hi = prop_type.max if prop_type.max is not None else 1.0
        return round(rng.uniform(lo, hi), 4)

    if isinstance(prop_type, StringType):
        pattern = prop_type.pattern
        if pattern is None:
            return _random_string(rng, length=8)
        return _generate_from_pattern(pattern, index)

    if isinstance(prop_type, EnumType):
        return rng.choice(prop_type.values)

    if isinstance(prop_type, BoolType):
        return rng.choice([True, False])

    if isinstance(prop_type, DateType):
        return _random_datetime(rng)

    raise ValueError(f"Unknown property type: {prop_type}")


def _generate_from_pattern(pattern, index):
    if '{id}' in pattern:
        return pattern.replace('{id}', str(index))

    try:
        import exrex
        return exrex.getone(pattern)
    except ImportError:
        raise ImportError(
            "Package 'exrex', for regex, not installed. Install with: pip install exrex"
        )


def _random_string(rng, length = 8):
    alphabet = string.ascii_lowercase
    return ''.join(rng.choice(alphabet) for _ in range(length))


def _random_datetime(rng):
    import datetime
    start = datetime.datetime(2020, 1, 1)
    delta_days = (datetime.datetime.now() - start).days
    random_day = rng.randint(0, max(delta_days, 1))
    dt = start + datetime.timedelta(days=random_day)
    return dt.isoformat()


def generate_node_properties(node, index, rng):
    props = {}
    for prop in node.properties:
        props[prop.name] = generate_value(prop.type, index, rng)
    return props


def generate_nodes(node, count, rng, batch_size= 5000):
    batch = []
    for i in range(count):
        record = {
            "_id": f"{node.name}_{i}",
            **generate_node_properties(node, i, rng),
        }
        batch.append(record)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def generate_edges(edge, source_ids, target_ids, rng, sharing_mode = "Shared", batch_size = 5000):

    card = edge.cardinality
    min_edges = card.min if card else 1
    max_edges = (card.max if card and not card.is_unbounded() else 5) if card else 1

    no_self_loop = edge.no_self_loop()
    acyclic = edge.is_acyclic()
    same_type = edge.source.name == edge.target.name

    batch = []

    if sharing_mode == "NotShared":
        pool = list(target_ids)
        pool_size = len(pool)

        for src_idx, src_id in enumerate(source_ids):
            if pool_size <= 0:
                break

            num_edges = rng.randint(min_edges, max_edges) if max_edges >= min_edges else min_edges
            num_edges = min(num_edges, pool_size)

            chosen = []
            for _ in range(num_edges):
                idx = rng.randrange(pool_size)
                candidate = pool[idx]

                if no_self_loop and same_type and candidate == src_id:
                    if pool_size <= 1:
                        continue
                    idx2 = rng.randrange(pool_size)
                    candidate = pool[idx2]
                    idx = idx2
                    if candidate == src_id:
                        continue

                chosen.append(candidate)
                pool_size -= 1
                pool[idx] = pool[pool_size]

            for tgt_id in chosen:
                record = {
                    "from": src_id,
                    "to": tgt_id,
                    **generate_node_properties(edge, src_idx, rng),
                }
                batch.append(record)

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

        if batch:
            yield batch
        return

    m = len(target_ids)

    for src_idx, src_id in enumerate(source_ids):
        num_edges = rng.randint(min_edges, max_edges) if max_edges >= min_edges else min_edges

        if acyclic and same_type:
            available = m - (src_idx + 1)
            if available <= 0:
                continue
            k = min(num_edges, available)
            offset = src_idx + 1
            picks_idx = rng.sample(range(offset, m), k=k)
            chosen = [target_ids[i] for i in picks_idx]
        else:
            k = min(num_edges, m)
            if k <= 0:
                continue
            chosen = rng.sample(target_ids, k=k)

            if no_self_loop and same_type and src_id in chosen:
                chosen = [t for t in chosen if t != src_id]
                if len(chosen) < k and m > k:
                    extra = rng.sample(target_ids, k=1)[0]
                    tries = 0
                    while (extra == src_id or extra in chosen) and tries < 5:
                        extra = rng.sample(target_ids, k=1)[0]
                        tries += 1
                    if extra != src_id and extra not in chosen:
                        chosen.append(extra)

        for tgt_id in chosen:
            record = {
                "from": src_id,
                "to": tgt_id,
                **generate_node_properties(edge, src_idx, rng),
            }
            batch.append(record)

            if len(batch) >= batch_size:
                yield batch
                batch = []

    if batch:
        yield batch


def _sharing_mode_for(model, edge):
    spec = model.spec.sharing_for(edge.name) if model.spec else None
    return spec.mode if spec else "Shared"


def generate_dataset_streaming(model, seed= None, batch_size= 5000):

    rng = random.Random(seed)
    node_ids_by_type: Dict[str, List[str]] = {}

    for node in model.nodes:
        count = model.count_for(node.name)
        ids_accum: List[str] = []

        for batch in generate_nodes(node, count, rng, batch_size):
            ids_accum.extend(r["_id"] for r in batch)
            yield ("node", node.name, batch)

        node_ids_by_type[node.name] = ids_accum

    for edge in model.edges:
        source_ids = node_ids_by_type.get(edge.source.name, [])
        target_ids = node_ids_by_type.get(edge.target.name, [])
        sharing_mode = _sharing_mode_for(model, edge)

        for batch in generate_edges(
            edge, source_ids, target_ids, rng,
            sharing_mode=sharing_mode, batch_size=batch_size,
        ):
            yield ("edge", edge.name, batch)


def generate_dataset(model, seed = None, batch_size = 5000):
    rng = random.Random(seed)
    nodes_by_type: Dict[str, List[Dict]] = {}
    node_ids_by_type: Dict[str, List[str]] = {}

    for node in model.nodes:
        count = model.count_for(node.name)
        all_records = []
        for batch in generate_nodes(node, count, rng, batch_size):
            all_records.extend(batch)
        nodes_by_type[node.name] = all_records
        node_ids_by_type[node.name] = [r["_id"] for r in all_records]

    edges_by_type: Dict[str, List[Dict]] = {}
    for edge in model.edges:
        source_ids = node_ids_by_type.get(edge.source.name, [])
        target_ids = node_ids_by_type.get(edge.target.name, [])

        all_edges = []
        for batch in generate_edges(edge, source_ids, target_ids, rng, batch_size):
            all_edges.extend(batch)
        edges_by_type[edge.name] = all_edges

    return {"nodes": nodes_by_type, "edges": edges_by_type}