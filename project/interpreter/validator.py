from typing import List
from model.classes import GraphGenModel

class ValidationError(Exception):

    def __init__(self, errors):
        self.errors = errors
        message = "Semantic validation didnt pass:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        super().__init__(message)


def validate_model(model):
    errors = []
    errors += _check_generate_spec_exists(model)

    if model.spec is None:
        raise ValidationError(errors)

    errors += _check_percentages_sum_to_100(model)
    errors += _check_all_nodes_covered_in_where(model)
    errors += _check_no_unknown_nodes_in_where(model)
    errors += _check_cardinality_bounds(model)
    errors += _check_acyclic_self_loop_consistency(model)
    errors += _check_cardinality_feasibility(model)
    errors += _check_property_type_ranges(model)
    errors += _check_enum_has_values(model)

    if errors:
        raise ValidationError(errors)

def _check_generate_spec_exists(model):
    if model.spec is None:
        return ["Model doesn't have 'generate:' block."]
    return []


def _check_percentages_sum_to_100(model):
    total = model.spec.total_percent()
    if total != 100:
        return [
            f"Sum of percentages in WHERE block is {total}%, "
            f"and has to be 100%."
        ]
    return []


def _check_all_nodes_covered_in_where(model):
    errors = []
    covered_names = {p.target.name for p in model.spec.percentages}
    for node in model.nodes:
        if node.name not in covered_names:
            errors.append(
                f"Node type '{node.name}' is defined in schema, but doesn't have a "
                f"percentage in WHERE block."
            )
    return errors


def _check_no_unknown_nodes_in_where(model):
    errors = []
    known_names = {n.name for n in model.nodes}
    for p in model.spec.percentages:
        if p.target is None or p.target.name not in known_names:
            errors.append(
                f"WHERE block references unknown node type"
                f"({p.target.name if p.target else '???'})."
            )
    return errors


def _check_cardinality_bounds(model):
    errors = []
    for edge in model.edges:
        card = edge.cardinality
        if card is None:
            continue
        if card.is_unbounded():
            continue
        if card.min > card.max:
            errors.append(
                f"Edge '{edge.name}': cardinality min ({card.min}) is bigger then "
                f"max ({card.max})."
            )
    return errors


def _check_acyclic_self_loop_consistency(model):
    errors = []
    for edge in model.edges:
        same_type = edge.source is not None and edge.target is not None \
            and edge.source.name == edge.target.name
        if same_type and edge.is_acyclic() and not edge.no_self_loop():
            errors.append(
                f"Edge '{edge.name}': goes from '{edge.source.name}' to the same type "
                f"and has an 'acyclic' constraint, but no 'no_self_loop' constraint. "
                f"A self-loop would automatically form a cycle; add 'no_self_loop' "
                f"or remove 'acyclic'."
            )
    return errors


def _check_cardinality_feasibility(model):
    errors = []
    for edge in model.edges:
        card = edge.cardinality
        if card is None or card.min == 0:
            continue

        source_count = model.count_for(edge.source.name) if edge.source else 0
        target_count = model.count_for(edge.target.name) if edge.target else 0

        if source_count == 0:
            errors.append(
                f"Edge '{edge.name}': cardinality min={card.min} requires "
                f"at least one instance of type '{edge.source.name}', but WHERE "
                f"specifies 0 instances for this type (check the percentage)."
            )
        if target_count == 0:
            errors.append(
                f"Edge '{edge.name}': cardinality min={card.min} requires "
                f"at least one instance of type '{edge.target.name}', but WHERE "
                f"specifies 0 instances for this type (check the percentage)."
            )
    return errors


def _check_property_type_ranges(model):
    errors = []
    for node in model.nodes:
        for prop in node.properties:
            t = prop.type
            has_range = hasattr(t, 'has_range') and t.has_range()
            if has_range and t.min > t.max:
                errors.append(
                    f"Property '{node.name}.{prop.name}': range min ({t.min}) "
                    f"is bigger then max ({t.max})."
                )
    return errors


def _check_enum_has_values(model):
    errors = []
    for node in model.nodes:
        for prop in node.properties:
            t = prop.type
            if type(t).__name__ == 'EnumType' and len(t.values) == 0:
                errors.append(
                    f"Property '{node.name}.{prop.name}': enum tip doesn't has any values. "
                )
    return errors