from typing import List, Optional, Union

class IntType:
    def __init__(self, parent=None, min=None, max=None):
        self.parent = parent
        self.min = min
        self.max = max

    def has_range(self):
        return self.min is not None and self.max is not None

    def __repr__(self):
        return f"IntType(min={self.min}, max={self.max})"


class FloatType:
    def __init__(self, parent=None, min=None, max=None):
        self.parent = parent
        self.min = min
        self.max = max

    def has_range(self):
        return self.min is not None and self.max is not None

    def __repr__(self):
        return f"FloatType(min={self.min}, max={self.max})"


class StringType:
    def __init__(self, parent=None, pattern=None):
        self.parent = parent
        self.pattern = pattern

    def has_pattern(self):
        return self.pattern is not None

    def __repr__(self):
        return f"StringType(pattern={self.pattern!r})"


class EnumType:
    def __init__(self, parent=None, values=None):
        self.parent = parent
        self.values = values if values is not None else []

    def __repr__(self):
        return f"EnumType(values={self.values})"


class BoolType:
    def __init__(self, parent=None, kind=None):
        self.parent = parent
        self.kind = kind

    def __repr__(self):
        return "BoolType()"


class DateType:
    def __init__(self, parent=None, kind=None):
        self.parent = parent
        self.kind = kind

    def __repr__(self):
        return "DateType()"

class PropertyDef:
    def __init__(self, parent=None, name=None, type=None):
        self.parent = parent
        self.name = name
        self.type = type

    def __repr__(self):
        return f"PropertyDef(name={self.name!r}, type={self.type})"


class NodeDef:
    def __init__(self, parent=None, name=None, properties=None):
        self.parent = parent
        self.name = name
        self.properties = properties if properties is not None else []

    def property_names(self):
        return [p.name for p in self.properties]

    def property_by_name(self, name):
        return next((p for p in self.properties if p.name == name), None)

    def __repr__(self):
        return f"NodeDef(name={self.name!r}, properties={self.properties})"


class CardinalityDef:
    def __init__(self, parent=None, min=None, max=None):
        self.parent = parent
        self.min = min
        self.max = max  # int ili '*'

    def is_unbounded(self):
        return self.max == '*'

    def __repr__(self):
        return f"CardinalityDef(min={self.min}, max={self.max!r})"


class EdgeDef:
    def __init__(
        self,
        parent=None,
        name=None,
        source=None,
        target=None,
        cardinality=None,
        constraints=None,
        properties=None,
    ):
        self.parent = parent
        self.name = name
        self.source = source
        self.target = target
        self.cardinality = cardinality
        self.constraints = constraints if constraints is not None else []
        self.properties = properties if properties is not None else []

    def is_acyclic(self):
        return 'acyclic' in self.constraints

    def is_unique(self):
        return 'unique' in self.constraints

    def no_self_loop(self):
        return 'no_self_loop' in self.constraints

    def __repr__(self):
        return (
            f"EdgeDef(name={self.name!r}, "
            f"source={self.source.name if self.source else None!r}, "
            f"target={self.target.name if self.target else None!r}, "
            f"cardinality={self.cardinality}, "
            f"constraints={self.constraints}, "
            f"properties={self.properties})"
        )

class DataAmount:
    _MULTIPLIERS = {'k': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, None: 1}

    def __init__(self, parent=None, value=None, unit=None):
        self.parent = parent
        self.value = value
        self.unit = unit

    def resolved(self):
        return self.value * self._MULTIPLIERS[self.unit]

    def __repr__(self):
        return f"DataAmount(value={self.value}, unit={self.unit!r})"


class ClassPercentage:
    def __init__(self, parent=None, percent=None, target=None):
        self.parent = parent
        self.percent = percent
        self.target = target

    def __repr__(self):
        return (
            f"ClassPercentage(percent={self.percent}, "
            f"target={self.target.name if self.target else None!r})"
        )


class SharingSpec:
    def __init__(self, parent=None, target=None, mode=None):
        self.parent = parent
        self.target = target
        self.mode = mode

    def is_shared(self):
        return self.mode == 'Shared'

    def __repr__(self):
        return (
            f"SharingSpec(target={self.target.name if self.target else None!r}, "
            f"mode={self.mode!r})"
        )


class GenerateSpec:
    def __init__(
        self,
        parent=None,
        total=None,
        targets=None,
        percentages=None,
        sharing=None,
        Index=None,
    ):
        self.parent = parent
        self.total = total
        self.targets = targets if targets is not None else []
        self.percentages = percentages if percentages is not None else []
        self.sharing = sharing if sharing is not None else []
        self.add_index = bool(Index)

    def percentage_for(self, node_name):
        for p in self.percentages:
            if p.target.name == node_name:
                return p.percent
        return None

    def sharing_for(self, edge_name):
        return next((s for s in self.sharing if s.target.name == edge_name), None)

    def total_percent(self):
        return sum(p.percent for p in self.percentages)

    def __repr__(self):
        return (
            f"GenerateSpec(total={self.total}, targets={self.targets}, "
            f"percentages={self.percentages}, sharing={self.sharing}, "
            f"add_index={self.add_index})"
        )

class GraphGenModel:
    def __init__(self, parent=None, nodes=None, edges=None, spec=None):
        self.parent = parent
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []
        self.spec = spec

    def node_by_name(self, name):
        return next((n for n in self.nodes if n.name == name), None)

    def edge_by_name(self, name):
        return next((e for e in self.edges if e.name == name), None)

    def count_for(self, node_name):
        if self.spec is None:
            return 0
        percent = self.spec.percentage_for(node_name)
        if percent is None:
            return 0
        return round(self.spec.total.resolved() * percent / 100)

    def __repr__(self):
        return (
            f"GraphGenModel(nodes={len(self.nodes)}, edges={len(self.edges)}, "
            f"spec={self.spec})"
        )