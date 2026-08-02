# Manual Release Package Utility

## Purpose

GitHub Releases for `obsidian-tools` are stable, template-based publications
without custom assets. Publishing a release does not start package generation,
create an upgrade toolkit, or promote a prerelease.

The inherited package builder and workflow remain available only as optional
manual maintenance utilities. They are outside the normal release process and
must not be run unless a maintainer explicitly requests a package for an
existing release.

The agent rules come from
[agent-coding-rules](https://github.com/asphyx0r/agent-coding-rules), a
repository that provides practical behavior and code-quality rules for AI
coding agents.

GitHub provides its standard source archives for each release:

- `Source code (zip)`
- `Source code (tar.gz)`

Those archives contain only files committed in `obsidian-tools` at the release
tag. No additional release asset is required by repository policy.

## Optional Generated File

An explicitly requested manual run creates one enriched package named like
this:

```text
obsidian-tools-vX.Y.Z-with-agent-rules.zip
```

The ZIP includes the normal starter kit files plus these files from
`agent-coding-rules`:

- `AGENTS.md`
- `CODING_RULES.md`
- `COMMIT_RULES.md`
- `DOCUMENTATION_RULES.md`
- `LANGUAGE_RULES.md`
- `RELEASE_RULES.md`

The ZIP also includes two provenance files:

- `_agent-rules-source.json` records the packaged repository, upstream starter
  kit, and agent-rules references and commits.
- `_starter-kit-files.json` records each managed path, raw and canonical
  SHA-256 digests, content kind, Git mode, and upgrade strategy.

This downstream repository never builds or uploads a starter-kit upgrade
toolkit. The cumulative updater remains available locally for repository
maintenance but is not a release asset.

For a concise usage procedure in French, see
[Upgrade toolkit](upgrade-toolkit.md).

The cumulative updater classifies the six rule files and
`_agent-rules-source.json` as `agent-rules`. It reports those paths but never
writes them. Each target repository remains responsible for synchronizing
those files through its own pull-request workflow.

Repository-specific inventories and operator documentation are
initialization-only. Cumulative upgrades preserve `docs/SKILLS.md`,
`docs/release-package.md`, `docs/repository-files.md`, and `tools/README.md`
instead of attempting an unsafe generic merge. They also preserve
`tools/repository-audit.sh`, whose test and tool inventory belongs to the
target repository.

When an initialization-only file changed upstream, the plan reports
`review-initialize-only`. The signal does not block or write the target; it
identifies repository-owned content that maintainers should review separately.

## Rule Freshness Gate

The package builder resolves the requested public `agent-coding-rules` release
and compares it with the tracked `_agent-rules-source.json`. It then verifies
the canonical hash of every tracked rule. A customized file is accepted only
when provenance schema 3 contains its matching `preservedFiles` record.

No source-repository GitHub App token is required. The built-in workflow token
is used only to upload assets to the current repository release.

## Manual Release Mode

Use this exceptional mode only after a maintainer explicitly requests an
enriched package for an existing release. It is not part of release completion.

The release must already exist on GitHub before running the workflow manually.
The `tag` input must be an existing GitHub release tag that uses SemVer with a
leading `v`, for example `v1.3.0`. The manual workflow uploads an asset to
that release; it does not create the release itself.

Manual runs never create, promote, or otherwise edit a GitHub Release.

1. Open the `obsidian-tools` repository on GitHub.
2. Open the **Actions** tab.
3. Select the **Manual release package** workflow.
4. Click **Run workflow**.
5. Fill in `tag` with the release tag to package, for example `v1.3.0`.
6. Fill `agent_rules_ref` with `latest` or a SemVer `agent-coding-rules` tag,
   for example `v1.36.1`.
7. Click **Run workflow**.

Manual release packages accept `latest` or an explicit SemVer tag. Use a SemVer
tag when you need to recreate a package from a known agent-rules release.
Branch names are still rejected so the generated asset stays reproducible.

When the workflow finishes, verify the package only when it was explicitly
requested. Normal `obsidian-tools` releases must remain asset-free.

## Local Test

Run the full repository audit locally before publishing a release:

```bash
bash tools/repository-audit.sh
```

The full audit intentionally resolves the latest published full
`agent-coding-rules` release during package smoke checks. Treat a failure to
resolve or validate that latest release as an audit failure before publishing.
It also needs network access to npm for Markdown lint bootstrapping and PyPI
for Codespell bootstrapping. Use `markdown`, `spelling`, or `static` when you
need to isolate one audit family.

You can also test only the package generation locally before publishing a release.

From the repository root, run:

```powershell
powershell -NoProfile -File tools\build-release-package.ps1 `
  -RepositoryRef local-test `
  -OutputDirectory .tmp\release-package-test `
  -PackageName test-release-package.zip
```

Inspect the generated ZIP:

```powershell
tar -tf .tmp\release-package-test\test-release-package.zip
tar -xOf .tmp\release-package-test\test-release-package.zip _agent-rules-source.json
tar -xOf .tmp\release-package-test\test-release-package.zip _starter-kit-files.json
```

The local test creates a ZIP only. It does not upload anything to GitHub.
`AgentRulesRef` defaults to `latest`; pass a SemVer tag only when you need to
assert a known agent-rules release. The argument validates tracked content; it
does not overlay files from the source repository.

The script copies files reported by `git ls-files`. Local untracked files are
not included in the package. This is intentional, because release packages
should be built from committed repository content.

## Troubleshooting

An asset-free GitHub Release is the expected result. Do not run the manual
workflow merely because no custom asset is present.

If the manual workflow fails, check that the `tag` input matches an existing
GitHub release tag using SemVer with a leading `v`.

If the package must use a specific agent rules version, run the manual
workflow again with an explicit SemVer `agent_rules_ref` value.
