from dataclasses import dataclass
from typing import Tuple
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from cycler import cycler
from itertools import combinations
from colorspacious import cspace_convert
from matplotlib.colors import to_rgb, to_hex
import numpy as np

@dataclass(frozen=True) 
class Palette:

    name: str
    colours: Tuple[str, ...]

    def __getitem__(self, index):
        return self.colours[index]

    def __len__(self):
        return len(self.colours)

    @property
    def listed_cmap(self):
        '''discrtised colour map'''
        return ListedColormap(self.colours, name=f"{self.name}_listed")

    @property
    def continuous_cmap(self):
        '''continuous colour map'''
        return LinearSegmentedColormap.from_list(self.name, self.colours, N=256)

    @property
    def cycler(self):
        return cycler(color=self.colours)

    @staticmethod
    def relative_luminance(colour):

        """Calculate WCAG relative luminance."""

        rgb = to_rgb(colour)
        def linearise(channel):
            if channel <= 0.04045:
                return channel / 12.92
            return ((channel + 0.055) / 1.055) ** 2.4

        r, g, b = (linearise(channel) for channel in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @classmethod
    def contrast_ratio(cls, colour1, colour2):

        """Calculate the luminance contrast ratio."""

        luminance1 = cls.relative_luminance(colour1)
        luminance2 = cls.relative_luminance(colour2)
        lighter = max(luminance1, luminance2)
        darker = min(luminance1, luminance2)
        return (lighter + 0.05) / (darker + 0.05)

    @property
    def hc_2colour(self):

        colour1, colour2 = max(
            combinations(self.colours, 2),
            key=lambda pair: self.contrast_ratio(*pair),
        )
        hc_colour = [colour1, colour2]

        return hc_colour

    @property
    def hc_show(self):

        """Show the 2 colours with the greatest luminance contrast."""

        cmap = ListedColormap(self.hc_2colour)

        return cmap

    def cvd(self, cvd_type='deuteranomaly', severity=100):

        """
        Simulate a colour palette under colour-vision deficiency.
        
        Parameters
        ----------
        colors : list of str;Matplotlib-compatible colours.
        cvd_type : str; 'deuteranomaly', 'protanomaly', or 'tritanomaly'.
        severity : float; 0 means normal colour vision; 100 approximates complete deficiency.
        """
        
        rgb = np.array([to_rgb(colour) for colour in self.colours])
        cvd_space = {
            "name": "sRGB1+CVD",
            "cvd_type": cvd_type,
            "severity": severity}

        simulated = cspace_convert(rgb, cvd_space, "sRGB1")
        simulated = np.clip(simulated, 0, 1)
        simulated_colours = [to_hex(colour) for colour in simulated]

        #palette = Palette(name=f'{self.name}_{cvd_type[:3]}_{int(severity)}', colours=simulated_colours)
        cmap = ListedColormap(simulated_colours)

        return cmap
    
    @property
    def gray(self):

        """
        Convert colours to grayscale using relative luminance.
        """

        rgb = np.array([to_rgb(colour) for colour in self.colours])
        # Approximate luminance weights for displayed sRGB colours
        luminance = (
            0.2126 * rgb[:, 0]
            + 0.7152 * rgb[:, 1]
            + 0.0722 * rgb[:, 2]
        )

        grayscale = np.column_stack([luminance] * 3)
        simulated_colours = [to_hex(colour) for colour in grayscale]

        cmap = ListedColormap(simulated_colours)

        return cmap


van_gogh_night = Palette(name='van_gogh_night', colours=('#304F8C', '#30728C', '#97B78E', '#BDBF75', '#BF9821'))
van_gogh_wheatfield= Palette(name='van_gogh_wheatfield', colours=('#44774A', '#85B979', '#A9D9D4', '#D9A23D', '#BF8136'))
#cezane_apple = Palette(name='cezane_apple', colours=('#734D3F', '#8C281F', '#A67538', '#D9D1B8', '#72828C'))
#monet_bench = Palette(name='monet_bench', colours=('#5B7343', '#818C2E', '#A6A056', '#BFAC95', '#8C6F65'))
monet_irises = Palette(name='monet_irises', colours=('#515A8C', '#64758C', '#A8BF84', '#81AA82', '#6E7346'))
monet_sunrise = Palette(name='monet_sunrise', colours=('#3873A6', '#809BBF', '#9BB9BF', '#F2C094', '#D99E89'))
rainbow = Palette(name='rainbow', colours=('#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51'))