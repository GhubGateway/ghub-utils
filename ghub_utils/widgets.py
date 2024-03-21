from pathlib import Path
from time import sleep
from typing import List, Callable, Dict

import ipywidgets as pwidg
import matplotlib.pyplot as plt
from IPython.display import display, Javascript
from numpy import ndarray
from pandas import DataFrame

from . import files


class OptionToggle(pwidg.HBox):
    """Widget with multiple buttons that trigger a function on press"""
    def __init__(self, label: str, options: list, **kwargs):
        """
        :param options: list of button names
        :param kwargs:
        """
        label_desc = pwidg.Label(label)

        children = [label_desc,]
        for o in options:
            btn = pwidg.Button(description=o)
            children.append(btn)

        super().__init__(children=children, **kwargs)

    def on_click(self, btn_map: Dict[str, Callable]):
        """
        Register a function to trigger on click
        :param btn_map: dictionary of {button description: on click function}
        """
        for bname, func in btn_map.items():
            for b in self.children:
                if b.description == bname:
                    b.on_click(func)

    def click(self, btn_desc: str):
        for b in self.children:
            if b.description == btn_desc:
                b.click()

    def disable(self, btn_desc):
        for c in self.children:
            if c.description == btn_desc:
                c.disabled = True

    def enable(self, btn_desc):
        for c in self.children:
            if c.description == btn_desc:
                c.disabled = False


class DataSelector(pwidg.VBox):
    """
    Widget handling the selection of data for the project; allows for selecting
      from sample data (packaged with project), existing (previously uploaded),
      and upload data (upload your own)
    """
    OPTIONS = ['Sample', 'Personal']

    def __init__(self, validate_func: Callable = None, **kwargs):
        """
        :param validate_func: (optional) validation function to run on selected
          data
        """
        self._data = None # getter/setter below
        self._data_path: Path = None
        self._callbacks = []

        # uploaded/selected data
        label_instr = pwidg.Label(value='Select data source:')
        btn_sample = pwidg.Button(description=self.OPTIONS[0])
        btn_own = pwidg.Button(description=self.OPTIONS[1])
        box_options = pwidg.HBox((label_instr, btn_sample, btn_own))

        sel_file = pwidg.Select(
            options=[],
            description='Select files:',
        )
        sel_file.layout.display = 'none' # hide selector upon init

        btn_up = pwidg.FileUpload(
            desc='Upload',
            accept='.p,.csv',
            multiple=True,
            dir=files.DIR_SESS,
        )
        btn_submit = pwidg.Button(description='Select')
        btn_submit.disabled = True # disable upon init
        box_pick = pwidg.HBox((btn_submit, btn_up))
        box_pick.layout.display = 'none' # hide upon init

        out_selected = pwidg.Output()
        out_selected.layout.visibility = 'hidden'

        def source_sample(b):
            """Sample data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'hidden'
            box_pick.layout.display = 'block'
            out_selected.layout.visibility = 'visible'

            samples = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_SAMPLE_DATA).iterdir()
                if p.suffix in files.FORMAT_DATA_IN
            ]
            sel_file.options = samples

        def source_own(b):
            """Personal data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'visible'
            box_pick.layout.display = 'block'
            out_selected.layout.visibility = 'visible'

            personal = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_TEMP).iterdir()
                if p.suffix in files.FORMAT_DATA_IN
            ]
            sel_file.options = personal

        btn_sample.on_click(source_sample)
        btn_own.on_click(source_own)

        def select(change):
            """File selected from selector"""
            v = change['new']

            if (v is not None) and (len(v) > 0):
                btn_submit.disabled = False
                # save data path from project root
                self._data_path = files.DIR_PROJECT / v
            else:
                btn_submit.disabled = True

        sel_file.observe(select, names='value')

        def submit(b):
            """Read data in @self.data_path"""
            data = files.load_data(self._data_path)
            out_selected.clear_output(wait=True)

            with out_selected:
                if validate_func is not None:
                    try:
                        validate_func(data)
                    except Exception as e:
                        print(f'*** NOTE ***'
                              f'\nSelected data is not in a proper format for '
                              f'the fitting functions. Reason: '
                              f'\n{e.args[0]}'
                              f'\n************')

                print(f'Loaded data from: {self._data_path.name}\n'
                      f'First 5 elements:')

                if isinstance(data, DataFrame):
                    display(data.head(5))
                elif isinstance(data, ndarray):
                    display(data[:5, :])

            self.data = data

        btn_submit.on_click(submit)

        def upload(change):
            v = change['new']

            if (v is not None) and (len(v) > 0):
                for name, meta in v.items():
                    # files.dump_data() requires a dictionary
                    d = {name: meta['content']}
                    files.dump_data(files.DIR_TEMP / name, d, bytes=True)
                    btn_own.click() # reload list of existing files

        btn_up.observe(upload, names='value')

        super().__init__(
            [box_options, sel_file, box_pick, out_selected],
            **kwargs
        )

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, val):
        """Call observing functions"""
        self._data = val
        for cb in self._callbacks:
            cb(self._data)

    def m_observe(self, callback):
        self._callbacks.append(callback)


class ResultsDownloader(pwidg.HBox):
    """
    Abstract widget object for downloading some data with a field for specifying filename and a
      dropdown filetype selection
    """
    def __init__(self,
                 placeholder_filename: str,
                 download_formats: List,
                 download_name: str):
        txt_filename = pwidg.Text(
            value='',
            placeholder=placeholder_filename,
        )
        drop_file_format = pwidg.Dropdown(
            options=download_formats,
            value=download_formats[0]
        )
        btn_down = pwidg.Button(
            description=download_name,
            icon='download',
            disabled=True
        )

        def toggle(change):
            """Disable download button if no filename specified"""
            if change['name'] == 'value':
                if len(change['new']) > 0:
                    btn_down.disabled = False
                else:
                    btn_down.disabled = True

        txt_filename.observe(toggle)

        super().__init__((txt_filename, drop_file_format, btn_down))

    def on_click(self, func):
        btn_down = self.children[2]
        btn_down.on_click(func)

    def download(self, **kwargs):
        """Function that downloads respective data"""
        raise NotImplementedError('Abstract method; must override!')

    def disable(self):
        """
        Disable everything but the download button -- that gets controlled by
          the filename field
        """
        # TODO 6/27: could see this not working as intended if order of the
        #   children is changed
        for c in self.children[:-1]:
            c.disabled = True

    def enable(self):
        """
        Enable everything but the download button -- that gets controlled by
          the filename field
        """
        # TODO 6/27: could see this not working as intended if order of the
        #   children is changed
        for c in self.children[:-1]:
            c.disabled = False

    def hide(self):
        """Hide the widget"""
        if self.layout.display == 'block':
            self.layout.display = 'none'

    def show(self):
        """Show the widget"""
        if self.layout.display == 'none':
            self.layout.display = 'block'


class PlotDownloader(ResultsDownloader):
    """Button to download plots"""
    def __init__(self):
        super().__init__(
            placeholder_filename='enter plot filename',
            download_formats=files.FORMAT_IMG_OUT,
            download_name='Plot'
        )

    def download(self, fig: plt.Figure):
        """Download image to browser"""
        txt_filename = self.children[0]
        drop_file_format = self.children[1]

        filename = f'{txt_filename.value}.{drop_file_format.value}'
        path_up = files.upload_plt_plot(fig, filename)
        # need to make path relative to '.' for javascript windows
        path_rel = files.get_path_relative_to(path_up, files.DIR_PROJECT).as_posix()
        mpath = Path(path_rel)

        while True:
            if not mpath.exists():
                sleep(1)
            else:
                # trigger a browser popup that will download the image to browser
                js = Javascript(
                    f"window.open('{path_rel}', 'Download', '_blank')"
                )
                display(js)
                break


class DataDownloader(ResultsDownloader):
    """Widget for transformed data downloading"""
    def __init__(self):
        super().__init__(
            placeholder_filename='enter output data filename',
            download_formats=files.FORMAT_DATA_OUT,
            download_name='Data'
        )

    def download(self, data: dict):
        """Download @data to host results directory and to user system"""
        txt_filename = self.children[0]
        drop_file_format = self.children[1]

        fname = f'{txt_filename.value}.{drop_file_format.value}'
        fpath = files.DIR_OUT / fname
        files.dump_data(fpath, data, bytes=False)

        # need to make path relative to '.' for javascript windows
        path = files.get_path_relative_to(fpath, files.DIR_PROJECT).as_posix()

        # trigger a browser popup that will download the image to browser
        js = Javascript(
            f"window.open('{path}', 'Download', '_blank')"
        )
        display(js)


class FormConfigIO(pwidg.VBox):
    """
    Form widget for changing parameters of a function and plotting its results
    """
    def __init__(self,
                 form_widgets: List,
                 update_func: Callable,
                 submit_text: str = "Submit",
                 download=True,
                 **kwargs):
        """
        :param form_widgets: list of widgets to display vertically-stacked
        :param update_func:
        :param submit_text:
        :param download: should a download button be displayed to save output?
        :param test:
        :param test_msg:
        :param kwargs:
        """
        btn_submit = pwidg.Button(description=submit_text)
        down_plot = PlotDownloader()
        down_data = DataDownloader()
        if download:
            down_plot.disable() # nothing to download yet; disable
            down_data.disable()  # nothing to download yet; disable
        else:
            down_plot.hide() # @download == False
            down_data.hide()  # @download == False
        box_down = pwidg.VBox([down_plot, down_data])
        box_btns = pwidg.HBox([btn_submit, box_down])
        out_plot = pwidg.Output()

        # @update_func output
        output = None

        def update(b):
            """Call the @update_func passed above"""
            nonlocal output
            output = update_func()

            # if @update_func returns some results, enable downloading
            if output is not None:
                down_plot.enable()
                down_data.enable()

                with out_plot:
                    out_plot.clear_output(wait=True)
                    display(output['fig'])
            else:
                down_plot.disable()
                down_data.disable()

        def save_plot(b):
            nonlocal output
            fig = output.get('fig')

            down_plot.download(fig)

        def save_data(b):
            nonlocal output

            data = output.get('data')
            down_data.download(data)

        btn_submit.on_click(update)
        down_plot.on_click(save_plot)
        down_data.on_click(save_data)

        children = (*form_widgets, box_btns, out_plot)
        super().__init__(children, **kwargs)
        display(self)
