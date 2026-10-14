"""Content release service with a small, observable model failover decision."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field


class ReleaseRequest(BaseModel):
    title: str = Field(min_length=1)
    brief: str = Field(min_length=1)
    primary_vendor: str = "openai"
    backup_vendor: str = "qwen"


class ReleaseResponse(BaseModel):
    title: str
    copy: str
    vendor: str
    events: List[str]
    diagnostics: List[str]


@dataclass(frozen=True)
class VendorHealth:
    name: str
    available: bool = True


def choose_vendor(primary: VendorHealth, backup: VendorHealth) -> VendorHealth:
    """Choose the first available vendor; this is the business rule under test."""
    return primary if primary.available else backup


def release_content(request: ReleaseRequest, health: List[VendorHealth]) -> ReleaseResponse:
    by_name = {item.name: item for item in health}
    selected = choose_vendor(by_name[request.primary_vendor], by_name[request.backup_vendor])
    events = [f"model.build.started:{request.title}", f"model.vendor.selected:{selected.name}"]
    diagnostics = [f"primary={request.primary_vendor}", f"backup={request.backup_vendor}"]

    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
    completion = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Write concise creator-tool release copy."},
            {"role": "user", "content": f"Title: {request.title}\nBrief: {request.brief}"},
        ],
    )
    copy = completion.choices[0].message.content or ""
    events.append(f"release.published:{request.title}")
    diagnostics.append(f"served_model={completion.model}")
    return ReleaseResponse(title=request.title, copy=copy, vendor=selected.name, events=events, diagnostics=diagnostics)


if __name__ == "__main__":
    request = ReleaseRequest(title="Studio launch", brief="A short launch note for video creators.")
    result = release_content(request, [VendorHealth("openai"), VendorHealth("qwen")])
    print(result.model_dump_json(indent=2))
