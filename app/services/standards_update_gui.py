from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from standards_update_checker import (
    DEFAULT_TARGETS,
    StandardTarget,
    StandardsUpdateChecker,
    format_text_report,
    load_targets_from_file,
)


class StandardsUpdateApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ISO/NORSOK Update Checker")
        self.root.geometry("1100x700")

        self.rows: list[dict[str, tk.Entry]] = []

        self._build_ui()
        self.load_targets(DEFAULT_TARGETS)

    def _build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=10)
        controls.pack(fill="x")

        ttk.Button(controls, text="Legg til rad", command=self.add_row).pack(side="left", padx=4)
        ttk.Button(controls, text="Fjern siste rad", command=self.remove_last_row).pack(side="left", padx=4)
        ttk.Button(controls, text="Last inn JSON", command=self.open_targets_file).pack(side="left", padx=4)
        ttk.Button(controls, text="Lagre JSON", command=self.save_targets_file).pack(side="left", padx=4)
        ttk.Button(controls, text="Køyr sjekk", command=self.run_check).pack(side="left", padx=12)

        self.status_var = tk.StringVar(value="Klar")
        ttk.Label(controls, textvariable=self.status_var).pack(side="right")

        table_wrap = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        table_wrap.pack(fill="both", expand=False)

        self.table = ttk.Frame(table_wrap)
        self.table.pack(fill="x")

        headers = ["Standardkode", "Kjelde", "Søke-URL", "Merknad"]
        for col, header in enumerate(headers):
            ttk.Label(self.table, text=header).grid(row=0, column=col, padx=4, pady=2, sticky="w")

        self.table.columnconfigure(0, weight=1)
        self.table.columnconfigure(1, weight=1)
        self.table.columnconfigure(2, weight=3)
        self.table.columnconfigure(3, weight=2)

        result_wrap = ttk.Frame(self.root, padding=10)
        result_wrap.pack(fill="both", expand=True)

        ttk.Label(result_wrap, text="Resultat").pack(anchor="w")

        self.output = tk.Text(result_wrap, wrap="word", height=20)
        self.output.pack(fill="both", expand=True)

    def add_row(self, target: StandardTarget | None = None) -> None:
        row_idx = len(self.rows) + 1

        code_entry = ttk.Entry(self.table)
        source_entry = ttk.Entry(self.table)
        url_entry = ttk.Entry(self.table)
        note_entry = ttk.Entry(self.table)

        code_entry.grid(row=row_idx, column=0, padx=4, pady=2, sticky="ew")
        source_entry.grid(row=row_idx, column=1, padx=4, pady=2, sticky="ew")
        url_entry.grid(row=row_idx, column=2, padx=4, pady=2, sticky="ew")
        note_entry.grid(row=row_idx, column=3, padx=4, pady=2, sticky="ew")

        if target:
            code_entry.insert(0, target.code)
            source_entry.insert(0, target.source)
            url_entry.insert(0, target.search_url)
            note_entry.insert(0, target.note)

        self.rows.append(
            {
                "code": code_entry,
                "source": source_entry,
                "search_url": url_entry,
                "note": note_entry,
            }
        )

    def remove_last_row(self) -> None:
        if not self.rows:
            return
        last = self.rows.pop()
        for widget in last.values():
            widget.destroy()

    def clear_rows(self) -> None:
        while self.rows:
            self.remove_last_row()

    def load_targets(self, targets: list[StandardTarget]) -> None:
        self.clear_rows()
        for target in targets:
            self.add_row(target)

    def get_targets_from_ui(self) -> list[StandardTarget]:
        targets: list[StandardTarget] = []
        for idx, row in enumerate(self.rows, start=1):
            code = row["code"].get().strip()
            source = row["source"].get().strip()
            search_url = row["search_url"].get().strip()
            note = row["note"].get().strip()

            if not code and not source and not search_url and not note:
                continue
            if not code or not source or not search_url:
                raise ValueError(f"Rad {idx}: code, source og search_url må fyllast ut.")

            targets.append(StandardTarget(code=code, source=source, search_url=search_url, note=note))

        if not targets:
            raise ValueError("Ingen gyldige standardar i lista.")

        return targets

    def open_targets_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Vel JSON-fil",
            filetypes=[("JSON filer", "*.json"), ("Alle filer", "*.*")],
        )
        if not path:
            return

        try:
            targets = load_targets_from_file(path)
            self.load_targets(targets)
            self.status_var.set(f"Lasta {len(targets)} standardar frå {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Feil", f"Klarte ikkje laste fil:\n{exc}")

    def save_targets_file(self) -> None:
        try:
            targets = self.get_targets_from_ui()
        except ValueError as exc:
            messagebox.showerror("Ugyldig input", str(exc))
            return

        path = filedialog.asksaveasfilename(
            title="Lagre JSON-fil",
            defaultextension=".json",
            filetypes=[("JSON filer", "*.json"), ("Alle filer", "*.*")],
        )
        if not path:
            return

        payload = [
            {
                "code": item.code,
                "source": item.source,
                "search_url": item.search_url,
                "note": item.note,
            }
            for item in targets
        ]

        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

        self.status_var.set(f"Lagra {len(payload)} standardar til {Path(path).name}")

    def run_check(self) -> None:
        try:
            targets = self.get_targets_from_ui()
        except ValueError as exc:
            messagebox.showerror("Ugyldig input", str(exc))
            return

        self.status_var.set("Køyrer sjekk...")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Hentar data frå kjelder...\n")

        thread = threading.Thread(target=self._run_check_background, args=(targets,), daemon=True)
        thread.start()

    def _run_check_background(self, targets: list[StandardTarget]) -> None:
        checker = StandardsUpdateChecker()
        results = checker.check_targets(targets)
        report = format_text_report(results)

        def update_ui() -> None:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, report)
            self.status_var.set(f"Ferdig: {len(results)} standardar sjekka")

        self.root.after(0, update_ui)


def main() -> None:
    root = tk.Tk()
    app = StandardsUpdateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
