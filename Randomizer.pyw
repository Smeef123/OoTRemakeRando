"""OoT Remake Randomizer window: Ship of Harkinian's randomizer menu (its own tabs, sections, options, descriptions and
tricks, read from build/soh_options.json) with Generate, which runs rando.py and installs the seed into Hookshot.
Double-click to open. Your choices are kept in settings/ui_settings.json."""
import json, os, random, subprocess, sys, threading, tkinter as tk
from tkinter import ttk, filedialog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from remake_settings import FORCED, ALLOWED  # noqa: E402
import paths  # noqa: E402

OPTS = json.load(open(paths.OPTIONS, encoding='utf-8'))
SAVE = os.path.join(HERE, 'settings', 'ui_settings.json')
HOOKSHOT_MODS = paths.MODS  # the folder Play.pyw gives the game
PY = sys.executable.replace('pythonw.exe', 'python.exe')


def load_saved():
    try:
        return json.load(open(SAVE, encoding='utf-8'))
    except Exception:
        return {}


class Tip:
    """Option description shown on hover, like SoH's (?) markers."""
    def __init__(self, w, text):
        self.w, self.text, self.top = w, text, None
        w.bind('<Enter>', self.show); w.bind('<Leave>', self.hide)

    def show(self, _):
        if not self.text: return
        self.top = tk.Toplevel(self.w); self.top.wm_overrideredirect(True)
        self.top.geometry(f'+{self.w.winfo_rootx() + 20}+{self.w.winfo_rooty() + 24}')
        tk.Label(self.top, text=self.text, justify='left', wraplength=420, bg='#ffffe0', relief='solid',
                 borderwidth=1, padx=6, pady=4).pack()

    def hide(self, _):
        if self.top: self.top.destroy(); self.top = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('OoT Remake Randomizer (Ship of Harkinian)')
        self.geometry('1180x760')
        saved = load_saved()
        self.values = {}  # cvar -> StringVar holding the choice text
        self.choices = {}  # cvar -> list of choice texts
        # MQ-only tricks are left out: the remake has no Master Quest dungeons
        self.trick_info = {t['key']: t for t in OPTS['tricks'] if not t.get('mq')}
        self.tricks = {k: tk.BooleanVar(value=k in saved.get('tricks', [])) for k in self.trick_info}
        self.build_top(saved)
        nb = ttk.Notebook(self); nb.pack(fill='both', expand=True, padx=6, pady=4)
        # only what the remake can do: SoH options it can't follow are left out (rando.py holds them at the normal
        # game's value); SoH's tricks are N64 techniques, so there is no Tricks tab
        for tab in OPTS['tabs']:
            if any(o['cvar'] not in FORCED for o in self.all_options(tab)):
                nb.add(self.build_tab(nb, tab, saved.get('settings', {})), text=tab['name'])
        self.tricks = {}
        self.log = tk.Text(self, height=7, state='disabled', bg='#1e1e1e', fg='#d0d0d0')
        self.log.pack(fill='x', padx=6, pady=(0, 6))
        self.say("Ship of Harkinian's randomizer settings, limited to what works in the remake.")

    # ---- top bar: seed, generate, spoiler
    def build_top(self, saved):
        f = ttk.Frame(self); f.pack(fill='x', padx=6, pady=6)
        ttk.Label(f, text='Seed').pack(side='left')
        self.seed = tk.StringVar(value=saved.get('seed', ''))
        ttk.Entry(f, textvariable=self.seed, width=24).pack(side='left', padx=4)
        ttk.Button(f, text='Random', command=lambda: self.seed.set(str(random.randrange(10 ** 9, 10 ** 10)))).pack(side='left')
        self.gen_btn = ttk.Button(f, text='Generate and install', command=self.generate)
        self.gen_btn.pack(side='left', padx=12)
        ttk.Button(f, text='Open spoiler log', command=self.open_spoiler).pack(side='left')
        ttk.Button(f, text='Reset to defaults', command=self.reset).pack(side='left', padx=12)
        ttk.Label(f, text='Install to').pack(side='left', padx=(12, 2))
        self.mods = tk.StringVar(value=saved.get('mods', HOOKSHOT_MODS))
        ttk.Entry(f, textvariable=self.mods, width=40).pack(side='left')
        ttk.Button(f, text='...', width=3, command=lambda: self.mods.set(filedialog.askdirectory() or self.mods.get())).pack(side='left')

    # ---- a SoH sidebar tab: columns of sections of options, scrollable
    def build_tab(self, parent, tab, saved):
        outer = ttk.Frame(parent)
        canvas = tk.Canvas(outer, highlightthickness=0); sb = ttk.Scrollbar(outer, command=canvas.yview)
        inner = ttk.Frame(canvas); canvas.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True); sb.pack(side='right', fill='y')
        canvas.bind_all('<MouseWheel>', lambda e: self.focus_canvas(e).yview_scroll(-e.delta // 120, 'units'))
        col = 0
        for column in tab.get('groups', []):
            sections = [s for s in column.get('groups', [column])
                        if any(o['cvar'] not in FORCED for o in s.get('options', []))]
            if not sections: continue
            cf = ttk.Frame(inner); cf.grid(row=0, column=col, sticky='n', padx=6); col += 1
            for section in sections:
                lf = ttk.LabelFrame(cf, text=section['name']); lf.pack(fill='x', pady=4)
                for r, o in enumerate(o for o in section['options'] if o['cvar'] not in FORCED):
                    self.add_option(lf, r, o, saved)
        return outer

    def all_options(self, g):
        return g.get('options', []) + [o for s in g.get('groups', []) for o in self.all_options(s)]

    def focus_canvas(self, e):
        w = e.widget
        while w is not None and not isinstance(w, tk.Canvas):
            w = getattr(w, 'master', None)
        return w if w is not None else tk.Canvas(self)

    def add_option(self, frame, row, o, saved):
        cvar, choices = o['cvar'], o.get('choices') or ['Off', 'On']
        self.choices[cvar] = choices
        forced = cvar in FORCED
        idx = FORCED[cvar] if forced else saved.get(cvar, o['default'])
        idx = min(max(int(idx), 0), len(choices) - 1)
        shown = [choices[i] for i in ALLOWED[cvar]] if cvar in ALLOWED else choices
        if choices[idx] not in shown: idx = choices.index(shown[0])
        var = tk.StringVar(value=choices[idx]); self.values[cvar] = var
        lab = ttk.Label(frame, text=o['name'])
        lab.grid(row=row, column=0, sticky='w', padx=4, pady=1)
        box = ttk.Combobox(frame, textvariable=var, values=shown, state='disabled' if forced else 'readonly',
                           width=max(14, min(28, max(len(c) for c in choices) + 2)))
        box.grid(row=row, column=1, sticky='e', padx=4, pady=1)
        Tip(lab, o.get('description', '')); Tip(box, o.get('description', ''))
        self.defaults = getattr(self, 'defaults', {}); self.defaults[cvar] = o['default']

    # ---- tricks: filterable checklist, like SoH's Tricks tab
    def build_tricks(self, parent):
        f = ttk.Frame(parent)
        top = ttk.Frame(f); top.pack(fill='x', pady=4)
        ttk.Label(top, text='Filter').pack(side='left', padx=4)
        flt = tk.StringVar(); ttk.Entry(top, textvariable=flt, width=40).pack(side='left')
        ttk.Button(top, text='None', command=lambda: [v.set(False) for v in self.tricks.values()]).pack(side='left', padx=8)
        canvas = tk.Canvas(f, highlightthickness=0); sb = ttk.Scrollbar(f, command=canvas.yview)
        inner = ttk.Frame(canvas); canvas.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True); sb.pack(side='right', fill='y')
        boxes = {}
        for k, v in sorted(self.tricks.items(), key=lambda kv: self.trick_info[kv[0]]['name']):
            boxes[k] = ttk.Checkbutton(inner, text=self.trick_info[k]['name'], variable=v)
            Tip(boxes[k], self.trick_info[k]['description'])

        def refresh(*_):
            q = flt.get().lower()
            for b in boxes.values(): b.pack_forget()
            for k, b in boxes.items():
                if q in self.trick_info[k]['name'].lower(): b.pack(anchor='w', padx=6)
        flt.trace_add('write', refresh); refresh()
        return f

    # ---- actions
    def settings_json(self):
        out = {}
        for cvar, var in self.values.items():
            i = self.choices[cvar].index(var.get())
            if cvar in FORCED or i != self.defaults[cvar]:
                out[cvar] = i
        tricks = [t for t, v in self.tricks.items() if v.get()]
        if tricks: out['gRandoSettings.EnabledTricks'] = ','.join(tricks)
        return out, tricks

    def save(self):
        s, tricks = self.settings_json()
        os.makedirs(os.path.dirname(SAVE), exist_ok=True)
        json.dump({'settings': s, 'tricks': tricks, 'seed': self.seed.get(), 'mods': self.mods.get()},
                  open(SAVE, 'w', encoding='utf-8'), indent=1)

    def reset(self):
        for cvar, var in self.values.items():
            if cvar not in FORCED: var.set(self.choices[cvar][self.defaults[cvar]])
        for v in self.tricks.values(): v.set(False)
        self.say('Back to Ship of Harkinian\'s defaults.')

    def say(self, text):
        self.log.configure(state='normal'); self.log.insert('end', text + '\n'); self.log.see('end')
        self.log.configure(state='disabled')

    def generate(self):
        self.save()
        s, _ = self.settings_json()
        cfg = os.path.join(HERE, 'settings', 'ui_last_run.json')
        json.dump(s, open(cfg, 'w', encoding='utf-8'), indent=1)
        args = [PY, '-I', os.path.join(HERE, 'rando.py'), cfg, '--mods', self.mods.get()]
        if self.seed.get().strip(): args += ['--seed', self.seed.get().strip()]
        self.gen_btn.configure(state='disabled'); self.say('Generating...')

        def run():
            r = subprocess.run(args, capture_output=True, text=True, creationflags=0x08000000)
            lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
            self.result = (r.returncode, lines)
        self.result = None
        threading.Thread(target=run, daemon=True).start()
        self.poll()

    def poll(self):  # tkinter calls must stay on the window's own thread
        if self.result is None:
            self.after(200, self.poll)
        else:
            self.done(*self.result)

    def done(self, code, lines):
        for l in lines[-12:]: self.say(l)
        self.say('Done: start a NEW game in Hookshot to play this seed.' if code == 0 else 'Failed (see above).')
        self.gen_btn.configure(state='normal')
        for l in lines:
            if l.startswith('seed ') and ':' in l:
                self.last_seed = l.split()[1].rstrip(':')

    def open_spoiler(self):
        seed = getattr(self, 'last_seed', None) or self.seed.get().strip()
        d = os.path.join(HERE, 'seeds', seed, 'Randomizer')
        if seed and os.path.isdir(d):
            os.startfile(max((os.path.join(d, f) for f in os.listdir(d)), key=os.path.getmtime))
        else:
            self.say('No spoiler log for that seed yet.')


if __name__ == '__main__':
    App().mainloop()
