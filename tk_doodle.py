from GSanim import CustomAnim
from tkinter import *
from assets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from NormCanvas import NormCanvas


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
    canvas                                .grid(row=0, column=10, columnspan=4, rowspan=4)


    row0 = 3
    Label(root, text="stator", **default).grid(row=row0+0, column=1)
    Label(root, text="rotor", **default).grid(row=row0+0, column=2)
    Label(root, text="Field vector", **default).grid(row=row0+1, column=0, sticky=E)
    Label(root, text="Field lines", **default).grid(row=row0+2, column=0, sticky=E)
    Label(root, text="Coil front", **default).grid(row=row0+3, column=0, sticky=E)

    widgets['rotor_field_lines']  = Checkbutton(root, **default)
    widgets['rotor_field_vec']    = Checkbutton(root, **default)
    widgets['rotor_coil_front']   = Checkbutton(root, **default)
    widgets['stator_field_lines'] = Checkbutton(root, **default)
    widgets['stator_field_vec']   = Checkbutton(root, **default)
    widgets['stator_coil_front']  = Checkbutton(root, **default)

    widgets['rotor_field_lines']  .grid(row=row0 + 1, column=1)
    widgets['rotor_field_vec']    .grid(row=row0 + 2, column=1)
    widgets['rotor_coil_front']   .grid(row=row0 + 3, column=1)
    widgets['stator_field_lines'] .grid(row=row0 + 1, column=2)
    widgets['stator_field_vec']   .grid(row=row0 + 2, column=2)
    widgets['stator_coil_front']  .grid(row=row0 + 3, column=2)

    Label(root, text="stator speed:", **default).grid(row=row0 + 1, column=10, sticky=E)
    Label(root, text="rotor speed:" , **default).grid(row=row0 + 2, column=10, sticky=E)
    Label(root, text="grid freq:"   , **default).grid(row=row0 + 3, column=10, sticky=E)
    Label(root, text="slip:"        , **default).grid(row=row0 + 1, column=12, sticky=E)
    Label(root, text="Pconv:"       , **default).grid(row=row0 + 2, column=12, sticky=E)
    Label(root, text="Tind:"        , **default).grid(row=row0 + 3, column=12, sticky=E)

    widgets['w_stator'] = Label(root, text="  0.0 rpm", **default)
    widgets['w_rotor']  = Label(root, text="-3475 rpm", **default)
    widgets['w_grid']   = Label(root, text="  -60 Hz" , **default)
    widgets['slip']     = Label(root, text=" 0.04"    , **default)
    widgets['Pconv']    = Label(root, text="-2341 W"  , **default)
    widgets['Tind']     = Label(root, text="-12.5 Nm" , **default)

    widgets['w_stator'].grid(row=row0 + 1, column=11, sticky=W)
    widgets['w_rotor'] .grid(row=row0 + 2, column=11, sticky=W)
    widgets['w_grid']  .grid(row=row0 + 3, column=11, sticky=W)
    widgets['slip']    .grid(row=row0 + 1, column=13, sticky=W)
    widgets['Pconv']   .grid(row=row0 + 2, column=13, sticky=W)
    widgets['Tind']    .grid(row=row0 + 3, column=13, sticky=W)

    widgets['sim_inertia'] = Checkbutton(root, text='Newton 2nd', **default)
    widgets['sim_inertia'].grid(row=row0 + 2, column=5)

    widgets['fps'] = Label(root, text='fps:', font=fonts['fps'], fg='#bb5533', bg=cl['bg'])
    widgets['fps'].grid(row=0, column=0, stick=W)



    widgets['time_factor'] = Label(root, text='...', **default)
    widgets['figs'] = (fig0, fig1)

    CustomAnim(canvas, widgets).loop()
    root.mainloop()


if __name__ == '__main__':
    main()