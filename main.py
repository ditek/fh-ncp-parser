
from typing import List
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


def to_int(hex_arr: List) -> int:
    hex_arr.reverse()
    hex_str = ''.join('{:02x}'.format(x) for x in hex_arr)
    return int(hex_str, 16)


class MainApp(App, BoxLayout):

    def log(self, text, append=False):
        """Write something to the log box"""
        if append:
            text = f'{self.root.ids.log.text}\n{str(text)}'
        self.root.ids.log.text = str(text)

    def on_parse(self, frame_type, data):
        str_arr = data.replace('[', '').replace(']', '').split(' ')
        if '' in str_arr:
            str_arr.remove('')
        try:
            data_bytes = [int(x) for x in str_arr]
        except Exception as e:
            self.log('Error: cannot parse list elements as integers')
            return

        if frame_type == 'Metering event':
            udidIndex = 1
            epIndex = udidIndex + 2
            attributeFlagIndex = epIndex + 1
            curSumDeliveredIndex = attributeFlagIndex + 1
            curSumReceivedIndex = curSumDeliveredIndex + 8
            instantDemandIndex = curSumReceivedIndex + 8

            if len(data_bytes) < instantDemandIndex:
                self.log(
                    f'Error: Expected data length {instantDemandIndex} got {len(data_bytes)}')
                return

            udid = to_int(data_bytes[udidIndex:udidIndex+2])
            ep = to_int(data_bytes[epIndex:epIndex+1])
            curSumDelivered = to_int(
                data_bytes[curSumDeliveredIndex:curSumDeliveredIndex + 8])
            curSumReceived = to_int(
                data_bytes[curSumReceivedIndex:curSumReceivedIndex + 8])
            instantDemand = to_int(
                data_bytes[instantDemandIndex:instantDemandIndex + 4])

            result = (
                ('udid', udid),
                ('ep', ep),
                ('curSumDelivered', curSumDelivered),
                ('curSumReceived', curSumReceived),
                ('instantDemand', instantDemand),
            )

        self.root.ids.field.clear_widgets()
        self.root.ids.value.clear_widgets()
        for item in result:
            field = Label(text=str(item[0]))
            value = Label(text=str(item[1]))
            self.root.ids.field.add_widget(field)
            self.root.ids.value.add_widget(value)


if __name__ == '__main__':
    # 0 2 0 6 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 141 190 16 0 0
    Window.top, Window.left = (100, 100)
    Window.clearcolor = (0.5, 0.5, 0.5, 1)
    MainApp().run()
