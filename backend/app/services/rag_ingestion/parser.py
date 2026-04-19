from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

PHASE_PATTERN = re.compile(r"phase_id\s*:\s*`?([a-zA-Z0-9_-]+)`?", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index is None:
        return {}, text

    frontmatter_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).strip()
    metadata = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(metadata, dict):
        return {}, body
    return metadata, body


def normalize_whitespace(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def split_markdown_sections(markdown_body: str) -> list[tuple[str, str]]:
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ],
        strip_headers=False,
    )
    split_docs = splitter.split_text(markdown_body)

    sections: list[tuple[str, str]] = []
    for doc in split_docs:
        header_parts: list[str] = []
        for i in range(1, 7):
            value = doc.metadata.get(f"Header {i}")
            if value:
                header_parts.append(str(value).strip())
        heading_path = " > ".join(header_parts) if header_parts else "root"
        sections.append((heading_path, doc.page_content))
    return sections


def load_documents(source_dir: Path) -> list[tuple[Path, str]]:
    docs: list[tuple[Path, str]] = []
    for file_path in source_dir.rglob("*.md"):
        docs.append((file_path, file_path.read_text(encoding="utf-8")))
    return docs


def extract_phase_id(section_text: str) -> str | None:
    match = PHASE_PATTERN.search(section_text)
    if match:
        return match.group(1)
    return None


def stable_chunk_id(source_path: str, heading_path: str, chunk_index: int, chunk_text: str) -> str:
    digest = hashlib.sha256(
        f"{source_path}|{heading_path}|{chunk_index}|{chunk_text}".encode("utf-8")
    ).hexdigest()
    return f"chunk-{digest[:24]}"


def build_chunk_records(
    source_root: Path,
    file_path: Path,
    content: str,
    chunk_size: int,
    overlap: int,
) -> list[tuple[str, str, dict[str, Any]]]:
    doc_meta, body = parse_frontmatter(content)
    normalized_body = normalize_whitespace(body)
    if not normalized_body:
        return []

    rel_source = file_path.relative_to(source_root).as_posix()
    sections = split_markdown_sections(normalized_body)
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    records: list[tuple[str, str, dict[str, Any]]] = []
    running_index = 0

    for heading_path, section_text in sections:
        clean_section = normalize_whitespace(section_text)
        if not clean_section:
            continue

        phase_id = extract_phase_id(clean_section)
        text_chunks = fallback_splitter.split_text(clean_section)

        for text_chunk in text_chunks:
            metadata: dict[str, Any] = {
                "source_path": rel_source,
                "heading_path": heading_path,
                "algorithm": str(doc_meta.get("algorithm", "unknown")),
                "doc_type": str(doc_meta.get("doc_type", "unknown")),
                "language": str(doc_meta.get("language", "unknown")),
                "level": str(doc_meta.get("level", "unknown")),
                "version": str(doc_meta.get("version", "unknown")),
                "source_scope": str(doc_meta.get("source_scope", "static_knowledge")),
            }
            if phase_id:
                metadata["phase_id"] = phase_id

            tags = doc_meta.get("intent_tags")
            if not isinstance(tags, list):
                tags = doc_meta.get("intent_set", [])
            if isinstance(tags, list):
                metadata["intent_tags"] = ",".join(str(tag) for tag in tags)

            chunk_id = stable_chunk_id(rel_source, heading_path, running_index, text_chunk)
            records.append((chunk_id, text_chunk, metadata))
            running_index += 1

    return records
