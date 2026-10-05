#!/usr/bin/env python3
from __future__ import annotations

import copy
import curses
import os
import shutil
import subprocess
import textwrap
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
IMAGE_CANDIDATES = (
    APP_DIR / "anacleto_classic.png",
    APP_DIR / "anacleto.png",
    APP_DIR / "anacleto_hero.png",
    APP_DIR / "anacleto_tui_hero.png",
)

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


@dataclass
class TUIState:
    status: str = "STANDBY"
    mission_id: str = "---"
    objective: str = ""
    phase: str = "Sistema en reposo. Esperando directiva..."
    result: str = ""
    error: str = ""
    history: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    running: bool = False
    spinner_idx: int = 0
    scroll_offset: int = 0  # Control de scroll para respuestas largas


def _short(value: Any, limit: int = 15000) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[:limit] + "\n[... truncado por límite de buffer ...]"


def _event(state: TUIState, text: str) -> None:
    state.events.append(f"[{time.strftime('%H:%M:%S')}] {text}")
    state.events = state.events[-100:]


def get_capabilities() -> list[str]:
    try:
        from sovereign_agent.tools import registry
        return registry.names()
    except Exception:
        return []


def run_mission(state: TUIState, runtime, objective: str, refresh) -> None:
    try:
        state.running = True
        state.status = "INITIALIZING"
        state.phase = "Acoplando motor Gemma 4 al clúster 3x RTX 3060"
        _event(state, "Runtime soberano persistente activo.")
        refresh()

        _event(state, "Runtime soberano conectado con éxito.")
        
        state.status = "SUBMITTING"
        state.phase = "Enrutando misión a través de CODEX"
        _event(state, "Despachando directiva a la pasarela.")
        refresh()

        mission = runtime.gateway.submit_mission(
            title="SOVEREIGN TUI E2E",
            objective=objective,
        )

        state.mission_id = str(mission.get("mission_id", "CODEX-UNKNOWN"))
        state.status = "EXECUTING"
        state.phase = "Factory → SovereignAgent → ToolExecutor"
        state.history.insert(0, f"{time.strftime('%H:%M:%S')}  {state.mission_id}")
        _event(state, f"Misión registrada: {state.mission_id}")
        refresh()

        conversation_context = [
            copy.deepcopy(message)
            for message in runtime.agent.context.get_messages()
        ]

        roles = [
            str(message.get("role", "?"))
            for message in conversation_context
        ]

        _event(
            state,
            f"Contexto conversacional acoplado: "
            f"{len(conversation_context)} mensajes.",
        )

        _event(
            state,
            f"Context roles: {roles}",
        )

        for index, message in enumerate(
            conversation_context,
            start=1,
        ):
            content = str(message.get("content") or "")
            preview = " ".join(content.split())[:120]

            _event(
                state,
                f"CTX[{index}] {message.get('role')}: {preview}",
            )
        refresh()

        result = runtime.gateway.run_mission(
            state.mission_id,
            conversation_context=conversation_context,
        )

        state.status = str(result.get("status", "COMPLETED"))
        state.phase = "Misión ejecutada con éxito"
        mission_result = result.get("result") or {}

        if isinstance(mission_result, dict):
            state.result = _short(
                mission_result.get("result")
                or mission_result.get("error")
                or result
            )
            state.error = str(mission_result.get("error") or "")
        else:
            state.result = _short(mission_result)
            state.error = ""

        if not result.get("ok", False):
            state.status = "ERROR"
            state.error = _short(result.get("error") or state.error)
            _event(state, f"Fallo en misión: {state.error}")
        else:
            if state.result:
                runtime.agent.context.add_assistant_message(
                    state.result
                )

            _event(
                state,
                "Respuesta incorporada al contexto conversacional.",
            )
            _event(state, "Verificación completada con éxito.")
            state.scroll_offset = 0  # Reiniciar scroll al recibir nueva respuesta

    except Exception as exc:
        state.status = "ERROR"
        state.phase = "Excepción en pipeline"
        state.error = f"{type(exc).__name__}: {exc}"
        _event(state, f"ERROR: {state.error}")
    finally:
        state.running = False
        refresh()


def draw_cyber_box(stdscr, y: int, x: int, h: int, w: int, title: str, color: int = 1) -> None:
    if h < 3 or w < 4:
        return
    try:
        attr = curses.color_pair(color) | curses.A_BOLD
        stdscr.attron(attr)
        stdscr.addstr(y, x, "╔" + "═" * (w - 2) + "╗")
        for row in range(1, h - 1):
            stdscr.addstr(y + row, x, "║")
            stdscr.addstr(y + row, x + w - 1, "║")
        stdscr.addstr(y + h - 1, x, "╚" + "═" * (w - 2) + "╝")
        
        label = f"┤ {title} ├"
        stdscr.addstr(y, x + 3, label)
        stdscr.attroff(attr)
    except curses.error:
        pass


def draw_wrapped(stdscr, y: int, x: int, width: int, text: str, max_lines: int, attr=0) -> int:
    """Dibuja texto ajustado sin scroll (para fases y títulos cortos)."""
    if width <= 0 or max_lines <= 0:
        return 0
    lines: list[str] = []
    for paragraph in str(text or "").splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width=max(10, width)) or [""])
    for i, line in enumerate(lines[:max_lines]):
        try:
            stdscr.addstr(y + i, x, line[:width], attr)
        except curses.error:
            pass
    return min(len(lines), max_lines)


def draw_scroller(stdscr, y: int, x: int, width: int, height: int, text: str, offset: int, attr=0) -> int:
    """Dibuja texto con soporte de desplazamiento vertical (scroll)."""
    if width <= 0 or height <= 0:
        return 0
    
    lines: list[str] = []
    for paragraph in str(text or "").splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width=max(10, width)) or [""])
    
    total_lines = len(lines)
    max_offset = max(0, total_lines - height)
    safe_offset = max(0, min(offset, max_offset))
    
    visible_lines = lines[safe_offset : safe_offset + height]
    
    for i, line in enumerate(visible_lines):
        try:
            stdscr.addstr(y + i, x, line[:width], attr)
        except curses.error:
            pass
            
    return max_offset


def _render_ascii_art(width: int, height: int) -> list[str]:
    art = [
        "    █████╗ ███╗   ██╗",
        "   ██╔══██╗████╗  ██║",
        "   ███████║██╔██╗ ██║  [ANACLETO]",
        "   ██╔══██║██║╚██╗██║  [AGENTE]",
        "   ██║  ██║██║ ╚████║  [SECRETO]",
        "   ╚═╝  ╚═╝╚═╝  ╚═══╝",
    ]
    return art[:height]


def _status_attr(status: str) -> int:
    if status == "ERROR":
        return curses.color_pair(4) | curses.A_BOLD
    if status in {"COMPLETED", "STANDBY"}:
        return curses.color_pair(2) | curses.A_BOLD
    if status in {"EXECUTING", "INITIALIZING", "SUBMITTING", "QUEUED"}:
        return curses.color_pair(3) | curses.A_BOLD
    return curses.A_BOLD


def main(stdscr) -> None:
    curses.curs_set(1)
    stdscr.timeout(100)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    from sovereign_agent.composition import create_anacleto_gemma_runtime

    state = TUIState()
    objective = ""
    worker = None
    capabilities = get_capabilities()

    # Runtime soberano persistente durante toda la sesión TUI.
    # Esto permite conservar la conversación entre misiones
    # sin reutilizar los checkpoints internos de las misiones.
    runtime = create_anacleto_gemma_runtime()

    def refresh():
        try:
            stdscr.move(0, 0)
            stdscr.refresh()
        except curses.error:
            pass

    def safe_addstr(y, x, value, attr=0):
        height, width = stdscr.getmaxyx()

        if y < 0 or y >= height or x >= width:
            return

        value = str(value)
        available = max(0, width - x - 1)

        if available <= 0:
            return

        try:
            stdscr.addnstr(
                y,
                x,
                value,
                available,
                attr,
            )
        except curses.error:
            pass

    def draw():
        height, width = stdscr.getmaxyx()

        stdscr.erase()

        if height < 22 or width < 80:
            safe_addstr(
                0,
                0,
                f"Terminal demasiado pequeño: mínimo 80x22 · actual {width}x{height}",
                curses.color_pair(3) | curses.A_BOLD,
            )
            refresh()
            return

        # ====================================================
        # HEADER
        # ====================================================

        # ====================================================
        # SOVEREIGN IDENTITY
        # ====================================================

        sovereign_logo = [
            "███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗",
            "██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║",
            "███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██║  ███╗██╔██╗ ██║",
            "╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║",
            "███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║╚██████╔╝██║ ╚████║",
            "╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
        ]

        logo_y = 1

        for i, line in enumerate(sovereign_logo):
            if logo_y + i >= height - 1:
                break

            safe_addstr(
                logo_y + i,
                2,
                line[:max(0, width - 4)],
                curses.color_pair(1) | curses.A_BOLD,
            )

        # El logo ocupa deliberadamente todo el ancho disponible.
        # El modelo se muestra debajo del logo para evitar solapamientos.
        model_y = logo_y + len(sovereign_logo)

        safe_addstr(
            model_y,
            max(2, width - 29),
            "GEMMA 4 · 26B",
            curses.color_pair(5),
        )

        header_divider_y = model_y + 1

        safe_addstr(
            header_divider_y,
            2,
            "─" * max(1, width - 4),
            curses.color_pair(1),
        )

        # ====================================================
        # REGISTRY
        # ====================================================

        registry_y = header_divider_y + 1

        safe_addstr(
            registry_y,
            2,
            "REGISTRY",
            curses.color_pair(3) | curses.A_BOLD,
        )

        registry_line = (
            f"{len(capabilities)} tools · "
            "262K native · "
            "llama-server :18080"
        )

        safe_addstr(
            registry_y,
            12,
            registry_line,
            curses.color_pair(5),
        )

        safe_addstr(
            registry_y + 1,
            2,
            "─" * max(1, width - 4),
            curses.color_pair(1),
        )

        # ====================================================
        # CAPABILITIES
        # ====================================================

        capabilities_y = registry_y + 2

        safe_addstr(
            capabilities_y,
            2,
            "CAPABILITIES / SKILLS",
            curses.color_pair(6) | curses.A_BOLD,
        )

        skills = " · ".join(capabilities)

        skill_lines = textwrap.wrap(
            skills if skills else "registry unavailable",
            width=max(20, width - 4),
        )

        for i, line in enumerate(skill_lines[:4]):
            safe_addstr(
                capabilities_y + 1 + i,
                2,
                line,
                curses.color_pair(6),
            )

        capabilities_end = (
            capabilities_y
            + 1
            + max(1, min(4, len(skill_lines)))
        )

        safe_addstr(
            capabilities_end,
            2,
            "─" * max(1, width - 4),
            curses.color_pair(6),
        )

        # ====================================================
        # COMPACT STATUS
        # ====================================================

        status_y = capabilities_end + 1

        status_attr = (
            curses.color_pair(4) | curses.A_BOLD
            if state.status == "ERROR"
            else curses.color_pair(2) | curses.A_BOLD
        )

        safe_addstr(
            status_y,
            2,
            "STATUS",
            curses.color_pair(3) | curses.A_BOLD,
        )

        safe_addstr(
            status_y,
            10,
            state.status,
            status_attr,
        )

        safe_addstr(
            status_y,
            23,
            f"MISSION {state.mission_id}",
            curses.color_pair(5),
        )

        safe_addstr(
            status_y + 1,
            2,
            "PHASE",
            curses.color_pair(3) | curses.A_BOLD,
        )

        phase = state.phase or "Sistema en reposo"

        phase_lines = textwrap.wrap(
            phase,
            width=max(20, width - 10),
        )

        safe_addstr(
            status_y + 1,
            9,
            phase_lines[0] if phase_lines else "",
            curses.color_pair(2),
        )

        safe_addstr(
            status_y + 2,
            2,
            "─" * max(1, width - 4),
            curses.color_pair(1),
        )

        # ====================================================
        # CONVERSATION
        # ====================================================

        conversation_top = status_y + 3
        prompt_y = height - 3

        conversation_height = max(
            3,
            prompt_y - conversation_top - 2,
        )

        content: list[str] = []

        # ----------------------------------------------------
        # TELEMETRÍA DE MISIONES
        # ----------------------------------------------------
        if state.history:
            for item in state.history:
                content.append(f"MISSION  {item}")

        # ----------------------------------------------------
        # CONVERSACIÓN REAL
        #
        # La fuente de verdad visual es el mismo contexto
        # persistente que se entrega a Gemma entre misiones.
        # Los mensajes de herramientas se omiten deliberadamente:
        # la TUI muestra conversación usuario <-> SOVEREIGN,
        # no el protocolo interno de ejecución.
        # ----------------------------------------------------
        conversation_messages = runtime.agent.context.get_messages()

        for message in conversation_messages:
            role = str(message.get("role", "")).lower()
            content_text = str(message.get("content") or "").strip()

            if not content_text:
                continue

            if role == "user":
                content.append("")
                for line in textwrap.wrap(
                    f"> {content_text}",
                    width=max(20, width - 6),
                ):
                    content.append(line)

            elif role == "assistant":
                content.append("")
                content.append("SOVEREIGN")

                content.extend(
                    textwrap.wrap(
                        content_text,
                        width=max(20, width - 6),
                    )
                )

        if state.error:
            content.append("")
            content.append(f"ERROR: {state.error}")

        if not content:
            content = [
                "",
                "Sistema preparado.",
                "Escribe una misión para comenzar.",
            ]

        max_scroll = max(
            0,
            len(content) - conversation_height,
        )

        offset = min(
            state.scroll_offset,
            max_scroll,
        )

        start_index = max(
            0,
            len(content) - conversation_height - offset,
        )

        visible = content[
            start_index:start_index + conversation_height
        ]

        # Render natural: la conversación comienza directamente
        # debajo del divisor y crece hacia abajo.
        render_start = conversation_top

        for i, line in enumerate(visible):
            attr = 0

            if line.startswith("> "):
                attr = curses.color_pair(1)

            elif line == "SOVEREIGN":
                attr = curses.color_pair(2) | curses.A_BOLD

            elif line.startswith("ERROR"):
                attr = curses.color_pair(4)

            elif line.startswith("MISSION"):
                attr = curses.color_pair(5)

            safe_addstr(
                render_start + i,
                2,
                line,
                attr,
            )

        # ====================================================
        # PROMPT
        # ====================================================

        safe_addstr(
            prompt_y,
            2,
            ">",
            curses.color_pair(1) | curses.A_BOLD,
        )

        safe_addstr(
            prompt_y,
            4,
            objective,
            curses.color_pair(1),
        )

        try:
            stdscr.move(
                prompt_y,
                min(
                    width - 2,
                    4 + len(objective),
                ),
            )
        except curses.error:
            pass

        safe_addstr(
            height - 2,
            2,
            "[ENTER] Ejecutar   [↑/↓] Scroll   [Ctrl+C] Salir",
            curses.color_pair(5),
        )

        refresh()

    while True:
        draw()

        if worker is not None and not worker.is_alive():
            worker = None

        try:
            key = stdscr.get_wch()
        except curses.error:
            continue

        if key == "\x03":
            return

        if key == curses.KEY_UP:
            state.scroll_offset = max(
                0,
                state.scroll_offset - 1,
            )
            continue

        if key == curses.KEY_DOWN:
            state.scroll_offset += 1
            continue

        if state.running:
            continue

        if key in ("\n", "\r"):
            mission = objective.strip()

            if not mission:
                continue

            state.objective = mission

            runtime.agent.context.add_user_message(mission)

            state.result = ""
            state.error = ""
            state.status = "QUEUED"
            state.phase = "Encolando tarea..."
            state.events = []
            state.scroll_offset = 0

            _event(
                state,
                f"Orden: '{state.objective}'",
            )

            refresh()

            worker = threading.Thread(
                target=run_mission,
                args=(
                    state,
                    runtime,
                    mission,
                    refresh,
                ),
                daemon=True,
            )

            worker.start()
            objective = ""

            # Rearmar explícitamente el modo de entrada después
            # de lanzar el worker. La conversación permanece en
            # runtime.agent.context; aquí solo recuperamos el input.
            try:
                curses.curs_set(1)
            except curses.error:
                pass

            refresh()
            continue

        if key in (
            curses.KEY_BACKSPACE,
            "\x7f",
            "\b",
        ):
            objective = objective[:-1]
            continue

        if isinstance(key, str) and key.isprintable():
            objective += key


if __name__ == "__main__":
    curses.wrapper(main)
