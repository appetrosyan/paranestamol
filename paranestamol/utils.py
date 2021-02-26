from os.path import splitext
from matplotlib.pyplot import rcParams

def cleanupFileRoot(file_root):
    ret = file_root.replace('file://', '', 1)
    exts = ['.stats', '.resume', '.paramnames', '.inputparams', '.ranges']
    ends = ['_equal_weights', '_dead-birth', '_dead','_phys_live-birth',  '_phys_live']
    root, ext = splitext(ret)
    if ext in exts:
        return root, ext
    elif ext == '.txt':
        for end in ends:
            try:
                rt, end = root.rsplit(end, 1)
                return rt, end+ext
            except ValueError:
                pass
    else:
       return file_root, ''         


class Legend:
    colorCycles = rcParams["axes.prop_cycle"].by_key()["color"]
    currentColorOffset = 0

    def __init__(self, title='', color=None, alpha=None):
        self.title = title
        if color is not None:
            self.color = color
        else:
            self.color = Legend.colorCycles[Legend.currentColorOffset
                                            % len(Legend.colorCycles)]
        if alpha is None:
            self.alpha = 1
        Legend.currentColorOffset += 1

        @property
        def color(self):
            return self._color

        @color.setter
        def color_(self, color):
            if isinstance(color, str):
                if len(color) == 8: # ARGB
                    self._color = f'#{color[3:]}'
                    self.alpha = int(color[1:3], 16)/int("ff", 16)
                else:           # Probably fine
                    self._color = color
