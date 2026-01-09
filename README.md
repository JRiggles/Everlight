![App Icon](static/appicon.png)

# Everlight

### Hello adventurer!

This is **Everlight**, a MacOS app I wrote to control the Hue lights at my home gaming table to make our D&D games more immersive.

It only works for the lights at my house, but you're welcome to look around.

I built the app for my DM because I thought it would be fun, and it was a good excuse to learn my way around [NiceGUI](https://nicegui.io).

## Features
- Control the color and brightness of not one, but *two* lights!
- Turn the lights on *or* off!
- Save presets for use later (if you don't provide a name for the preset, a random monster, spell, or item name from D&D 5e will be used)
- Export your presets for safe keeping
- The lights are automatically reset to their default "warm white" color when the app is exited

<img src="screenshots/main.png" alt="screenshot of the main Everlight application window">

## Dependencies
- [httpx](https://github.com/projectdiscovery/httpx)
- [NiceGUI](https://nicegui.io)
- [phue](https://github.com/studioimaginaire/phue)

Built using [py2app](https://github.com/ronaldoussoren/py2app) because I ran into issues with NiceGUI's built-in pyinstaller-based build system...

## Contributing

Don't worry about it!

## Acknowledgements
Thanks to [D&D 5e API](https://www.dnd5eapi.co) (no affiliation)

*Dungeons & Dragons is © Wizards of the Coast LLC. All rights reserved. This project is not affiliated with or endorsed by Wizards of the Coast.*

## AI Disclosure
I *did* use a generative tool to create the app icon, and no, I don't feel great about it.

## License

This project is licensed under the [MIT License](LICENSE).
