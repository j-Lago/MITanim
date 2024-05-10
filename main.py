import tkinter as tk
from NormCanvas import NormCanvas
from custom_animation import CustomAnim



def main():

    WIDTH, HEIGHT = 700, 700

    window = tk.Tk()
    window.title("Motor de Indução Trifásico")
    canvas = NormCanvas(window, bg='#ffffff', height=HEIGHT, width=WIDTH)

    fonts = {
        'default': ('Cambria', 12),
        'fps': ('Poor Richard', 14),
    }

    widgets = {
        'fps': tk.Label(window, text='fps:', font=fonts['fps'], fg='#bb5533'),
        'w_stator': tk.Label(window, text='...', font=fonts['default']),
        'w_rotor': tk.Label(window, text='...', font=fonts['default']),
        'w_grid': tk.Label(window, text='...', font=fonts['default']),
        'frame_delay': tk.Label(window, text='...', font=fonts['default'])
    }

    widgets['fps'].pack(anchor='w')
    canvas.pack()
    widgets['w_stator'].pack(anchor='e')
    widgets['w_rotor'].pack(anchor='e')
    widgets['w_grid'].pack(anchor='e')
    widgets['frame_delay'].pack(anchor='e')

    window.update()

    anim = CustomAnim(canvas, widgets)
    anim.loop()

    window.mainloop()


if __name__ == '__main__':
    main()
