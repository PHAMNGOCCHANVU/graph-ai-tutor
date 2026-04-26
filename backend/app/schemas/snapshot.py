from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    label: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class GraphPayload(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class SnapshotState(BaseModel):
    current_node: str | None = None
    visited: list[str] = Field(default_factory=list)
    queue: list[str] = Field(default_factory=list)
    distances: dict[str, float] = Field(default_factory=dict)
    notes: str | None = None


class AlgorithmSnapshot(BaseModel):
    step_id: int = Field(ge=0)
    algorithm: str
    graph: GraphPayload
    state: SnapshotState
    meta: dict[str, Any] = Field(default_factory=dict)
