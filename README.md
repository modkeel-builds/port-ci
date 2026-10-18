# port-ci

Builds and boots community ports of popular Minecraft mods for new Minecraft versions, on
GitHub's runners. When a Minecraft release comes out, many mods take weeks or months to update;
often a fork somewhere already has a branch for the new version. Each job here looks for one,
builds it and starts a dedicated server with it, using [Modkeel](https://github.com/Modkeel/modkeel)
(`pip install modkeel`), the same steps `modkeel get` runs on a player's PC.

| File | What it does |
|---|---|
| `candidates.py` | The most downloaded open source mods on Modrinth with no build for a version |
| `port_job.py` | One mod: find a build or a fork for the version, build it, boot a server, write `result.json` |
| `.github/workflows/port.yml` | Run by hand (Actions -> port -> Run workflow): pick the mods, one job each, a summary table |

## What it does not do

- Upload jars. Results name the source (fork, branch) and the jar's SHA-1, so anyone can build
  the same thing; publishing a port is a separate step that checks its licence and source.
- Test players' modpacks. Each run covers the mods picked for one Minecraft version and loader.
- Hold secrets. The mods' own Gradle builds run in these jobs, so the token they see can only
  read.

## Licence

MIT. The mods built here keep their own licences; only open source mods are picked.
