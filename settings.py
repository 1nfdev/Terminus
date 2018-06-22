import sublime
import sublime_plugin


class SubtermEditSettingsListener(sublime_plugin.EventListener):
    def on_post_window_command(self, window, command, args):
        if command == "edit_settings":
            base = args.get("base_file", "")
            w = sublime.active_window()
            if base.endswith("sublime-keymap") and "/SublimelyTerminal/Default" in base:
                user_view = w.active_view()
                user_view.settings().erase("edit_settings_view")
                user_view.settings().set("subterm_edit_keybindings_view", 'user')
                w.focus_group(0)
                base_platform_view = w.active_view()
                base_platform_view.settings().erase("edit_settings_view")
                base_platform_view.settings().set("subterm_edit_keybindings_view", 'base')
                base_platform_view.set_read_only(True)
                w.run_command(
                    "open_file", {"file": "${packages}/SublimelyTerminal/Default.sublime-keymap"})
                base_view = w.active_view()
                base_view.settings().set("subterm_edit_keybindings_view", 'base')
                base_view.set_read_only(True)
                w.focus_group(1)

            elif base.endswith("SublimelyTerminal.sublime-settings"):
                w.focus_group(0)
                base_view = w.active_view()
                base_view.set_read_only(True)
                w.focus_group(1)

    def on_pre_close(self, view):
        """
        Grabs the window id before the view is actually removed
        """
        view_settings = view.settings()

        if view_settings.get('subterm_edit_keybindings_view') is None:
            return

        if view.window() is None:
            return

        view.settings().set('window_id', view.window().id())

    def on_close(self, view):
        """
        Closes the other settings view when one of the two is closed
        """

        view_settings = view.settings()

        if view_settings.get('subterm_edit_keybindings_view') is None:
            return

        window_id = view_settings.get('window_id')
        window = None
        for win in sublime.windows():
            if win.id() == window_id:
                window = win
                break

        if not window:
            return

        views = window.views()
        for other in views:
            if other.settings().get("subterm_edit_keybindings_view"):
                def close_view():
                    window.focus_view(other)
                    window.run_command("close")
                    if len(window.views()) == 0 and len(window.folders()) < 1:
                        if window.id() == sublime.active_window().id():
                            window.run_command("close_window")

                # Run after timeout so the UI doesn't block with the view half closed
                sublime.set_timeout(close_view, 10)


class SubtermEditSettingsCommand(sublime_plugin.WindowCommand):
    """
    For some reasons, the command palette doesn't trigger `on_post_window_command` for
    dev version of Sublime Text. The command palette would call `gs_edit_settings` and
    subsequently trigger `on_post_window_command`.
    """
    def run(self, **kwargs):
        self.window.run_command("edit_settings", kwargs)
