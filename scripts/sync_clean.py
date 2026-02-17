#!/usr/bin/env python3
"""
Wrapper de compatibilidad.
Usa el sincronizador principal para mantener un solo flujo de verdad.
"""

from pathlib import Path

from sync_instruments import InstrumentSyncer


def main() -> int:
    workspace_root = Path(__file__).parent.parent
    syncer = InstrumentSyncer(str(workspace_root))
    return syncer.run(force_sync=True)


if __name__ == "__main__":
    raise SystemExit(main())
