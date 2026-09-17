#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: publish-pr-media.sh --description <text> <media-file> [<media-file> ...]

Publish PR media to a new secret gist and print revision-pinned raw URLs.
Secret gists are unlisted, not private: uploaded media is public by URL.
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

description=""
files=()

while (($#)); do
  case "$1" in
    --description)
      (($# >= 2)) || die "--description requires a value"
      description=$2
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      files+=("$@")
      break
      ;;
    -*)
      die "unknown option: $1"
      ;;
    *)
      files+=("$1")
      shift
      ;;
  esac
done

[[ -n "$description" ]] || die "--description is required"
((${#files[@]} > 0)) || die "at least one media file is required"

for command_name in gh git curl file; do
  command -v "$command_name" >/dev/null 2>&1 || die "required command not found: $command_name"
done

names=()
seen_names="|"
shopt -s nocasematch
for media_path in "${files[@]}"; do
  [[ -f "$media_path" ]] || die "media file not found: $media_path"
  media_name=${media_path##*/}
  [[ "$media_name" =~ ^[A-Za-z0-9._-]+$ ]] || die "unsafe media filename: $media_name"

  case "$media_name" in
    *.png|*.jpg|*.jpeg|*.gif|*.webp|*.mp4|*.webm) ;;
    *) die "unsupported media type: $media_name" ;;
  esac

  case "$seen_names" in
    *"|$media_name|"*) die "duplicate media filename: $media_name" ;;
  esac
  seen_names="${seen_names}${media_name}|"
  names+=("$media_name")
done
shopt -u nocasematch

temp_root=$(mktemp -d "${TMPDIR:-/tmp}/publish-pr-media.XXXXXX")
trap 'rm -rf "$temp_root"' EXIT

placeholder="$temp_root/README.md"
printf '# PR media\n\nBinary media for %s.\n' "$description" >"$placeholder"

gist_url=$(gh gist create --desc "$description" "$placeholder")
gist_url=${gist_url%/}
case "$gist_url" in
  https://gist.github.com/*/*) ;;
  *) die "unexpected gist URL: $gist_url" ;;
esac

gist_path=${gist_url#https://gist.github.com/}
gist_owner=${gist_path%%/*}
gist_id=${gist_path##*/}
[[ -n "$gist_owner" && -n "$gist_id" && "$gist_owner" != "$gist_id" ]] \
  || die "could not parse gist owner and id from: $gist_url"

echo "created secret gist: $gist_url" >&2
echo "warning: secret gists are public by URL" >&2

clone_dir="$temp_root/gist"
git clone "$gist_url.git" "$clone_dir"

for index in "${!files[@]}"; do
  cp "${files[$index]}" "$clone_dir/${names[$index]}"
done

git -C "$clone_dir" add -- "${names[@]}"
git -C "$clone_dir" commit -m "Add PR media"
git -C "$clone_dir" push

revision=$(git -C "$clone_dir" rev-parse HEAD)
[[ "$revision" =~ ^[0-9a-fA-F]{40}$ ]] || die "unexpected gist revision: $revision"

first_raw_url="https://gist.githubusercontent.com/$gist_owner/$gist_id/raw/$revision/${names[0]}"
verify_path="$temp_root/verify-media"
curl --fail --silent --show-error --location --retry 3 \
  --output "$verify_path" "$first_raw_url"
[[ -s "$verify_path" ]] || die "raw media URL returned an empty file: $first_raw_url"
echo "verified media: $(file --brief "$verify_path")" >&2

printf 'gist_url\t%s\n' "$gist_url"
printf 'revision\t%s\n' "$revision"
for media_name in "${names[@]}"; do
  printf 'media_url\t%s\thttps://gist.githubusercontent.com/%s/%s/raw/%s/%s\n' \
    "$media_name" "$gist_owner" "$gist_id" "$revision" "$media_name"
done
