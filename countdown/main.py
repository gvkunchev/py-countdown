from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

import config


class ExitPopup(Popup):

    def exit(self):
        app.stop()


class CountdownWidget(Widget):

    timer_text = StringProperty("")
    process_percent = NumericProperty(1)

    def __init__(self, *args, **kwargs):
        self._init_config()
        self._deadline = config.TIMER * config.SECONDS_IN_MIN
        self._fullscreen = False
        self._timer = self._deadline
        self._running = False
        self._update_bind_properties()
        self._exit_popup = ExitPopup()
        super().__init__(*args, **kwargs)

    def _init_config(self):
        for item in dir(config):
            setattr(self, item, getattr(config, item))

    def _update_bind_properties(self):
        self.timer_text = '{:02}:{:02}'.format(*divmod(self._timer,
                                                       self.SECONDS_IN_MIN))
        try:
            self.process_percent = self._timer / self._deadline
        except ZeroDivisionError:
            self.process_percent = 0

    def _tick(self, *_):
        if not self._timer:
            self._running = False
            return Clock.unschedule(self._tick)
        self._timer -= 1
        self._update_bind_properties()

    def _toggle_clock(self):
        if self._running:
            Clock.unschedule(self._tick)
        else:
            Clock.schedule_interval(self._tick, 1)
        self._running = not self._running

    def _adjust_time(self, time):
        if self._timer == 0 and time < 0:
            return False
        if self._timer + time < 0:
            time = -self._timer
        self._timer += time
        self._deadline += time
        self._update_bind_properties()

    def _toggle_full_screen(self):
        if self._fullscreen:
            Window.fullscreen = False
        else:
            Window.fullscreen = 'auto'
        self._fullscreen = not self._fullscreen

    @property
    def text_height(self, *_):
        return self.TEXT_FONT_SIZE * 2 + self.TEXT_MARGIN_TOP

    @property
    def lines_height(self, *_):
        return (self.THICK_LINE_HEIGHT + self.THIN_LINE_HEIGHT
                + self.LINE_MARGIN * 2)

    def update_width(self, *_):
        self.width = min(Window.width, self.MAX_WIDTH)
        self.pos = ((Window.width - self.width) / 2, 0)

    def on_key_down(self, win, keyboard, keycode, text, modifiers):
        match keycode:
            case config.PAUSE_KEYCODE:
                self._toggle_clock()
            case config.ADD_MINUTE_KEYCODE:
                self._adjust_time(config.SECONDS_IN_MIN)
            case config.REMOVE_MINUTE_KEYCODE:
                self._adjust_time(-config.SECONDS_IN_MIN)
            case config.FULLSCREEN_KYCODE:
                self._toggle_full_screen()

    def on_request_close(self, *args, **kwargs):
        self._exit_popup.open()
        return True

class CountdownApp(App):
    def build(self):
        countdown_widget = CountdownWidget()
        Window.clearcolor = config.BACKGROUND_COLOR
        Window.bind(on_resize=countdown_widget.update_width)
        Window.bind(on_key_down=countdown_widget.on_key_down)
        Window.dispatch('on_resize', Window.width, Window.height)
        Window.bind(on_request_close=countdown_widget.on_request_close)
        return countdown_widget


if __name__ == '__main__':
    app = CountdownApp()
    app.run()
