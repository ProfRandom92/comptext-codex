"""Module M: MCP Integration - Multi-agent messaging, tool routing, contract governance."""

from typing import Any, Dict

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="M",
    name="MCP Integration",
    purpose="Multi-agent messaging, tool routing, and contract governance",
    token_priority="high",
    security={"pii_safe": True, "threat_model": "capability_scoped"},
    privacy={"dp_budget": "epsilon<=0.2_per_exchange", "federated_ready": True},
)
class ModuleM(BaseModule):
    """MCP Integration module for multi-agent systems."""

    @codex_command(syntax="@AGENT_ROLE[name, capabilities, ...]", description="Define agent role and capabilities", token_cost_hint=40)
    def execute_agent_role(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        name = kwargs.get("name", "Agent")
        caps = kwargs.get("capabilities", [])
        return {"agent_name": name, "capabilities": caps if isinstance(caps, list) else [caps], "constraints": kwargs.get("constraints", []), "role_defined": True}

    @codex_command(syntax="@TASK_ASSIGN[task, workflow, ...]", description="Assign task to agents", token_cost_hint=40)
    def execute_task_assign(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        task = kwargs.get("task", "default_task")
        wf = kwargs.get("workflow", [])
        return {"task": task, "workflow": wf if isinstance(wf, list) else [wf], "collaboration": kwargs.get("collaboration", "sequential"), "status": "assigned"}


def get_module() -> ModuleM:
    return ModuleM()
