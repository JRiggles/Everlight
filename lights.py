from phue import Bridge, Light


class LightController:
    def __init__(self, bridge_ip: str) -> None:
        self.bridge = Bridge(bridge_ip)
        self.bridge.connect()
        self.bridge.get_api()
        lights: dict[str, Light] = (
            self.bridge.get_light_objects('name')  # type: ignore
        )
        self.D1 = lights.get('Dining Room 1')
        self.D2 = lights.get('Dining Room 2')

        if self.D1:
            self.D1.on = True
        if self.D2:
            self.D2.on = True

    def reset_lights(self) -> None:
        """Reset the two lights to a default warm white color"""
        for light in (self.D1, self.D2):
            if light:
                # NOTE: these are the default warm white settings from Hue
                light.hue = 6929
                light.saturation = 129
                light.brightness = 254

    def all_on(self) -> None:
        """Turn both lights on"""
        if self.D1:
            self.D1.on = True
        if self.D2:
            self.D2.on = True

    def all_off(self) -> None:
        """Turn both lights off"""
        if self.D1:
            self.D1.on = False
        if self.D2:
            self.D2.on = False

    def set_color(self, light: Light | None, color: str) -> None:
        if not light or not color:
            return
        color = color.lstrip('#')
        r, g, b = (int(color[i:i+2], 16) / 255 for i in (0, 2, 4))
        light.xy = self._rgb_to_xy(r, g, b)

    def set_brightness(self, light: Light | None, brightness: int) -> None:
        if not light:
            return
        # scale the percentage brightness (0-100) to Hue brightness (0-254)
        brightness = int((brightness / 100) * 254)
        light.brightness = brightness

    @staticmethod
    def _rgb_to_xy(red, green, blue) -> tuple[float, float]:
        red = pow((red + 0.055) / 1.055, 2.4) if red > 0.04045 else red / 12.92
        green = pow((green + 0.055) / 1.055, 2.4) if green > 0.04045 else green / 12.92
        blue = pow((blue + 0.055) / 1.055, 2.4) if blue > 0.04045 else blue / 12.92
        x = red * 0.649926 + green * 0.103455 + blue * 0.197109
        y = red * 0.234327 + green * 0.743075 + blue * 0.022598
        z = green * 0.053077 + blue * 1.035763
        try:
            return x / (x + y + z), y / (x + y + z)
        except ZeroDivisionError:
            return 0.0, 0.0


if __name__ == '__main__':  # TEST
    lc = LightController('10.0.42.2')
