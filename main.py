from GSanim import CustomAnim
from tkinter import *
from assets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from NormCanvas import NormCanvas
from copy import copy


def main():
    WIDTH, HEIGHT = 700, 700


    root = Tk()
    root.title("Practice with Grid")
    # root.geometry()


    default = {'font': fonts['default'], 'bg': cl['bg'], 'fg': cl['default_font']}
    root.configure(bg=default['bg'])
    fig0, _ = plt.subplots(1, 1, figsize=(6.5, 3.5))
    fig1, _ = plt.subplots(1, 1, figsize=(6.5, 3.5))

    widgets = {}

    widgets['canvas_fig0'] = FigureCanvasTkAgg(fig0, master=root)
    widgets['canvas_fig1'] = FigureCanvasTkAgg(fig1, master=root)
    canvas = NormCanvas(root, bg=cl['bg'], height=HEIGHT, width=WIDTH, highlightbackground=cl['bg'])

    widgets['canvas_fig0'].get_tk_widget().grid(row=1, column=0 , columnspan=9)
    widgets['canvas_fig1'].get_tk_widget().grid(row=2, column=0 , columnspan=9)
    canvas                                .grid(row=0, column=10, columnspan=11, rowspan=5)


    row0 = 3
    Label(root, text="stator", **default).grid(row=row0+0, column=1)
    Label(root, text="rotor", **default).grid(row=row0+0, column=2)
    Label(root, text="Field vector", **default).grid(row=row0+1, column=0, sticky=E)
    Label(root, text="Field lines", **default).grid(row=row0+2, column=0, sticky=E)
    Label(root, text="Coil front", **default).grid(row=row0+3, column=0, sticky=E)

    default_check = {'bg': '#c4dad0', 'padx': 20}
    widgets['rotor_field_lines']  = Checkbutton(root, **default_check)
    widgets['rotor_field_vec']    = Checkbutton(root, **default_check)
    widgets['rotor_coil_front']   = Checkbutton(root, **default_check)
    widgets['stator_field_lines'] = Checkbutton(root, **default_check)
    widgets['stator_field_vec']   = Checkbutton(root, **default_check)
    widgets['stator_coil_front']  = Checkbutton(root, **default_check)

    widgets['rotor_field_lines']  .grid(row=row0 + 1, column=2, stick=W+E+N+S, padx=1, pady=1)
    widgets['rotor_field_vec']    .grid(row=row0 + 2, column=2, stick=W+E+N+S, padx=1, pady=1)
    widgets['rotor_coil_front']   .grid(row=row0 + 3, column=2, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_field_lines'] .grid(row=row0 + 1, column=1, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_field_vec']   .grid(row=row0 + 2, column=1, stick=W+E+N+S, padx=1, pady=1)
    widgets['stator_coil_front']  .grid(row=row0 + 3, column=1, stick=W+E+N+S, padx=1, pady=1)

    Label(root, text="stator [rad/s]", **default).grid(row=row0 + 2, column=10)
    Label(root, text="rotor [rpm]"   , **default).grid(row=row0 + 2, column=12)
    Label(root, text="grid [Hz]"     , **default).grid(row=row0 + 2, column=14)
    Label(root, text="slip [pu]"     , **default).grid(row=row0 + 2, column=16)
    Label(root, text="Pconv [kW]"    , **default).grid(row=row0 + 2, column=18)
    Label(root, text="Tind [Nm]"     , **default).grid(row=row0 + 2, column=20)


    root.columnconfigure(10, weight=3, minsize=70)
    root.columnconfigure(12, weight=3, minsize=70)
    root.columnconfigure(14, weight=3, minsize=70)
    root.columnconfigure(16, weight=3, minsize=70)
    root.columnconfigure(18, weight=3, minsize=70)
    root.columnconfigure(20, weight=3, minsize=70)

    root.columnconfigure(11, weight=1, minsize=5)
    root.columnconfigure(13, weight=1, minsize=5)
    root.columnconfigure(15, weight=1, minsize=5)
    root.columnconfigure(17, weight=1, minsize=5)
    root.columnconfigure(19, weight=1, minsize=5)
    root.columnconfigure(21, weight=1, minsize=5)

    default_instruments = copy(default)
    default_instruments['bg'] = '#dd8834'
    widgets['w_stator'] = Label(root, text="  0.0 rpm", **default_instruments)
    widgets['w_rotor']  = Label(root, text="-3475 rpm", **default_instruments)
    widgets['w_grid']   = Label(root, text="  -60 Hz" , **default_instruments)
    widgets['slip']     = Label(root, text=" 0.04"    , **default_instruments)
    widgets['Pconv']    = Label(root, text="-2341 W"  , **default_instruments)
    widgets['Tind']     = Label(root, text="-12.5 Nm" , **default_instruments)

    widgets['w_stator'].grid(row=row0 + 3, column=10, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['w_rotor'] .grid(row=row0 + 3, column=12, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['w_grid']  .grid(row=row0 + 3, column=14, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['slip']    .grid(row=row0 + 3, column=16, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['Pconv']   .grid(row=row0 + 3, column=18, stick=W+E+N+S, ipadx=1, pady=1)
    widgets['Tind']    .grid(row=row0 + 3, column=20, stick=W+E+N+S, ipadx=1, pady=1)

    # widgets['w_stator_um'] = Label(root, text="rpm", **default)
    # widgets['w_rotor_um'] = Label(root, text="rpm", **default)
    # widgets['w_grid_um'] = Label(root, text="Hz", **default)
    # widgets['slip_um'] = Label(root, text="pu", **default)
    # widgets['Pconv_um'] = Label(root, text="kW", **default)
    # widgets['Tind_um'] = Label(root, text="Nm", **default)
    #
    # widgets['w_stator_um'].grid(row=row0 + 3, column=11, stick=W)
    # widgets['w_rotor_um'].grid(row=row0 + 3, column=13, stick=W)
    # widgets['w_grid_um'].grid(row=row0 + 3, column=15, stick=W)
    # widgets['slip_um'].grid(row=row0 + 3, column=17, stick=W)
    # widgets['Pconv_um'].grid(row=row0 + 3, column=19, stick=W)
    # widgets['Tind_um'].grid(row=row0 + 3, column=21, stick=W)




    widgets['sim_inertia'] = Checkbutton(root, text='Newton 2nd law          ', **default)
    widgets['sim_inertia'].grid(row=row0 + 2, column=5)

    widgets['fps'] = Label(root, text='fps:', font=fonts['fps'], fg='#bb5533', bg=cl['bg'])
    widgets['fps'].grid(row=0, column=0, stick=W)



    widgets['time_factor'] = Label(root, text='...', **default)
    widgets['figs'] = (fig0, fig1)

    CustomAnim(canvas, widgets).loop()
    root.mainloop()


if __name__ == '__main__':
    main()