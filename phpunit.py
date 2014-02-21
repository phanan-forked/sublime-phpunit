import os
import sys
import shlex
import ntpath
import subprocess
import sublime
import sublime_plugin

class RunPhpunitTestCommand(sublime_plugin.WindowCommand):

    def run(self, *args, **kwargs):
        file_name = self.window.active_view().file_name()
        phpunit_config_path = self.find_phpunit_config(file_name)

        file_name = file_name.replace(' ', '\ ')
        phpunit_config_path = phpunit_config_path.replace(' ', '\ ')

        self.run_in_terminal('cd ' + phpunit_config_path + ' && phpunit ' + file_name)

    def find_phpunit_config(self, file_name):
        phpunit_config_path = file_name
        found = False
        while found == False:
            phpunit_config_path = os.path.abspath(os.path.join(phpunit_config_path, os.pardir))
            found = os.path.isfile(phpunit_config_path + '/phpunit.xml') or phpunit_config_path == '/'
        return phpunit_config_path

    def run_in_terminal(self, command):
        osascript_command = 'osascript '
        osascript_command += '"' + sublime.packages_path() + '/User/run_command.applescript"'
        osascript_command += ' "' + command + '"'
        osascript_command += ' "PHPUnit Tests"'
        os.system(osascript_command)
        # subprocess.Popen("""osascript -e 'tell application "Sublime Text" to activate' """, shell=True)


class FindMatchingTestCommand(sublime_plugin.WindowCommand):

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def run(self, *args, **kwargs):
        file_name = self.window.active_view().file_name()
        file_name = self.path_leaf(file_name)
        file_name = file_name[0:file_name.find('.')]
        tab_target = 0

        if 'Test' not in file_name:
            file_name = file_name + 'Test'
        else:
            # Strip 'Test' and add '.' to force matching the non-test file
            file_name = file_name[0:file_name.find('Test')] + '.'
            tab_target = 1

        # Big dirty macro-ish hack. Eventually I should just open the file in some sort of
        # logical way.
        self.window.run_command("set_layout", {"cells": [[0, 0, 1, 1], [1, 0, 2, 1]], "cols": [0.0, 0.5, 1.0], "rows": [0.0, 1.0]})
        self.window.run_command("focus_group", {"group": tab_target})
        self.window.run_command("show_overlay", {"overlay": "goto", "text": file_name, "show_files": "true"})
        self.window.run_command("move", {"by": "lines", "forward": False})

        # This is a dirty hack to get it to switch files... Can't simulate 'Enter'
        # but triggering the overlay again to close it seems to have the same effect.
        self.window.run_command("show_overlay", {"overlay": "goto", "show_files": "true"})
        self.window.run_command("focus_group", {"group": 0})
        self.window.run_command("focus_group", {"group": tab_target})

