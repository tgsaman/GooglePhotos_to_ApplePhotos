import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from photo_metadata_patch import process_metadata_files, check_directory_writable


def check_environment():
    """Check for required dependencies and return an error message if missing."""
    errors = []
    if not shutil.which("exiftool"):
        errors.append("'exiftool' not found on PATH")
    if sys.version_info < (3, 8):
        errors.append("Python 3.8 or higher is required")
    return "\n".join(errors)


def run_process(root_dir, dry_run, workers, output):
    try:
        csv_path = process_metadata_files(
            root_dir, dry_run=dry_run, parallel_workers=workers, output_path=output
        )
        messagebox.showinfo("Done", f"Finished. CSV log at: {csv_path}")
    except SystemExit:
        # process_metadata_files may call sys.exit on error
        pass
    except Exception as e:
        messagebox.showerror("Error", str(e))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Google Photos Metadata Patcher")
        self.geometry("500x200")

        self.root_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.dry_run_var = tk.BooleanVar(value=False)
        self.workers_var = tk.IntVar(value=4)

        tk.Label(self, text="Google Photos Export Folder:").pack(anchor="w", padx=10, pady=5)
        frm1 = tk.Frame(self)
        frm1.pack(fill="x", padx=10)
        tk.Entry(frm1, textvariable=self.root_var, width=50).pack(side="left", expand=True, fill="x")
        tk.Button(frm1, text="Choose Folder...", command=self.browse_root).pack(side="left", padx=5)
        tk.Label(self, text="Output CSV (optional):").pack(anchor="w", padx=10, pady=5)
        frm2 = tk.Frame(self)
        frm2.pack(fill="x", padx=10)
        tk.Entry(frm2, textvariable=self.output_var, width=50).pack(side="left", expand=True, fill="x")
        tk.Button(frm2, text="Save CSV To...", command=self.browse_output).pack(side="left", padx=5)
        frm3 = tk.Frame(self)
        frm3.pack(fill="x", padx=10, pady=10)
        tk.Checkbutton(frm3, text="Dry Run", variable=self.dry_run_var).pack(side="left")
        tk.Label(frm3, text="Workers:").pack(side="left", padx=(20, 5))
        tk.Spinbox(frm3, from_=1, to=16, textvariable=self.workers_var, width=5).pack(side="left")

        tk.Button(self, text="Run", command=self.on_run).pack(pady=10)

    def browse_root(self):
        path = filedialog.askdirectory(title="Select Google Photos export root")
        if path:
            self.root_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(title="Select output CSV", defaultextension=".csv")
        if path:
            self.output_var.set(path)

    def on_run(self):
        root_dir = self.root_var.get()
        if not root_dir:
            messagebox.showerror("Error", "Please select the export folder")
            return
        if not check_directory_writable(root_dir):
            messagebox.showerror(
                "Error",
                "Cannot write to the selected folder. Close other apps that might lock the files.",
            )
            return
        error = check_environment()
        if error:
            messagebox.showerror("Missing Dependency", error)
            return
        run_process(
            root_dir,
            dry_run=self.dry_run_var.get(),
            workers=self.workers_var.get(),
            output=self.output_var.get() or None,
        )
        self.destroy()



if __name__ == "__main__":
    App().mainloop()
