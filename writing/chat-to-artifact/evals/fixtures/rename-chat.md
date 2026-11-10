# Exported chat: naming the CLI

**Sam:** We need a name for the new CLI. I was thinking `forge`.

**Assistant:** `forge` collides with the Foundry tool and the Atlassian product; search results will be noisy. Alternatives: `kiln`, `anvil`, `smith`.

**Sam:** Let's go with anvil then.

**Assistant:** `anvil` is also taken on PyPI by an unrelated package, so `pip install anvil` would install the wrong thing.

**Sam:** Ugh. OK, kiln. Check PyPI?

**Assistant:** `kiln` is free on PyPI and crates.io.

**Sam:** Kiln it is. Config file should be kiln.toml in the repo root, not a dotfile, people never find dotfiles. Somebody needs to grab the GitHub org name but I don't know who yet.
