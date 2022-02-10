import os
import sys

from PySide2.QtUiTools import QUiLoader
from qtpy.QtWidgets import QTreeWidgetItem, QLineEdit
from qtpy import QtWidgets

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TreePathWindow(object):
    def __init__(self, startpath, output_le: QLineEdit, sep: str = '/') -> None:
        super().__init__()
        self.selecte_element_path = None
        self.output_le = output_le
        self.sep = sep
        self.main_window = self.load_main_window_from_ui(startpath)
        self.path_tree = self.main_window.path_tree
        self.file_tree = self.main_window.file_tree
        self.path_le = self.main_window.path_le
        self.ok_btn = self.main_window.ok_btn
        self.canc_btn = self.main_window.canc_btn
        self.monitor_le = self.main_window.monitor_le

        self.history_path = []
        self.startpath = startpath
        self.update_history_path(startpath)
        current_tree, complete_path = self.update_tree_with_history(self.path_tree)
        self.load_tree_directory(current_tree, startpath)

    def join(self, str1, str2):
        if str1 == '' or str2 == '':
            return str2 + str1
        new_str = str1 + self.sep + str2
        return new_str

    def basename(self, element):
        list_dir = element.split(self.sep)
        return list_dir[-1]

    def update_history_path(self, path):
        self.history_path = path.split(self.sep)

        if '' in self.history_path:
            self.history_path.remove('')

    def update_tree_with_history(self, tree):
        complete_path = ''
        current_tree = tree
        for path in self.history_path:
            complete_path = self.join(complete_path, path)
            current_tree = QTreeWidgetItem(current_tree, [path])
            current_tree.setExpanded(True)
            self.path_tree.addTopLevelItem(current_tree)
        return current_tree, complete_path

    def double_click_path_element(self, item):
        try:
            self.monitor_le.setText('')
            if not item.isExpanded():
                if len(self.history_path) == 1 and self.sep == '\\':
                    self.history_path[0] = self.history_path[0].replace(self.sep, '')

                selected_direcotry = item.text(0)
                self.path_tree.clear()
                self.file_tree.clear()

                current_tree, complete_path = self.update_tree_with_history(self.path_tree)

                current_tree = QTreeWidgetItem(current_tree, [selected_direcotry])
                current_tree.setExpanded(True)
                self.path_tree.addTopLevelItem(current_tree)

                self.path_le.setText(self.join(complete_path, selected_direcotry))

                self.load_tree_directory(current_tree, self.join(complete_path, selected_direcotry))
                self.update_history_path(self.join(complete_path, selected_direcotry))
            else:
                self.update_history_path(self.path_le.text())
                index = self.history_path.index(item.text(0).replace(self.sep, ''))
                self.history_path = self.history_path[:index + 1]

                if len(self.history_path) == 1 and self.sep == '\\':
                    self.history_path[0] += self.sep

                self.path_tree.clear()
                self.file_tree.clear()
                current_tree, complete_path = self.update_tree_with_history(self.path_tree)
                self.load_tree_directory(current_tree, complete_path)
                self.path_le.setText(complete_path)
        except Exception as e:
            self.monitor_le.setText(str(e))

    def click_element(self, item):
        self.update_history_path(self.path_le.text())
        selected_element = item.text(0)

        complete_path = ''

        current_history = self.history_path
        if item.isExpanded():
            index = self.history_path.index(item.text(0).replace(self.sep, ''))
            current_history = self.history_path[:index]

        for path in current_history:
            complete_path = self.join(complete_path, path)

        if complete_path == '' and not self.sep in selected_element:
            self.selecte_element_path = selected_element + self.sep
        else:
            self.selecte_element_path = self.join(complete_path, selected_element)

    def change_complete_path_with_label(self):
        current_path = self.path_le.text()

        self.path_tree.clear()
        self.file_tree.clear()
        self.update_history_path(current_path)
        current_tree, complete_path = self.update_tree_with_history(self.path_tree)
        self.load_tree_directory(current_tree, current_path)

    def load_tree_directory(self, tree, startpath):
        for element in os.listdir(startpath):
            path_info = self.join(startpath, element)
            if os.path.isdir(path_info):
                parent_itm = QTreeWidgetItem(tree, [self.basename(element)])
                # parent_itm.setIcon(0, QIcon('assets/folder.ico'))
            else:
                parent_itm = QTreeWidgetItem(self.file_tree, [self.basename(element)])
                # parent_itm.setIcon(0, QIcon('assets/file.ico'))
            self.main_window.path_tree.addTopLevelItem(parent_itm)

    def get_selecte_element(self):
        self.output_le.setText(self.selecte_element_path)
        self.main_window.close()

    def close_app(self):
        self.main_window.close()



    def load_main_window_from_ui(self, startpath):
        loader = QUiLoader()

        def mainwindow_setup(w):
            w.setWindowTitle("Select file")

        window = loader.load("TreePathProject"+self.sep+"tree_path.ui", None)

        mainwindow_setup(window)
        window.path_le.setText(startpath)
        window.path_tree.setHeaderHidden(True)
        window.file_tree.setHeaderHidden(True)
        window.path_tree.itemDoubleClicked.connect(self.double_click_path_element)

        window.path_tree.itemClicked.connect(self.click_element)
        window.file_tree.itemClicked.connect(self.click_element)

        window.path_le.editingFinished.connect(self.change_complete_path_with_label)
        window.ok_btn.clicked.connect(self.get_selecte_element)
        window.canc_btn.clicked.connect(self.close_app)

        window.monitor_le.setText('')
        return window

    def show(self):
        self.main_window.show()


def main():
    # os.chdir(os.path.dirname(os.path.dirname(__file__)))
    startpath = os.getcwd()
    # startpath = r"C:\Users"

    app = QtWidgets.QApplication(sys.argv)
    temp = QLineEdit()
    tre_wnd = TreePathWindow(startpath, temp, os.sep)
    tre_wnd.show()
    app.exec_()

    print('path:', temp.text())
