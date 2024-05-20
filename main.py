from GSanim import CustomAnim
from tkinter import *
from PIL import Image, ImageTk
from assets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from NormCanvas import NormCanvas
from copy import copy


def main():
    WIDTH, HEIGHT = 700, 700


    root = Tk()
    root.title("Laboratório Virtual de Máquinas Elétricas: Motor de Indução Trifásico")
    # root.geometry()
    # root.overrideredirect(True)

    gepai = ImageTk.PhotoImage(Image.open('./gepai.png'))
    Label(root, image=gepai, fg=cl['bg'], bg=cl['bg']).grid(row=0, column=0, rowspan=1, columnspan=2, stick=N+W)

    # ifsc = ImageTk.PhotoImage(Image.open('./ifsc.png'))
    # Label(root, image=ifsc, fg=cl['bg'], bg=cl['bg']).grid(row=0, column=0, rowspan=1, columnspan=1)

    widgets = {}
    widgets['fps'] = Label(root, text='fps:', font=fonts['fps'], fg='#D5DBDB', bg=cl['bg'])
    widgets['fps'].grid(row=0, column=16, stick=N+E)


    default = {'font': fonts['default'], 'bg': cl['bg'], 'fg': cl['default_font']}
    root.configure(bg=default['bg'])
    fig0, _ = plt.subplots(1, 1, figsize=(6.5, 3.5))
    fig1, _ = plt.subplots(1, 1, figsize=(6.5, 3.5))



    widgets['canvas_fig0'] = FigureCanvasTkAgg(fig0, master=root)
    widgets['canvas_fig1'] = FigureCanvasTkAgg(fig1, master=root)


    widgets['canvas_fig0'].get_tk_widget().grid(row=1, column=0 , columnspan=6)
    widgets['canvas_fig1'].get_tk_widget().grid(row=2, column=0 , columnspan=6)



    # control_frame = Frame(root)
    # control_frame.grid(row=3, column=0, rowspan=4, columnspan=3, sticky=E+S+N+W)
    control_frame = root
    row0, col0 = 3, 0
    default_check = {'bg': '#c4dad0'}
    Label(control_frame, text="stator", **default).grid(row=row0+0, column=col0+1)
    Label(control_frame, text="rotor", **default).grid(row=row0+0, column=col0+2)
    Label(control_frame, text="Field lines", **default).grid(row=row0+1, column=col0, sticky=E)
    Label(control_frame, text="Field vecs", **default).grid(row=row0+2, column=col0, sticky=E)
    Label(control_frame, text="Coil front", **default).grid(row=row0+3, column=col0, sticky=E)
    widgets['rotor_field_vec']    = Checkbutton(control_frame, **default_check)
    widgets['rotor_field_lines']  = Checkbutton(control_frame, **default_check)
    widgets['rotor_coil_front']   = Checkbutton(control_frame, **default_check)
    widgets['stator_field_vec']   = Checkbutton(control_frame, **default_check)
    widgets['stator_field_lines'] = Checkbutton(control_frame, **default_check)
    widgets['stator_coil_front']  = Checkbutton(control_frame, **default_check)
    widgets['rotor_field_vec']    .grid(row=row0 + 2, column=col0 + 2, stick=W+E+N+S, padx=1, pady=1)
    widgets['rotor_field_lines']  .grid(row=row0 + 1, column=col0 + 2, stick=W+E+N+S, padx=1, pady=1)
    widgets['rotor_coil_front']   .grid(row=row0 + 3, column=col0 + 2, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_field_vec']   .grid(row=row0 + 2, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_field_lines'] .grid(row=row0 + 1, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_coil_front']  .grid(row=row0 + 3, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)

    widgets['sim_inertia'] = Checkbutton(root, text='Newton 2nd', **default)
    widgets['sim_inertia'].grid(row=row0 + 2, column=col0 + 3)

    row0, col0 = 3, 4
    Label(control_frame, text="ref",    **default).grid(row=row0 + 0, column=col0+1)
    Label(control_frame, text="stator", **default).grid(row=row0 + 1, column=col0, sticky=E)
    Label(control_frame, text="rotor",  **default).grid(row=row0 + 2, column=col0, sticky=E)
    Label(control_frame, text="field",  **default).grid(row=row0 + 3, column=col0, sticky=E)

    widgets['ref_stator'] = Checkbutton(control_frame, **default_check)
    widgets['ref_rotor']  = Checkbutton(control_frame, **default_check)
    widgets['ref_field']  = Checkbutton(control_frame, **default_check)
    widgets['ref_stator'] .grid(row=row0 + 2, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)
    widgets['ref_rotor']  .grid(row=row0 + 1, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)
    widgets['ref_field']  .grid(row=row0 + 3, column=col0 + 1, stick=W+E+N+S, padx=1, pady=1)



    default_instruments = copy(default)
    default_instruments['bg'] = '#c8fcd4'
    row0, col0 = 3, 6
    canvas = NormCanvas(root, bg=cl['bg'], height=HEIGHT, width=WIDTH, highlightbackground=cl['bg'])
    canvas.grid(row=0, column=col0, columnspan=11, rowspan=5)
    Label(root, text="stator", **default_instruments).grid(row=row0 + 1, column=col0+0, stick=W+E+N+S)
    Label(root, text="rotor",  **default_instruments).grid(row=row0 + 1, column=col0+2, stick=W+E+N+S)
    Label(root, text="grid",   **default_instruments).grid(row=row0 + 1, column=col0+4, stick=W+E+N+S)
    Label(root, text="slip",   **default_instruments).grid(row=row0 + 1, column=col0+6, stick=W+E+N+S)
    Label(root, text="Pconv",  **default_instruments).grid(row=row0 + 1, column=col0+8, stick=W+E+N+S)
    Label(root, text="Tind",   **default_instruments).grid(row=row0 + 1, column=col0+10, stick=W+E+N+S)

    widgets['w_stator_um'] = Label(root, text="[rad/s]", **default_instruments)
    widgets['w_rotor_um']  = Label(root, text="[rpm]"  , **default_instruments)
    widgets['w_grid_um']   = Label(root, text="[Hz]"   , **default_instruments)
    widgets['slip_um']     = Label(root, text="[pu]"   , **default_instruments)
    widgets['Pconv_um']    = Label(root, text="[kW]"   , **default_instruments)
    widgets['Tind_um']     = Label(root, text="[Nm]"   , **default_instruments)

    widgets['w_stator_um'].grid(row=row0 + 2, column=col0+0, stick=W+E+N+S)
    widgets['w_rotor_um'] .grid(row=row0 + 2, column=col0+2, stick=W+E+N+S)
    widgets['w_grid_um']  .grid(row=row0 + 2, column=col0+4, stick=W+E+N+S)
    widgets['slip_um']    .grid(row=row0 + 2, column=col0+6, stick=W+E+N+S)
    widgets['Pconv_um']   .grid(row=row0 + 2, column=col0+8, stick=W+E+N+S)
    widgets['Tind_um']    .grid(row=row0 + 2, column=col0+10, stick=W+E+N+S)


    root.columnconfigure(col0+0, weight=3, minsize=90)
    root.columnconfigure(col0+2, weight=3, minsize=90)
    root.columnconfigure(col0+4, weight=3, minsize=90)
    root.columnconfigure(col0+6, weight=3, minsize=90)
    root.columnconfigure(col0+8, weight=3, minsize=90)
    root.columnconfigure(col0+0, weight=3, minsize=90)

    root.columnconfigure(col0+1, weight=0, minsize=1)
    root.columnconfigure(col0+3, weight=0, minsize=1)
    root.columnconfigure(col0+5, weight=0, minsize=1)
    root.columnconfigure(col0+7, weight=0, minsize=1)
    root.columnconfigure(col0+9, weight=0, minsize=1)
    root.columnconfigure(col0+1, weight=0, minsize=1)

    default_instruments = copy(default)
    default_instruments['bg'] = '#a8dcb4'
    widgets['w_stator'] = Label(root, text="", **default_instruments)
    widgets['w_rotor']  = Label(root, text="", **default_instruments)
    widgets['w_grid']   = Label(root, text="", **default_instruments)
    widgets['slip']     = Label(root, text="", **default_instruments)
    widgets['Pconv']    = Label(root, text="", **default_instruments)
    widgets['Tind']     = Label(root, text="", **default_instruments)

    widgets['w_stator'].grid(row=row0 + 3, column=col0+0, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['w_rotor'] .grid(row=row0 + 3, column=col0+2, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['w_grid']  .grid(row=row0 + 3, column=col0+4, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['slip']    .grid(row=row0 + 3, column=col0+6, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['Pconv']   .grid(row=row0 + 3, column=col0+8, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['Tind']    .grid(row=row0 + 3, column=col0+10, stick=W+E+N+S, ipadx=1, pady=1)









    widgets['time_factor'] = Label(root, text='...', **default)
    widgets['figs'] = (fig0, fig1)

    CustomAnim(canvas, widgets).loop()
    root.mainloop()


if __name__ == '__main__':
    main()