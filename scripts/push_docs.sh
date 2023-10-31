#!/bin/bash
git clone https://user:$GITHUB_TOKEN@github.com/IndicoDataSolutions/indico-readme.git
cd indico-readme
git config --global user.email "engineering@indico.io"
git config --global user.name "cat-automation"
git checkout meghan/reorg
git checkout -b docs-version-$TAG
mkdir markdown
cp -r $DOCS_PATH ./markdown/$LANGUAGE
bash add_frontmatter_yaml.sh

git add ./markdown/$LANGUAGE
git commit -m "a set of doc changes"

git push --set-upstream origin docs-version-$TAG
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/IndicoDataSolutions/indico-readme/pulls \
  -d '{"title":"Amazing new feature","body":"Please pull these awesome changes in!","head":"docs-version-'"$TAG"'","base":"meghan/reorg"}'
