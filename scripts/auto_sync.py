#!/usr/bin/env python3
"""
AUTO SYNC DE INSTRUMENTOS
Ejecuta sync automático de forma periódica o por detección de cambios en carpeta.
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from sync_instruments import InstrumentSyncer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scripts/sync.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AutoSyncRunner:
    """Runner de sincronización automática."""

    def __init__(self, workspace_root: Path, expected_fotos: int):
        self.workspace_root = workspace_root
        self.photos_dir = workspace_root / "public" / "images" / "instrumentos"
        self.syncer = InstrumentSyncer(str(workspace_root), expected_fotos=expected_fotos)
        self._last_seen_hash = None

    def _current_folder_hash(self) -> str:
        names = sorted([p.stem for p in self.photos_dir.glob("*.webp")]) if self.photos_dir.exists() else []
        return self.syncer.calculate_files_hash(names)

    def run_sync(self, force: bool = False, reason: str = "manual") -> dict:
        """Ejecuta una sincronización y entrega un resumen estructurado."""
        logger.info("=" * 72)
        logger.info("🔄 AUTO SYNC (%s)", reason)
        logger.info("=" * 72)
        rc = self.syncer.run(force_sync=force)

        payload = {
            "success": rc == 0,
            "force": force,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "return_code": rc,
        }

        if self.syncer.json_path.exists():
            try:
                data = json.loads(self.syncer.json_path.read_text(encoding="utf-8"))
                payload["total_instruments"] = data.get("total_instruments")
                payload["total_fotos"] = data.get("total_fotos")
                payload["validacion"] = data.get("validacion", {})
            except Exception as exc:
                payload["json_read_error"] = str(exc)

        logger.info("Resultado auto-sync: %s", payload)
        return payload

    def run_once(self, force: bool = False) -> dict:
        """Ejecuta una sola vez."""
        return self.run_sync(force=force, reason="once")

    def run_daemon(self, interval_minutes: int, force_first_run: bool = False, max_runs: int = 0) -> int:
        """Sincroniza cada N minutos (varias veces al día)."""
        interval_seconds = max(60, interval_minutes * 60)
        logger.info("🕒 Modo daemon activo. Intervalo: %s minutos", interval_minutes)

        run_count = 0
        self.run_sync(force=force_first_run, reason="daemon-start")
        run_count += 1
        if max_runs > 0 and run_count >= max_runs:
            return 0

        while True:
            logger.info("⏳ Esperando %s segundos para próximo ciclo...", interval_seconds)
            time.sleep(interval_seconds)
            self.run_sync(force=False, reason="daemon-interval")
            run_count += 1
            if max_runs > 0 and run_count >= max_runs:
                logger.info("🏁 max_runs alcanzado (%s). Finalizando.", max_runs)
                return 0

    def run_watch(self, watch_seconds: int, force_first_run: bool = False, max_runs: int = 0) -> int:
        """Sincroniza cuando detecta cambios de archivos en carpeta."""
        interval_seconds = max(5, watch_seconds)
        logger.info("👀 Modo watch activo. Poll cada %s segundos", interval_seconds)

        self._last_seen_hash = self._current_folder_hash()
        run_count = 0
        self.run_sync(force=force_first_run, reason="watch-start")
        run_count += 1
        if max_runs > 0 and run_count >= max_runs:
            return 0

        while True:
            time.sleep(interval_seconds)
            current_hash = self._current_folder_hash()
            if current_hash != self._last_seen_hash:
                logger.info("📸 Cambio detectado en carpeta. Ejecutando sincronización...")
                self.run_sync(force=False, reason="watch-change-detected")
                self._last_seen_hash = current_hash
                run_count += 1
                if max_runs > 0 and run_count >= max_runs:
                    logger.info("🏁 max_runs alcanzado (%s). Finalizando.", max_runs)
                    return 0
            else:
                logger.info("Sin cambios en carpeta de fotos.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto sync de instrumentos")
    parser.add_argument("--force", action="store_true", help="Forzar sync en primera ejecución")
    parser.add_argument("--once", action="store_true", help="Ejecutar una sola vez")
    parser.add_argument("--watch", action="store_true", help="Modo watch por cambios en carpeta")
    parser.add_argument("--daemon", action="store_true", help="Modo periódico cada N minutos")
    parser.add_argument("--watch-seconds", type=int, default=30, help="Polling de watch (segundos)")
    parser.add_argument("--interval-minutes", type=int, default=360, help="Intervalo modo daemon (minutos)")
    parser.add_argument("--expected-fotos", type=int, default=249, help="Conteo esperado base para validación")
    parser.add_argument("--max-runs", type=int, default=0, help="Limitar ciclos (0 = infinito)")
    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent
    runner = AutoSyncRunner(workspace_root=workspace_root, expected_fotos=args.expected_fotos)

    try:
        if args.watch:
            return runner.run_watch(
                watch_seconds=args.watch_seconds,
                force_first_run=args.force,
                max_runs=args.max_runs,
            )
        if args.daemon:
            return runner.run_daemon(
                interval_minutes=args.interval_minutes,
                force_first_run=args.force,
                max_runs=args.max_runs,
            )

        # default: once
        runner.run_once(force=args.force)
        return 0
    except KeyboardInterrupt:
        logger.info("🛑 Auto-sync detenido por usuario")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
