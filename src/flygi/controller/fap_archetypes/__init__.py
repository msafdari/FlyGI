"""Per-game FAP archetypes: parsers and planners derived from measured rules.

Each module in this package implements ONE archetype decoded in the
2026-09-28 extension sweeps (docs/fap_extension_20260928/). The contract
mirrors the built-in archetypes in flygi.controller.fap_library:

  class SomethingArchetype:
      name: str                                   # short slug
      def reset(self) -> None                     # clear per-life state
      def match(self, grid) -> parse | None       # abstain with None
      def next_actions(self, parse, grid) -> list[Step]

Rules of the package, per the first principle and the hidden-set lesson:
parsers derive everything from the CURRENT grid; grammar constants measured
in the dossiers (colours, pitches, tile sizes) are allowed, board-instance
data (absolute coordinates, level layouts, action scripts) is not. A module
that cannot parse a board abstains; the executor's guards bound any harm.
Registration into FapExecutor's default list happens in fap_library, not
here.
"""
