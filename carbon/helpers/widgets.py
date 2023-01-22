"""
Carbon helper module -- useful ipywidgets
"""
__VERSION__ = "1.0"
__DATE__ = "23/01/2023"

import ipywidgets as _ipw

class CheckboxManager():
    """
    manages checkboxes that create True/False dicts
    
    :choices:       the checkbox choices either as list/tuple, or as dict; if it is a dict, then
                    the keys of the dict are the IDs, and the values are the display text; if it
                    is a list/tuple then keys and display values are the same
    :values:        the initial values; either None, False (unchecked), True (checked), or a
                    tuple/list of bools, one for each of the boxes
    :objects:       the objects associated with the checkbox items; if given, the `objects` method
                    returns all (un)checked objects
    :disabled:      if None, all False; otherwise tuple/list of bools
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, choices, values=None, objects=None, disabled=None):
    
        self.choice_ids = tuple(str(x) for x in choices) 
        try:
            self.choice_descr = tuple(str(x) for x in choices.values())
        except AttributeError:
            self.choice_descr = self.choice_ids
        
        if objects is None:
            self._objects = self.choice_descr
        else:
            if not len(objects) == len(self.choice_ids):
                raise ValueError(f"len(objects) [{len(objects)}] must be len(choices) [{len(self.choice_ids)}]", objects, choices)
            self._objects = objects
        if values is None or values is False:
            values = (False,)*len(self.choice_ids)
        elif values is True:
            values = (True,)*len(self.choice_ids)
        elif len(values) == len(self.choice_ids):
            values = tuple(bool(v) for v in values)
        else:
            raise ValueError(f"len(values) [{len(values)}] must be len(choices) [{len(self.choice_ids)}]", 
                             values, choices)
        self.initial_values = tuple(values)
        if disabled is None:
            self.disabled = (False,)*len(self.choice_ids)
        else:
            self.disabled = tuple(bool(v) for v in disabled)
            if len(self.disabled) != len(self.choice_ids):
                raise ValueError(f"len(disabled) [{len(self.disabled)}] must be len(choices) [{len(self.choice_ids)}]", 
                                 disabled, choices)
            
        self._checkboxes = tuple(
            _ipw.Checkbox(
                value=val, 
                description=descr, 
                disabled=dis,
                #layout = _ipw.Layout(width="150px")
            )
            for val, descr, dis in zip(self.initial_values, self.choice_descr, self.disabled)
        )
        
    @classmethod
    def from_idvdct(cls, idvdct, disabled=None):
        """
        alternative constructor, using idvdict
        
        :idvdct:     the id/value dict, ie a dict id => value
        :disabled:   as in the main constructor 
        """
        return cls(choices=idvdct.keys(), values=idvdct.values(), disabled=disabled)
    
    @property
    def checkboxes(self):
        """the tuple of check boxes"""
        return self._checkboxes
    
    @property
    def vbox(self):
        """the widget box, as vbox"""
        return _ipw.VBox(self.checkboxes)
        # https://ipywidgets.readthedocs.io/en/7.6.3/examples/Widget%20Styling.html#The-Grid-layout
        # https://ipywidgets.readthedocs.io/en/7.6.3/examples/Widget%20Styling.html#The-Flexbox-layout

    @property
    def hbox(self):
        """the widget box, as vbox"""
        return _ipw.HBox(self.checkboxes)   
    
    @property
    def values_dct(self):
        """returns a dict choice_id => chosen value"""
        return {cid: cb.value for cid, cb in zip(self.choice_ids, self._checkboxes)}
    
    @property
    def values(self):
        """returns tuple of chosens values"""
        return tuple(cb.value for cb in self._checkboxes)

    def display(self, vertical=True):
        """short for display(self.box)"""
        display(self.vbox if vertical else self.hbox)

    @property
    def checked(self):
        """returns a tuple of the ids of all checked boxes"""
        return tuple(cid for cid, val in self.values_dct.items() if val == True)
    
    @property
    def unchecked(self):
        """returns a tuple of the ids of all unchecked boxes"""
        return tuple(cid for cid, val in self.values_dct.items() if val == False)
    
    def objects(self, checked=True):
        """returns a tuple of objects pertaining to the (un)checked boxes"""
        return tuple(obj for obj, cb in zip(self._objects, self._checkboxes) if cb.value == checked)
    
    def __call__(self, *args, **kwargs):
        self.display(*args, **kwargs)

class PcSliderManager():
    """
    manages sliders that display percentages (0..100)
    
    :choices:       the slider choices either as list/tuple, or as dict; if it is a dict, then
                    the keys of the dict are the IDs, and the values are the display text; if it
                    is a list/tuple then keys and display values are the same
    :values:        the initial values; must be between 0..1 [-1..1 for pm sliders], even though 
                    the percentages are displayed as between 0..100%
    :pm:            plusminus; if None or False, range is 0..100%; if True, -100%..100%
    :range:         either a tuple (min, max), or a range of tuples; must not be provided at the 
                    same time as pm
    :disabled:      if None, all False; otherwise tuple/list of bools
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, choices, values=None, pm=None, range=None, disabled=None):
    
        if not range is None and not pm is None:
            raise ValueError("pm and range must not be not-None at the same time")

        self.choice_ids = tuple(str(x) for x in choices) 
        try:
            self.choice_descr = tuple(str(x) for x in choices.values())
        except AttributeError:
            self.choice_descr = self.choice_ids
            
        if values is None:
            values = (0.,)*len(self.choice_ids)
        else:
            try:
                if values >= 0 and values <= 1:
                    values = (float(values),)*len(self.choice_ids)
                else:
                    raise ValueError("Value must be between 0..1", values)
            except TypeError:
                if len(values) == len(self.choice_ids):
                    values = tuple(float(v) for v in values)
                else:
                    raise ValueError(f"len(values) [{len(values)}] must be len(choices) [{len(self.choice_ids)}]", values, choices)         
        self.initial_values = tuple(values)
        
        if disabled is None:
            self.disabled = (False,)*len(self.choice_ids)
        else:
            self.disabled = tuple(bool(v) for v in disabled)
            if len(self.disabled) != len(self.choice_ids):
                raise ValueError(f"len(disabled) [{len(self.disabled)}] must be len(choices) [{len(self.choice_ids)}]", disabled, choices)
        
        if pm is None or pm is False:
            self.pm = (False,)*len(self.choice_ids)
        elif pm is True:
            self.pm = (True,)*len(self.choice_ids)
        else:
            self.pm = tuple(bool(v) for v in pm)
            if len(self.pm) != len(self.choice_ids):
                raise ValueError(f"len(pm) [{len(self.disabled)}] must be len(choices) [{len(self.choice_ids)}]", disabled, choices)
        
        if not range is None:
            try:
                range[0][0]
                # this must be a tuple of tuples
                self.range = tuple(tuple(v) for v in range)
                if len(self.range) != len(self.choice_ids):
                    raise ValueError(f"len(range) [{len(self.range)}] must be len(choices) [{len(self.choice_ids)}]", range, choices)
            except:
                self.range = (range,)*len(self.choice_ids)
        else:
            self.range = ( (-1, 1) if pmv else (0,1) for pmv in self.pm)

        self._sliders = tuple(
            _ipw.FloatSlider(
                value=val*100,
                min=rg[0]*100,
                max=rg[1]*100,
                step=0.1,
                description=descr,
                disabled=dis,
                continuous_update=False,
                orientation='horizontal',
                readout=True,
                readout_format='.1f',
            )
            for val, descr, dis, rg in zip(
                self.initial_values, 
                self.choice_descr, 
                self.disabled,
                self.range,
            )
        )
        
#     @classmethod
#     def from_idvdct(cls, idvdct, disabled=None):
#         """
#         alternative constructor, using idvdict
        
#         :idvdct:     the id/value dict, ie a dict id => value
#         :disabled:   as in the main constructor 
#         """
#         return cls(choices=idvdct.keys(), values=idvdct.values(), disabled=disabled)
    
    @property
    def sliders(self):
        """the tuple of check boxes"""
        return self._sliders
    
    @property
    def vbox(self):
        """the widget box, as vbox"""
        return _ipw.VBox(self.sliders)
        # https://ipywidgets.readthedocs.io/en/7.6.3/examples/Widget%20Styling.html#The-Grid-layout
        # https://ipywidgets.readthedocs.io/en/7.6.3/examples/Widget%20Styling.html#The-Flexbox-layout

    @property
    def hbox(self):
        """the widget box, as vbox"""
        return _ipw.HBox(self.sliders)   
    
    @property
    def values_dct(self):
        """returns a dict choice_id => chosen value"""
        return {cid: cb.value/100. for cid, cb in zip(self.choice_ids, self._sliders)}
    
    @property
    def values(self):
        """returns tuple of chosens values"""
        return tuple(cb.value/100. for cb in self._sliders)

    def display(self, vertical=True):
        """short for display(self.box)"""
        display(self.vbox if vertical else self.hbox)
        
    def __call__(self, *args, **kwargs):
        self.display(*args, **kwargs)


class DropdownManager():
    """
    manages dropdowns that create True/False dicts
    
    :options:       tuple/list of dropdown options; alternatively a dict, in which case the 
                    dict keys are the options, and the values are the labels
    :labels:        the labels that are displayed in the dropdown
    :descr:         an option string displayed in front of the dropdown
    :defaultix:     index of the default option chosen
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, options, labels=None, defaultval=None, defaultix=None, descr=None):
    
        if not defaultval is None and not  defaultix is None:
            raise ValueError("Only one of defaultval, defaultix can be None")

        self.options = tuple(str(x) for x in options) 
        try:
            self.labels = tuple(str(x) for x in options.values())
            if not labels is None:
                raise ValueError("Must not provide labels in option dict and explicitly", options, labels)
        except AttributeError:
            if labels is None:
                self.labels = self.options
            else:
                self.labels = tuple(str(x) for x in labels)
        
        self.options = tuple(str(x) for x in options) 

        if not descr: 
            descr = ""
        self.descr = str(descr)

        if not defaultval is None:
            self.defaultix = None
            self.defaultval = defaultval
            self._dropdown = _ipw.Dropdown(
                options=[(l,o) for l,o in zip(self.labels, self.options)],
                value=self.defaultval,
                description=self.descr,
                disabled=False,
            )
        else:
            if defaultix is None:
                defaultix = 0
            if not defaultix >=0 and defaultix < len(self.options):
                raise ValueError(f"must have 0 <= defaultix [{defaultix}] < len(options) [{len(self.options)}]")
            self.defaultix = defaultix
            self.defaultval = None
            self._dropdown = _ipw.Dropdown(
                options=[(l,o) for l,o in zip(self.labels, self.options)],
                index=self.defaultix,
                description=self.descr,
                disabled=False,
            )

    @property
    def dropdown(self):
        """returns the _dropdown"""
        return self._dropdown
    
    @property
    def value(self):
        """returns the dropdown value"""
        return self._dropdown.value
    
    @property
    def label(self):
        """returns the dropdown label"""
        return self._dropdown.label

    @property
    def result(self):
        """returns the dropdown value and label"""
        return self._dropdown.value, self._dropdown.label
    
    def display(self):
        """short for display(self.dropdown)"""
        display(self.dropdown)
        
    def __call__(self):
        self.display()
