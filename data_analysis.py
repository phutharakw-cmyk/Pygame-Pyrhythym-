# data_analysis.py - Data Analysis Dashboard (English + All Sessions)
import os
import glob
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import DATA_DIR

class DataAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyrhythym - Data Analysis Dashboard")
        self.root.geometry("900x700")
        
        self.sessions = self._find_sessions()
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        
        self._create_widgets()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if not self.sessions:
            messagebox.showinfo("No Data", f"No gameplay data found in {DATA_DIR} folder")
        else:
            self.plot_graph()

    def _find_sessions(self):
        if not os.path.exists(DATA_DIR): 
            return []
        files = glob.glob(os.path.join(DATA_DIR, "*_score.csv"))
        return [os.path.basename(f).replace("_score.csv", "") for f in files]

    def _create_widgets(self):
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Select Session:").pack(side=tk.LEFT, padx=5)
        self.session_var = tk.StringVar()
        self.session_cb = ttk.Combobox(control_frame, textvariable=self.session_var, 
                                       values=self.sessions, width=40, state="readonly")
        self.session_cb.pack(side=tk.LEFT, padx=5)
        if self.sessions: 
            self.session_cb.current(len(self.sessions)-1)
        self.session_cb.bind("<<ComboboxSelected>>", self.plot_graph)

        ttk.Label(control_frame, text="Select Chart:").pack(side=tk.LEFT, padx=(20, 5))
        self.chart_var = tk.StringVar()
        
        self.charts = [
            "1. Score Progression (Bar Chart)",
            "2. Combo Progression (Line Chart)",
            "3. Judgement Summary (Table)",
            "4. Missed Note Types (Pie Chart) - All Sessions",
            "5. Reaction Time Distribution (Histogram)"
        ]
        self.chart_cb = ttk.Combobox(control_frame, textvariable=self.chart_var, 
                                     values=self.charts, width=40, state="readonly")
        self.chart_cb.pack(side=tk.LEFT, padx=5)
        self.chart_cb.current(0)
        self.chart_cb.bind("<<ComboboxSelected>>", self.plot_graph)

    def plot_graph(self, event=None):
        prefix = self.session_var.get()
        chart_type = self.chart_var.get()
        if not prefix: 
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        try:
            if "1." in chart_type:
                self._plot_score(ax, prefix)
            elif "2." in chart_type:
                self._plot_combo(ax, prefix)
            elif "3." in chart_type:
                self._plot_judgement(ax, prefix)
            elif "4." in chart_type:
                self._plot_missed_notes_pie(ax)
            elif "5." in chart_type:
                self._plot_reaction_hist(ax, prefix)
                
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            ax.text(0.5, 0.5, f"Error Loading Data:\n{e}", ha='center', va='center', 
                   color='red', fontsize=12)
            self.canvas.draw()

    def _plot_score(self, ax, prefix):
        """Score progression over time"""
        df = pd.read_csv(os.path.join(DATA_DIR, f"{prefix}_score.csv"))
        ax.bar(df['time'], df['score'], width=3.0, color='royalblue', alpha=0.8, edgecolor='black')
        ax.set_title("Score Progression", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time (Seconds)")
        ax.set_ylabel("Total Score")
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)

    def _plot_combo(self, ax, prefix):
        """Combo progression over time"""
        df = pd.read_csv(os.path.join(DATA_DIR, f"{prefix}_combo.csv"))
        ax.plot(df['time'], df['combo'], color='darkorange', linewidth=2, marker='.')
        ax.fill_between(df['time'], df['combo'], color='orange', alpha=0.3)
        ax.set_title("Combo Progression", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time (Seconds)")
        ax.set_ylabel("Combo Count")
        ax.grid(True, linestyle='--', alpha=0.6)

    def _plot_judgement(self, ax, prefix):
        """Judgement summary statistics"""
        df = pd.read_csv(os.path.join(DATA_DIR, f"{prefix}_hit.csv"))
        counts = df['result'].value_counts()
        ax.axis('tight')
        ax.axis('off')
        ax.set_title("Judgement Summary", fontsize=14, fontweight='bold', pad=20)
        
        cell_data = []
        total = 0
        for judge in ["PERFECT", "GOOD", "MISS"]:
            c = counts.get(judge, 0)
            total += c
            cell_data.append([judge, f"{c:,}"])
        cell_data.append(["TOTAL", f"{total:,}"])
        
        table = ax.table(cellText=cell_data, colLabels=["Judgement", "Count"], 
                         loc='center', cellLoc='center', colWidths=[0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1, 2.5)

    def _plot_missed_notes_pie(self, ax):
        """Pie chart of missed note types - from ALL sessions"""
        all_misses = []
        
        if not os.path.exists(DATA_DIR):
            ax.axis('off')
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', 
                   fontsize=16, color='red', fontweight='bold')
            ax.set_title("Missed Note Types (All Sessions)", fontsize=14, fontweight='bold')
            return
        
        hit_files = glob.glob(os.path.join(DATA_DIR, "*_hit.csv"))
        
        for hit_file in hit_files:
            try:
                df = pd.read_csv(hit_file)
                misses = df[df['result'] == 'MISS']
                if not misses.empty:
                    all_misses.append(misses)
            except:
                continue
        
        if not all_misses:
            ax.axis('off')
            ax.text(0.5, 0.5, "No missed notes in any session!\n(Full Combo / Perfect Play)", 
                   ha='center', va='center', fontsize=16, color='seagreen', fontweight='bold')
            ax.set_title("Missed Note Types (All Sessions)", fontsize=14, fontweight='bold')
        else:
            all_misses_df = pd.concat(all_misses, ignore_index=True)
            counts = all_misses_df['note_type'].value_counts()
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            ax.pie(counts, labels=[label.capitalize() for label in counts.index], 
                   autopct='%1.1f%%', startangle=140, colors=colors[:len(counts)], 
                   textprops={'fontsize': 12, 'fontweight': 'bold'},
                   wedgeprops={'edgecolor': 'black', 'linewidth': 1})
            ax.set_title("Missed Note Types (All Sessions)", fontsize=14, fontweight='bold')

    def _plot_reaction_hist(self, ax, prefix):
        """Reaction time distribution histogram"""
        df = pd.read_csv(os.path.join(DATA_DIR, f"{prefix}_reaction.csv"))
        
        max_val = df['reaction'].abs().max()
        limit = max(0.2, max_val + 0.05)
        
        ax.hist(df['reaction'], bins=20, range=(-limit, limit), 
               color='mediumpurple', edgecolor='black', alpha=0.8)
        
        ax.set_title("Reaction Time Distribution", fontsize=14, fontweight='bold')
        ax.set_xlabel("Reaction Delta (Seconds: Negative=Early, Positive=Late)")
        ax.set_ylabel("Frequency")
        ax.set_xlim(-limit, limit)
        
        ax.axvline(x=0, color='red', linestyle='dashed', linewidth=2.5)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)

def open_analysis_window():
    root = tk.Tk()
    app = DataAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    open_analysis_window()
