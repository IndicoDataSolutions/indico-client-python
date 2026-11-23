#!/usr/bin/env bash
# Tags HEAD with a release version and pushes the tag, which starts .github/workflows/release.yml.
set -euo pipefail

REMOTE=origin
WORKFLOW=release.yml
REMOTE_TAGS=''
NUM='(0|[1-9][0-9]*)'
VERSION_RE="^${NUM}\\.${NUM}\\.${NUM}(-(alpha|beta|rc|a|b)${NUM}|\\.(post|dev)${NUM})?\$"

if [[ -t 1 && -t 2 && -z "${NO_COLOR:-}" ]]; then
    GREEN=$'\033[32m' YELLOW=$'\033[33m' RED=$'\033[31m' BLUE=$'\033[34m' BOLD=$'\033[1m' RESET=$'\033[0m'
else
    GREEN='' YELLOW='' RED='' BLUE='' BOLD='' RESET=''
fi

say() { printf '%s%s%s %s\n' "$1" "$2" "$RESET" "$3"; }
ok() { say "$GREEN" "✓" "$1"; }
warn() { say "$YELLOW" "!" "$1"; }
act() { say "$BLUE" "→" "$1"; }
fail() {
    say "$RED" "✗" "$1" >&2
    exit 1
}

shapes() {
    cat <<EOF
  7.11.0          release
  7.11.0-alpha1   prerelease, published as 7.11.0a1
  7.11.0-beta1    prerelease, published as 7.11.0b1
  7.11.0-rc1      prerelease, published as 7.11.0rc1
  7.11.0-a1       prerelease, published as 7.11.0a1
  7.11.0-b1       prerelease, published as 7.11.0b1
  7.11.0.post1    post release
  7.11.0.dev1     dev release
EOF
}

usage() {
    cat <<EOF
Usage: scripts/release.sh <version> [--dry-run] [--yes] [--allow-older]

Tags HEAD with <version> and pushes the tag to ${REMOTE}.

Options:
  --dry-run      run every check, create and push nothing
  --yes          skip the confirmation prompt
  --allow-older  allow a version whose X.Y.Z is below the highest X.Y.Z tagged on ${REMOTE}
  -h, --help     show this help

Accepted versions (lowercase, no "v" prefix, no leading zeros):
$(shapes)

A .postN version needs its X.Y.Z tag on ${REMOTE}. A version already published
under another spelling (7.11.0-a1 vs 7.11.0-alpha1) is refused.
EOF
}

# Prints the version PyPI shows for an accepted tag.
published_version() {
    sed -E 's/-(alpha|a)([0-9]+)$/a\2/; s/-(beta|b)([0-9]+)$/b\2/; s/-rc([0-9]+)$/rc\1/' <<<"$1"
}

# Prints the GitHub Actions URL for the release workflow, from a git or https remote URL.
actions_url() {
    local path
    path=$(sed -E 's#^(git@|ssh://git@|https?://)github\.com[:/]##; s#\.git$##; s#/$##' <<<"$1")
    [[ "$path" =~ ^[^/]+/[^/]+$ ]] || return 1
    printf 'https://github.com/%s/actions/workflows/%s\n' "$path" "$WORKFLOW"
}

check_version() {
    [[ "$1" =~ $VERSION_RE ]] && return 0
    printf 'Accepted shapes (lowercase, no "v" prefix, no leading zeros):\n%s\n' "$(shapes)" >&2
    fail "invalid version '$1'"
}

# Prints the tag names found on origin, one per line.
remote_tag_names() {
    cut -f2 <<<"$REMOTE_TAGS" | cut -d/ -f3-
}

check_not_older() {
    local base=${1%%[-.][a-z]*} allow_older=$2 high_base high_tag
    read -r high_base high_tag < <(remote_tag_names | grep -E '^[0-9]+\.[0-9]+\.[0-9]+([-.]|$)' |
        awk '{match($0, /^[0-9]+\.[0-9]+\.[0-9]+/); print substr($0, 1, RLENGTH), $0}' |
        sort -V -s -k1,1 | tail -n1) || true
    if [[ -n "${high_base:-}" && "$base" != "$high_base" && "$(printf '%s\n%s\n' "$base" "$high_base" | sort -V | head -n1)" == "$base" ]]; then
        ((allow_older)) || fail "version $1 is older than the highest tag $high_tag; pass --allow-older to release on an older line"
        warn "releasing $1, older than the highest tag $high_tag"
        return 0
    fi
    ok "version is not older than the highest tag"
}

check_clean_tree() {
    if ! git diff --quiet || ! git diff --cached --quiet; then
        fail "working tree has staged or unstaged changes"
    fi
    ok "working tree is clean"
}

check_tag_free() {
    local tag=$1
    ! remote_tag_names | grep -qxF -- "$tag" || fail "tag $tag already exists on $REMOTE"
    ! git rev-parse -q --verify "refs/tags/$tag" >/dev/null ||
        fail "tag $tag exists locally but not on $REMOTE (an interrupted run?); remove it with: git tag -d $tag"
    ok "tag $tag is unused"
}

check_published_free() {
    local tag=$1 published name
    published=$(published_version "$tag")
    while read -r name; do
        [[ "$name" != "$tag" && "$name" =~ $VERSION_RE && "$(published_version "$name")" == "$published" ]] &&
            fail "tag $name on $REMOTE already publishes as $published"
    done < <(remote_tag_names)
    ok "version $published is not published under another tag"
}

check_post_base() {
    [[ "$1" =~ ^(.+)\.post[0-9]+$ ]] || return 0
    remote_tag_names | grep -qxF -- "${BASH_REMATCH[1]}" ||
        fail "$1 needs its base release, but tag ${BASH_REMATCH[1]} is not on $REMOTE"
    ok "base release ${BASH_REMATCH[1]} exists"
}

check_head_untagged() {
    local existing
    existing=$(git tag --points-at HEAD | paste -sd' ' -)
    [[ -z "$existing" ]] || fail "HEAD already carries tag $existing; one tag per commit"
    ok "HEAD carries no tag"
}

check_head_pushed() {
    local branches
    branches=$(git for-each-ref --contains HEAD --format='%(refname)' "refs/remotes/$REMOTE/" | grep -vx "refs/remotes/$REMOTE/HEAD" | sed 's#^refs/remotes/##' || true)
    [[ -n "$branches" ]] || fail "HEAD is not on any $REMOTE branch; push it first"
    ok "HEAD is on $REMOTE ($(paste -sd' ' - <<<"$branches"))"
}

check_default_tip() {
    local default
    default=$(git symbolic-ref --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null) ||
        fail "cannot resolve the default branch; run: git remote set-head $REMOTE --auto"
    if [[ "$(git rev-parse HEAD)" == "$(git rev-parse "$default")" ]]; then
        ok "HEAD is the tip of $default"
    elif git merge-base --is-ancestor HEAD "$default"; then
        warn "HEAD is an older commit of $default"
    else
        warn "HEAD is not merged into $default"
    fi
}

confirm() {
    local reply
    [[ -t 0 ]] || fail "stdin is not a terminal; pass --yes to confirm"
    read -r -p "Create and push this tag? [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]] || fail "aborted"
}

summary() {
    local branch published
    branch=$(git symbolic-ref --short -q HEAD || echo detached)
    published=$(published_version "$1")
    printf '\n  %sversion%s  %s\n' "$BOLD" "$RESET" "$1"
    [[ "$published" == "$1" ]] || printf '  %spypi%s     %s\n' "$BOLD" "$RESET" "$published"
    printf '  %scommit%s   %s %s\n  %sbranch%s   %s\n\n' \
        "$BOLD" "$RESET" "$(git rev-parse --short HEAD)" "$(git log -1 --format=%s)" \
        "$BOLD" "$RESET" "$branch"
}

push_tag() {
    local tag=$1 remote_sha
    git tag "$tag"
    if git push "$REMOTE" "refs/tags/$tag"; then
        ok "pushed tag $tag"
        return 0
    fi
    remote_sha=$(git ls-remote --refs "$REMOTE" "refs/tags/$tag" | cut -f1) ||
        fail "push failed and $REMOTE could not be checked; state unknown, local tag kept; check: git ls-remote --tags $REMOTE $tag"
    if [[ -n "$remote_sha" ]]; then
        [[ "$remote_sha" == "$(git rev-parse HEAD)" ]] ||
            fail "tag $tag on $REMOTE points at a different commit (${remote_sha:0:7}, HEAD is $(git rev-parse --short HEAD)); local tag kept, remove it with: git tag -d $tag"
        warn "push reported an error but tag $tag is on $REMOTE and the release run has started; local tag kept"
        return 0
    fi
    git tag -d "$tag" >/dev/null
    fail "push failed; local tag $tag removed"
}

main() {
    local version='' dry_run=0 assume_yes=0 allow_older=0 arg url
    for arg in "$@"; do
        case "$arg" in
        -h | --help) usage; return 0 ;;
        --dry-run) dry_run=1 ;;
        --yes) assume_yes=1 ;;
        --allow-older) allow_older=1 ;;
        -*) usage >&2; fail "unknown option $arg" ;;
        *) [[ -z "$version" ]] || fail "only one version may be given"; version=$arg ;;
        esac
    done
    [[ -n "$version" ]] || { usage >&2; fail "missing version"; }

    check_version "$version"
    ok "version $version is valid"
    check_clean_tree
    act "fetching tags from $REMOTE"
    git fetch --tags --prune --no-prune-tags "$REMOTE" ||
        fail "fetch from $REMOTE failed; a local tag that differs from $REMOTE is a common cause"
    REMOTE_TAGS=$(git ls-remote --tags --refs "$REMOTE") || fail "cannot list tags on $REMOTE"
    check_not_older "$version" "$allow_older"
    check_tag_free "$version"
    check_published_free "$version"
    check_post_base "$version"
    check_head_untagged
    check_head_pushed
    check_default_tip
    summary "$version"

    if ((dry_run)); then
        act "dry run: would run git tag $version"
        act "dry run: would run git push $REMOTE refs/tags/$version"
        return 0
    fi
    ((assume_yes)) || confirm
    push_tag "$version"

    if url=$(actions_url "$(git remote get-url "$REMOTE")"); then
        act "watch and approve the run: $url"
    else
        warn "cannot derive a GitHub URL from $REMOTE; open the Actions tab and find the $WORKFLOW run"
    fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
