import shutil

from contextlib import suppress
from dataclasses import dataclass
from multiprocessing import freeze_support  # noqa
from pathlib import Path
from typing import Optional
from uuid import uuid4

from nicegui import app, native, ui
from nicegui.observables import ObservableDict

from lights import LightController
from randomonster import get_dnd, names, used_names

# TODO: better fonts for title, UI
# TODO: fix help modal position in non-fullscreen viewports
# TODO: randomizer for colors
# TODO: easier editing of preset names
# TODO: import presets (storage-general.json)
# TODO: preconfigured animations
# TODO: drag to rearrange presets
# TODO: add scene transition timeline? Might be verrrry complicated...
# TODO: custom animations (needs scene timeline probably)
# TODO: replace lambdas in colorpicker callbacks with proper functions
# TODO: figure out a better way to have useful functions in '/' besides using
#       a ton of inner functions

VERSION = '1.1.0'


@dataclass
class LightBoardPreset:
    """Dataclass to store a lighting preset"""
    color1: str
    brightness1: int
    color2: str
    brightness2: int
    name: Optional[str] = ''

# UI color scheme
drow = '#6b6b88'
orc = '#91a32b'
dragon = '#BE3D20'
behir = "#5680AD"

with suppress(ConnectionRefusedError):
    # placeholder for LightController instance
    lc = LightController('127.0.0.1')
# FIXME: this is gross, but I can't think of a better way to give the
# on_shutdown handler access to the lc - it's early and I'm tired


@app.on_shutdown
def cleanup() -> None:
    if lc is not None and isinstance(lc, LightController):
        lc.reset_lights()


@app.on_page_exception
def connection_error_page(exception: Exception) -> None:
    if not isinstance(exception, ConnectionError):
        raise
    with ui.column().classes('absolute-center items-center gap-8'):
        ui.icon('wifi_off', size='xl')
        ui.label(f'{exception}').classes('text-2xl')


@ui.page('/')
def index() -> None:
    global lc
    try:
        lc = LightController('10.0.42.2')
    except OSError:  # failed to connect to bridge
        # NOTE: rasing an exception will put up the NiceGUI error page
        raise ConnectionError('Check your internet connection and try again')

    # store last selected colors for each light
    last_color = dict.fromkeys([lc.D1.name, lc.D2.name], '')  # type: ignore

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
    ui.colors(
        primary=drow,
        positive=orc,
        negative=dragon,
        info=behir,
    )

    # help button
    with ui.row().classes('items-baseline'):
        # heading
        ui.markdown("### Everlight").classes('ml-4')
        ui.button(
            icon='help',
            on_click=lambda: help_modal.open()
        ).classes('absolute top-4 right-4 px-4 py-2')

    # help modal
    with ui.dialog() as help_modal, ui.card().classes('no-shadow'):
        with ui.row().classes('items-baseline'):
            ui.markdown('### Everlight Help')
            ui.markdown(f'Version {VERSION}').classes(
                'text-sm text-gray-500 mr-auto'
            )
            ui.image('static/appicon.png').classes(
                'w-16 h-16 absolute right-4'
            )
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

    def reset_lights() -> None:
        lc.reset_lights()
        # restore the picker buttons to the default pirmary color
        picker_1.style('background-color: var(--q-primary) !important;')
        picker_2.style('background-color: var(--q-primary) !important;')
        ui.notify('Lights reset', type='info')

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
        app.storage.general[preset.name] = preset  # store preset
        ui.notify('Preset saved!', type='positive')
        show_presets()

    def show_presets() -> None:
        """Display saved presets from user storage"""
        if app.storage.general:  # show presets card if any presets are saved
            print(app.storage.general)  # DEBUG
            presets_card.visible = True
        else:  # otherwise hide the card
            presets_card.visible = False
            return
        preset_container.clear()
        for name, preset in app.storage.general.items():
            if isinstance(preset, ObservableDict):
                # convert ObservableDict back to LightBoardPreset dataclass
                preset = LightBoardPreset(**preset)
            elif isinstance(preset, str):
                return
            with preset_container, ui.card().props('flat bordered'):
                ui.markdown(f'##### {preset.name}')
                with ui.row().classes('items-center'):
                    ui.icon('circle', color=preset.color1, size='3rem')
                    ui.label(f'Brightness: {preset.brightness1}')
                with ui.row().classes('items-center'):
                    ui.icon('circle', color=preset.color2, size='3rem')
                    ui.label(f'Brightness: {preset.brightness2}')
                with ui.row().classes('justify-between'):
                    ui.button(
                        'Apply',
                        on_click=(
                            lambda p=preset: apply_preset(p)  # type: ignore
                        )
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
        ui.notify('Preset applied', type='info', color='primary')

    async def delete_preset(name: str) -> None:
        """Delete the preset with the given name from storage"""
        with ui.dialog() as dialog, ui.card().classes('no-shadow'):
            ui.html(
                'Are you sure you want to delete the preset'
                f'<br><b>"{name}"</b>?',
                sanitize=False,
                tag='h6',
            )
            with ui.row():
                ui.button(
                    'Yes',
                    on_click=lambda: dialog.submit('Yes'),
                    color='negative',
                )
                ui.button(
                    'No',
                    on_click=lambda: dialog.submit('No')
                )

        # choice = await dialog
        if await dialog == 'Yes' and name in app.storage.general:
            del app.storage.general[name]
            if name in used_names:
                used_names.remove(name)
                names.add(name)
            ui.notify( f'Preset "{name}" deleted', color='negative')
            show_presets()

    def export_presets() -> None:
        """Export presets to the Downloads folder"""
        # resolve path inside the app bundle
        basepath = Path(__file__).resolve().parent
        storage_path = basepath / '.nicegui' / 'storage-general.json'

        if not storage_path.exists():
            ui.notify(
                f'Storage file not found at: {storage_path}',
                type='negative'
            )
            return

        downloads_folder = Path.home() / 'Downloads'
        shutil.copy(storage_path, downloads_folder)
        destination = downloads_folder / 'Everlight Presets.json'
        shutil.move(downloads_folder / 'storage-general.json', destination)

        if destination.exists():
            ui.notify('Presets exported to Downloads folder!', type='positive')
        else:
            ui.notify('Exporting presets failed', type='negative')

    def import_presets() -> None:  # TODO: implement importing
        """Import a presets file"""
        # resolve path inside the app bundle
        basepath = Path(__file__).resolve().parent
        storage_path = basepath / '.nicegui' / 'storage-general.json'

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
                        last_color.update(
                            {lc.D1.name: e.color}  # type: ignore
                        ),
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
                        last_color.update(
                            {lc.D2.name: e.color}  # type: ignore
                        ),
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
        ui.button('Reset', on_click=reset_lights)
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
        ui.separator().props('vertical')
        ui.button('Save as Preset', on_click=save_preset)
        ui.button('Export Presets', on_click=export_presets)
        ui.button(
            'Import Presets',
            on_click=import_presets
        ).props('disabled').tooltip('Coming soon!')
    with ui.row().classes('w-1/4'):
        preset_name = ui.input(
            'Preset Name (optional):',
            # placeholder=choice(list(names)),
        ).classes('w-full')

    with ui.card().classes('w-full no-shadow') as presets_card:
        ui.markdown("#### Saved Presets").classes('px-4')
        preset_container = ui.row().classes('px-4')
    show_presets()


if __name__ in {'__main__', '__mp_main__'}:
    freeze_support()  # noqa
    app.native.window_args['resizable'] = True
    # app.native.start_args['debug'] = True
    ui.run(
        # reload=True,
        title='Everlight - D&D Lightboard',
        fullscreen=True,
        dark=True,
        # storage_secret='lightboard_secret',
        native=True,
        window_size=(1000, 625),
        port=native.find_open_port()
    )
