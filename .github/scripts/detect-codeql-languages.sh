#!/usr/bin/env bash
set -euo pipefail

declare -a languages=()

add_language() {
  local candidate="$1"
  for existing in "${languages[@]:-}"; do
    if [[ "$existing" == "$candidate" ]]; then
      return
    fi
  done
  languages+=("$candidate")
}

has_match() {
  find . -path './.git' -prune -o -type f \( "$@" \) -print -quit | grep -q .
}

if has_match -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name 'package.json'; then
  add_language 'javascript-typescript'
fi

if has_match -name '*.py' -o -name 'pyproject.toml' -o -name 'requirements.txt'; then
  add_language 'python'
fi

if has_match -name '*.java' -o -name '*.kt' -o -name '*.kts' -o -name 'pom.xml' -o -name 'build.gradle' -o -name 'build.gradle.kts'; then
  add_language 'java-kotlin'
fi

if has_match -name '*.go' -o -name 'go.mod'; then
  add_language 'go'
fi

if has_match -name '*.rb' -o -name 'Gemfile'; then
  add_language 'ruby'
fi

if has_match -name '*.swift' -o -name 'Package.swift'; then
  add_language 'swift'
fi

if has_match -path './.github/workflows/*' -o -path './.github/actions/*'; then
  add_language 'actions'
fi

printf '['
for i in "${!languages[@]}"; do
  [[ "$i" -gt 0 ]] && printf ','
  printf '"%s"' "${languages[$i]}"
done
printf ']\n'
