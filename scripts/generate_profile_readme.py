#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ORG = os.getenv("README_ORG", "bssm-oss")
OUTPUT_PATH = Path(os.getenv("README_OUTPUT", "profile/README.md"))
API_BASE = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
REPRESENTATIVE_CONTRIBUTOR = "heodongun"

INTRO = """# BSSM OSS

> 부산소프트웨어마이스터고등학교 오픈소스 조직입니다.
>
> BSSM OSS는 부산소프트웨어마이스터고등학교에서 만들어지는 다양한 실험, 도구, 앱, 라이브러리, 자동화 프로젝트를 한곳에 모아 공개하는 조직입니다. 학습을 위해 만든 작은 시도부터 실제로 사용할 수 있는 완성도 높은 프로젝트까지 함께 다루며, 단순히 코드를 올려두는 저장소가 아니라 다른 사람이 읽고 실행하고 기여할 수 있는 공개 저장소를 만드는 것을 목표로 합니다.
>
> 이 조직에는 Android, macOS, CLI, 웹, AI 워크플로, 개발자 도구처럼 기술 스펙트럼이 넓은 프로젝트가 함께 쌓입니다. 그래서 BSSM OSS의 리포지토리는 결과물만 보여주는 공간이 아니라, 아이디어를 어떻게 구현했고 어떤 문제를 풀고 있는지, 그리고 다음 기여자가 어디서부터 참여하면 되는지까지 드러나는 오픈소스 작업 기록이어야 합니다.
"""

RULES = """## 🤝 오픈소스 운영 규칙

### 1. Repository 이름 규칙

- 모든 공개 저장소 이름은 **소문자 kebab-case**를 기본으로 합니다.
- 저장소 이름만 보고도 무엇을 만드는지 알 수 있어야 합니다.
- `test`, `final`, `new`, `awesome-project`처럼 의미가 약한 이름은 지양합니다.
- 라이브러리, 앱, CLI, 실험 프로젝트처럼 성격이 다르면 이름에도 그 차이가 드러나야 합니다.

### 2. Pull Request 규칙

- PR 하나에는 **하나의 주제**만 담습니다.
- PR 본문에는 최소한 **배경, 변경 내용, 확인 방법**이 들어가야 합니다.
- UI 또는 동작 변화가 있으면 스크린샷, 실행 결과, 예시 출력 중 하나 이상을 함께 남깁니다.
- 리뷰어가 빠르게 이해할 수 있도록 큰 변경은 여러 PR로 나눕니다.
- 머지 전에 제목과 본문만 읽어도 왜 필요한 변경인지 이해되어야 합니다.

### 3. README 필수 규칙

- 모든 공개 저장소에는 **README가 반드시 있어야 합니다.**
- README에는 최소한 **프로젝트 소개, 실행/설치 방법, 사용 방법, 기술 스택 또는 구조, 기여 방법**이 포함되어야 합니다.
- 외부 사용자가 처음 들어와도 무엇을 하는 프로젝트인지 1분 안에 이해할 수 있어야 합니다.
- 실행이 어려운 프로젝트일수록 예시 화면, CLI 예시, API 예시, 데모 링크 같은 보조 설명을 더 자세히 적습니다.

### 4. 공개 저장소 기본 원칙

- 공개 저장소는 결과물뿐 아니라 **설명 가능성**까지 포함해 관리합니다.
- 문서가 없거나, 실행 방법이 없거나, 목적이 불분명한 저장소는 공개 상태로 오래 방치하지 않습니다.
- 다른 사람이 이어서 개발할 수 있는 상태를 만드는 것을 기본 품질 기준으로 삼습니다.
"""

MANUAL_CATEGORY = {
    "AICall": "AI · Agent · Workflow",
    "AIStudyWeb": "AI · Agent · Workflow",
    "beautiful-ccg": "AI · Agent · Workflow",
    "claudeCode-codex-": "AI · Agent · Workflow",
    "CodeAgora": "AI · Agent · Workflow",
    "cotor": "AI · Agent · Workflow",
    "Free-API": "AI · Agent · Workflow",
    "globalAI": "AI · Agent · Workflow",
    "harness-for-yall": "AI · Agent · Workflow",
    "kakao-talk-auto-bot": "AI · Agent · Workflow",
    "pandaAPI": "AI · Agent · Workflow",
    "PlainCode": "AI · Agent · Workflow",
    "PLASMA": "AI · Agent · Workflow",
    "desktop-pet": "Mobile · Desktop Apps",
    "desktop-pet-evernight-dance": "Mobile · Desktop Apps",
    "daybar": "Mobile · Desktop Apps",
    "findkey": "Mobile · Desktop Apps",
    "kakao-talk-auto-bot-mac": "Mobile · Desktop Apps",
    "kakao-talk-auto-bot-template": "Mobile · Desktop Apps",
    "killsnail": "Mobile · Desktop Apps",
    "real-iga": "Mobile · Desktop Apps",
    "reunionManager": "Mobile · Desktop Apps",
    "StudentIDreplica-": "Mobile · Desktop Apps",
    "AdaptiveUIRuntime": "Web · Browser · UI",
    "bssm-oss-page": "Web · Browser · UI",
    "MorphUI": "Web · Browser · UI",
    "readable": "Web · Browser · UI",
    "repo-tag": "Web · Browser · UI",
    "syncingsh": "Web · Browser · UI",
    "ytm-jam-extension": "Web · Browser · UI",
    "ytm-jam-web": "Web · Browser · UI",
    "cli-speedrun": "CLI · Developer Tools · Infra",
    "dep-age": "CLI · Developer Tools · Infra",
    "git-roast": "CLI · Developer Tools · Infra",
    "homebrew-tap": "CLI · Developer Tools · Infra",
    "port-who": "CLI · Developer Tools · Infra",
    "setup.sh": "CLI · Developer Tools · Infra",
    "terminal-pet": "CLI · Developer Tools · Infra",
    "whatdid": "CLI · Developer Tools · Infra",
    "wireguard-vpn-manager": "CLI · Developer Tools · Infra",
    "ytm-jam-cli": "CLI · Developer Tools · Infra",
    "good-opensource-zip": "Knowledge · Skills · Curation",
    "obsidian-skills-codex": "Knowledge · Skills · Curation",
    "pm-skills-codex": "Knowledge · Skills · Curation",
    "tutor-skills-codex": "Knowledge · Skills · Curation",
    "better-notion2pdf": "Experiments · Misc",
    "commit-vibe": "Experiments · Misc",
    "cotor-test": "Experiments · Misc",
    "ganbatte": "Experiments · Misc",
    "marubase": "Experiments · Misc",
    "newrrow": "Experiments · Misc",
    "Photon": "Experiments · Misc",
    "play-with-your-term": "Experiments · Misc",
    "ytm-jam-server": "Experiments · Misc",
}

MANUAL_TAGS = {
    "AdaptiveUIRuntime": ["TypeScript", "UI", "Library"],
    "better-notion2pdf": ["TypeScript", "Notion", "PDF"],
    "CodeAgora": ["TypeScript", "AI", "Code Review"],
    "desktop-pet-evernight-dance": ["Asset", "Desktop Pet"],
    "good-opensource-zip": ["AI", "Curation"],
    "killsnail": ["Swift", "macOS", "Toy App"],
    "obsidian-skills-codex": ["Obsidian", "CLI", "Knowledge"],
    "repo-tag": ["Chrome", "Extension"],
}

CATEGORY_ORDER = [
    "AI · Agent · Workflow",
    "Mobile · Desktop Apps",
    "Web · Browser · UI",
    "CLI · Developer Tools · Infra",
    "Knowledge · Skills · Curation",
    "Experiments · Misc",
]


@dataclass
class RepoRow:
    name: str
    url: str
    description: str
    stars: int
    language: str | None
    topics: list[str]
    archived: bool
    created_at: str
    top_contributor: str | None


def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "bssm-oss-profile-readme-generator",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed: {path} -> {exc.code} {body}"
        ) from exc


def fetch_public_repos(org: str) -> list[dict[str, Any]]:
    page = 1
    repos: list[dict[str, Any]] = []
    while True:
        batch = api_get(
            f"/orgs/{org}/repos", {"per_page": 100, "type": "public", "page": page}
        )
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def fetch_top_contributor(org: str, repo_name: str) -> str | None:
    return REPRESENTATIVE_CONTRIBUTOR


def normalize_repo(repo: dict[str, Any], top_contributor: str | None) -> RepoRow:
    return RepoRow(
        name=repo["name"],
        url=repo["html_url"],
        description=(repo.get("description") or "").strip() or "설명 준비 중",
        stars=int(repo.get("stargazers_count", 0)),
        language=repo.get("language"),
        topics=repo.get("topics") or [],
        archived=bool(repo.get("archived", False)),
        created_at=repo.get("created_at", "")[:10],
        top_contributor=top_contributor,
    )


def category_for(repo: RepoRow) -> str:
    if repo.name in MANUAL_CATEGORY:
        return MANUAL_CATEGORY[repo.name]
    return "Experiments · Misc"


def tag_list(repo: RepoRow) -> list[str]:
    if repo.name in MANUAL_TAGS:
        return MANUAL_TAGS[repo.name]

    tags: list[str] = []
    if repo.language:
        tags.append(repo.language)
    combined = " ".join(
        [repo.name, repo.description, repo.language or "", *repo.topics]
    ).lower()
    keyword_tags = [
        ("AI", ["ai", "llm", "claude", "codex", "gemini", "openai", "mcp", "persona"]),
        ("Android", ["android", "kotlin", "안드로이드"]),
        ("macOS", ["swift", "macos", "menu bar", "appkit", "메뉴바"]),
        ("Web", ["web", "react", "svelte", "html", "landing"]),
        ("Browser", ["chrome", "extension", "browser", "dom", "aria"]),
        ("CLI", ["cli", "terminal", "tui"]),
        (
            "Infra",
            ["docker", "wireguard", "ubuntu", "debian", "bash", "shell", "homebrew"],
        ),
        ("Knowledge", ["obsidian", "skill", "study", "quiz", "curation", "catalog"]),
        ("Game", ["game", "블랙잭", "스피드런"]),
        ("YouTube", ["youtube", "ytm"]),
        ("Security", ["security", "credential", "gitleaks", "trufflehog"]),
        ("Automation", ["automation", "자동", "workflow", "orchestration"]),
        ("Extension", ["extension", "chrome mv3"]),
        ("Library", ["library", "라이브러리"]),
        ("Template", ["template", "템플릿"]),
        ("Asset", ["asset", "에셋"]),
        ("Research", ["research", "리서치"]),
    ]
    for label, keys in keyword_tags:
        if any(key in combined for key in keys) and label not in tags:
            tags.append(label)
    if repo.archived and "Archived" not in tags:
        tags.append("Archived")
    return tags[:4] or ["Misc"]


def render_top_repos(repos: list[RepoRow]) -> str:
    top = sorted(repos, key=lambda item: (-item.stars, item.name.lower()))[:3]
    lines = [
        "## ⭐ 가장 많은 스타를 받은 프로젝트",
        "",
        "| 프로젝트 | 설명 | Stars |",
        "| --- | --- | ---: |",
    ]
    for repo in top:
        lines.append(
            f"| [{repo.name}]({repo.url}) | {escape_cell(repo.description)} | {repo.stars} |"
        )
    return "\n".join(lines)


def render_catalog(repos: list[RepoRow]) -> str:
    grouped: dict[str, list[RepoRow]] = {category: [] for category in CATEGORY_ORDER}
    for repo in sorted(repos, key=lambda item: (-item.stars, item.name.lower())):
        grouped.setdefault(category_for(repo), []).append(repo)
    lines = [
        "## 🗂️ 카테고리별 프로젝트 카탈로그",
        "",
        "GitHub 공개 저장소를 기준으로 자동 정리됩니다. `대표 기여자`는 조직 대표 계정인 `heodongun`으로 통일해 표시하고, 태그는 언어·토픽·저장소 성격을 바탕으로 자동 생성합니다.",
        "",
    ]
    for category in CATEGORY_ORDER:
        repos_in_category = grouped.get(category, [])
        if not repos_in_category:
            continue
        lines.extend(
            [
                f"### {category}",
                "",
                "| 프로젝트 | 설명 | 대표 기여자 | 태그 |",
                "| --- | --- | --- | --- |",
            ]
        )
        for repo in repos_in_category:
            contributor = (
                f"[@{repo.top_contributor}](https://github.com/{repo.top_contributor})"
                if repo.top_contributor
                else "-"
            )
            tags = " ".join(f"`{tag}`" for tag in tag_list(repo))
            lines.append(
                f"| [{repo.name}]({repo.url}) | {escape_cell(repo.description)} | {contributor} | {tags} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def escape_cell(text: str) -> str:
    return text.replace("|", "\\|")


def build_readme(repos: list[RepoRow]) -> str:
    parts = [
        INTRO.strip(),
        "",
        render_top_repos(repos),
        "",
        render_catalog(repos),
        "",
        RULES.strip(),
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    raw_repos = fetch_public_repos(ORG)
    filtered = [repo for repo in raw_repos if repo.get("name") != ".github"]
    repos: list[RepoRow] = []
    for raw in filtered:
        contributor = fetch_top_contributor(ORG, raw["name"])
        repos.append(normalize_repo(raw, contributor))
    content = build_readme(repos)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} for {len(repos)} public repositories in {ORG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
