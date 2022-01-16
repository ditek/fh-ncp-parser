from typing import List
from collections import OrderedDict
from dataclasses import dataclass
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard


@dataclass
class FrameType:
    # An optional start index in case the listed fields do not start at 0
    start_idx: int
    # A map between field names and lengths
    fields: OrderedDict


###########################################################

frame_types = {
    'Metering event': FrameType(
        start_idx=1,
        fields=OrderedDict({
            'udid': 2,
            'ep': 1,
            'attributeFlag': 1,
            'curSumDelivered': 8,
            'curSumReceived': 8,
            'instantDemand': 4,
        })
    ),
    'OTA query next image event response': FrameType(
        start_idx=1,
        fields=OrderedDict({
            'udid': 2,
            'ep': 1,
            'ManufacturerID': 2,
            'ImageType': 2,
            'FileVersion': 4,
            'ImageSize': 4,
        })
    ),
}

result_text = ''

###########################################################


def to_int(hex_arr: List) -> int:
    hex_arr.reverse()
    hex_str = ''.join('{:02x}'.format(x) for x in hex_arr)
    return int(hex_str, 16)


class MainApp(App, BoxLayout):

    def on_start(self):
        self.root.ids.frame_type.values = [
            frame_name for frame_name in frame_types.keys()]
        return super().on_start()

    def log(self, text, append=False):
        """Write something to the log box"""
        if append:
            text = f'{self.root.ids.log.text}\n{str(text)}'
        self.root.ids.log.text = str(text)

    def on_parse(self, frame_type, data):
        global result_text
        self.log('')
        str_arr = data.replace('[', '').replace(']', '').split(' ')
        if '' in str_arr:
            str_arr.remove('')
        try:
            data_bytes = [int(x) for x in str_arr]
        except Exception as e:
            self.log('Error: cannot parse list elements as integers')
            return

        frame = frame_types[frame_type]
        values = {}
        current_idx = frame.start_idx
        for field, field_len in frame.fields.items():
            if current_idx+field_len > len(data_bytes):
                self.log(
                    f'Error: frame length mismatch. Check the selected frame type')
                return
            values[field] = to_int(
                data_bytes[current_idx:current_idx+field_len])
            current_idx += field_len
        result = ((x, y) for x, y in values.items())

        self.root.ids.field.clear_widgets()
        self.root.ids.value.clear_widgets()
        result_text = ''
        for item in result:
            field = Label(text=str(item[0]))
            value = Label(text=str(item[1]))
            self.root.ids.field.add_widget(field)
            self.root.ids.value.add_widget(value)
            result_text += f'{item[0]}\t\t{item[1]}\n'

    def on_copy(self):
        Clipboard.copy(result_text)


if __name__ == '__main__':
    # 0 2 0 6 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 141 190 16 0 0
    Window.top, Window.left = (100, 100)
    Window.clearcolor = (0.5, 0.5, 0.5, 1)
    MainApp().run()
