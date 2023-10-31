#!/bin/bash
cd /harness/indico-readme
git checkout -b docs-version-$TAG
./add_frontmatter.yaml
# touch test.md
# git add test.md
git add --all
git commit -m "a set of doc changes"
git push --set-upstream origin docs-version-$TAG
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/IndicoDataSolutions/indico-readme/pulls \
  -d '{"title":"Amazing new feature","body":"Please pull these awesome changes in!","head":"docs-version-'"$TAG"'","base":"main"}'
