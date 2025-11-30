from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from nicegui import app, ui, Client
from nicegui.observables import ObservableDict
from lights import LightController
from randomonster import get_dnd, names, used_names


@dataclass
class LightBoardPreset:
    """Dataclass to store a lighting preset"""
    color1: str
    brightness1: int
    color2: str
    brightness2: int
    name: Optional[str] = ''


lc = LightController('10.0.42.2')
# store last selected colors for each light
last_color = dict.fromkeys([lc.D1.name, lc.D2.name], '')  # type: ignore

# UI color scheme
drow = '#6b6b88'
orc = '#91a32b'
dragon = "#BE3D20"


@ui.page('/')
def index(client: Client) -> None:
    app.add_static_files('/static', 'static')
    ui.query('body').style(
        "background-image: url('static/bg1.jpeg');"
        "background-attachment: fixed;"
        "background-size: cover;"
        "background-position: center;"
        "background-repeat: no-repeat;"
        "backdrop-filter: blur(0.33rem) brightness(42%);"
    )
    # set color scheme
    ui.colors(primary=drow, positive=orc, negative=dragon)
    ui.markdown("## 💡 LightBoard")

    # help button
    with ui.row().classes('absolute top-0 right-0 p-4'):
        ui.button(icon='help', on_click=lambda: help_modal.open())

    # help modal
    with ui.dialog() as help_modal, ui.card().classes('no-shadow'):
        ui.markdown("### LightBoard Help")
        ui.separator()
        ui.markdown(
            """
            ##### *Light Controls*

            Use the switches to turn lights on/off, the color pickers to change colors, and the sliders to adjust brightness. Changes are made immediately.

            ##### *Global Controls*

            Use the buttons to reset the lights to their default setting, turn all lights on or off, or save a preset for later.

            ##### *Presets*

            Save your current light settings as a preset, apply saved presets, or delete them. You can provide a name for your preset before saving it, or a random name will be generated.
            """
        )
        ui.button('Okay', on_click=lambda: help_modal.close())

    def save_preset() -> None:
        """Save the current light settings as a preset in user storage"""
        preset = LightBoardPreset(
            color1=last_color.get(lc.D1.name, '#FFFFFF'),  # type: ignore
            brightness1=brightness_1.value,
            color2=last_color.get(lc.D2.name, '#FFFFFF'),  # type: ignore
            brightness2=brightness_2.value,
            # use the user-provided name for the preset, or a random monster
            # name, or if all else fails, a random UUID segment
            name=preset_name.value or get_dnd() or uuid4().hex[:8].upper(),
        )
        if preset_name.value:
            preset_name.value = ''  # clear preset name input on save
        app.storage.user[preset.name] = preset  # store preset
        ui.notify('Preset saved!', color='positive')
        show_presets()

    def show_presets() -> None:
        """Display saved presets from user storage"""
        if app.storage.user:  # show presets card if any presets are saved
            presets_card.visible = True
        else:  # otherwise hide the card
            presets_card.visible = False
            return
        preset_container.clear()
        for name, preset in app.storage.user.items():
            if isinstance(preset, ObservableDict):
                # convert ObservableDict back to LightBoardPreset dataclass
                preset = LightBoardPreset(**preset)
            with preset_container, ui.card().props('flat bordered'):
                ui.markdown(f'##### {preset.name}')
                with ui.row():
                    ui.icon('circle', color=preset.color1, size='3rem')
                    ui.label(f'Brightness: {preset.brightness1}')
                with ui.row():
                    ui.icon('circle', color=preset.color2, size='3rem')
                    ui.label(f'Brightness: {preset.brightness2}')
                with ui.row().classes('justify-between'):
                    ui.button(
                        'Apply',
                        on_click=lambda p=preset: apply_preset(p)
                    )
                    ui.button(
                        'Delete',
                        on_click=lambda n=name: delete_preset(str(n))
                    )

    def apply_preset(preset: LightBoardPreset) -> None:
        """Set the lights to the given preset"""
        # set light colors
        lc.set_color(lc.D1, preset.color1)
        lc.set_color(lc.D2, preset.color2)
        # set color picker button backgrounds
        picker_1.style(f'background-color: {preset.color1} !important;')
        picker_2.style(f'background-color: {preset.color2} !important;')
        # set color picker vaulues
        p1.set_color(preset.color1)
        p2.set_color(preset.color2)
        # set brightness sliders (also sets actual light brightness)
        brightness_1.value = preset.brightness1
        brightness_2.value = preset.brightness2
        # force update to frontend on client side
        picker_2.update()
        picker_1.update()
        # notify user
        ui.notify('Preset applied', color='primary')

    def delete_preset(name: str) -> None:
        """Delete the preset with the given name from storage"""
        if name in app.storage.user:
            del app.storage.user[name]
            if name in used_names:
                used_names.remove(name)
                names.add(name)
            ui.notify(f'Preset "{name}" deleted', color='negative')
            show_presets()

    # main UI layout
    # REFACTOR: the light controls are essentially identical for both lights;
    # maybe they could be a class (or whaterver nicegui uses for reusable
    # UI components?)
    with ui.row(wrap=False).classes('w-full'):
        # light 1 controls
        with ui.card().classes('no-shadow w-full'), ui.column().classes('px-4 w-full'):
            ui.markdown("#### Light 1")
            on_off_1 = ui.switch(
                'On',
                value=True,
                on_change=lambda e: [
                    setattr(lc.D1, 'on', e.value),
                    setattr(on_off_1, 'text', 'On' if e.value else 'Off')
                ]
            )

            with (
                ui.row().classes('w-full'),
                ui.button(icon='palette').classes('w-full') as picker_1
            ):
                p1 = ui.color_picker(
                    on_pick=lambda e: [
                        lc.set_color(lc.D1, e.color),
                        print(e),
                        picker_1.style(
                            f'background-color: {e.color} !important;'
                        ),
                        last_color.update({lc.D1.name: e.color}),
                    ]
                )
            # show minimal color picker
            p1.q_color.props('default-view=palette no-header')
            with ui.row().classes('w-full'):
                ui.icon('brightness_6', size='1.5rem')
                brightness_1 = ui.slider(
                    min=0,
                    max=100,
                    value=100,
                    on_change=lambda e: lc.set_brightness(lc.D1, int(e.value)),
                ).props('label-always')

        # light 2 controls
        with ui.card().classes('no-shadow w-full'), ui.column().classes('px-4 w-full'):
            ui.markdown("#### Light 2")
            on_off_2 = ui.switch(
                'On',
                value=True,
                on_change=lambda e: [
                    setattr(lc.D2, 'on', e.value),
                    setattr(on_off_2, 'text', 'On' if e.value else 'Off')
                ]
            )
            with (
                ui.row().classes('w-full'),
                ui.button(icon='palette').classes('w-full') as picker_2
            ):
                p2 = ui.color_picker(
                    on_pick=lambda e: [
                        lc.set_color(lc.D2, e.color),
                        picker_2.style(
                            f'background-color: {e.color} !important;'
                        ),
                        last_color.update({lc.D2.name: e.color}),
                    ]
                )
                # show minimal color picker
                p2.q_color.props('default-view=palette no-header')
            with ui.row().classes('w-full'):
                ui.icon('brightness_6', size='1.5rem')
                brightness_2 = ui.slider(
                    min=0,
                    max=100,
                    value=100,
                    on_change=lambda e: lc.set_brightness(lc.D2, int(e.value)),
                ).props('label-always')

    # global controls
    with ui.row():
        ui.button('Reset', on_click=lc.reset_lights)
        # FIXME: I'm almost 100% sure setattr isn't the right way to do this
        ui.button('All On', on_click=(
            lambda _: [
                setattr(on_off_1, 'value', True),
                setattr(on_off_2, 'value', True)
            ]
        ))
        ui.button('All Off', on_click=(
            lambda _: [
                setattr(on_off_1, 'value', False),
                setattr(on_off_2, 'value', False)
            ]
        ))
        ui.button('Save as Preset', on_click=save_preset)
    with ui.row().classes('w-1/4'):
        preset_name = ui.input(
            'Preset Name (optional):',
            # placeholder=choice(list(names)),
        ).classes('w-full')

    with ui.card().classes('w-full no-shadow') as presets_card:
        ui.markdown("#### Saved Presets").classes('px-4')
        preset_container = ui.row().classes('px-4')
    show_presets()


if __name__ in {"__main__", "__mp_main__"}:
    # app.native.window_args['resizable'] = True
    ui.run(
        title='LightBoard',
        reload=True,
        dark=True,
        storage_secret='lightboard_secret',
        # native=True,
    )
