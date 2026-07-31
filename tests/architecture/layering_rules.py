"""Layering contract rules for the import-graph gate."""

from __future__ import annotations

from dataclasses import dataclass

from tests.architecture.import_graph import ImportEdge

COMMON_FORBIDDEN_TARGETS = frozenset({
    'crm',
    'tasks',
    'massmail',
    'chat',
    'help',
    'quality',
    'voip',
})


@dataclass(frozen=True, slots=True)
class LayeringRule:
    rule_id: str
    description: str

    def violates(self, edge: ImportEdge) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class SharedkernelIsolationRule(LayeringRule):
    rule_id: str = 'sharedkernel_isolation'
    description: str = 'sharedkernel must not import any project app'

    def violates(self, edge: ImportEdge) -> bool:
        return edge.source_app == 'sharedkernel'


@dataclass(frozen=True, slots=True)
class CommonFeatureIsolationRule(LayeringRule):
    rule_id: str = 'common_feature_isolation'
    description: str = (
        'common must not import crm, tasks, massmail, chat, help, quality or voip'
    )

    def violates(self, edge: ImportEdge) -> bool:
        return edge.source_app == 'common' and edge.target_app in COMMON_FORBIDDEN_TARGETS


@dataclass(frozen=True, slots=True)
class CrmCommonAdminIsolationRule(LayeringRule):
    rule_id: str = 'crm_common_admin_isolation'
    description: str = 'crm must not import common.admin'

    def violates(self, edge: ImportEdge) -> bool:
        return edge.source_app == 'crm' and edge.imported_module.startswith('common.admin')


CORE_LAYERING_RULES: tuple[LayeringRule, ...] = (
    SharedkernelIsolationRule(),
    CommonFeatureIsolationRule(),
    CrmCommonAdminIsolationRule(),
)


def core_rule_violations(edges: list[ImportEdge]) -> dict[str, list[ImportEdge]]:
    violations: dict[str, list[ImportEdge]] = {rule.rule_id: [] for rule in CORE_LAYERING_RULES}
    for edge in edges:
        for rule in CORE_LAYERING_RULES:
            if rule.violates(edge):
                violations[rule.rule_id].append(edge)
    return violations
