from kivy.app import App
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from  google_drive import DriveManager
import sys
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.properties import StringProperty, ListProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.filechooser import FileChooser, FileChooserListLayout, FileChooserListView
from kivy.uix.modalview import ModalView
import os
import json

SELECTED_FILE = {"file_id": None, "filename": "", "status": "None"}


class Screens(ScreenManager):
    pass


class WelcomeScreen(Screen):

    def on_enter(self):
        self.vrf = Clock.schedule_interval(self.verify_login, .2)
        #self.drive = DriveManager()
        #self.drive.func = "login"
        #self.drive.start()

        self.drive = DriveManager()
        self.drive.func = "login"
        self.drive.start()
        print(f"ola o rweu;tado {self.drive.service}")

    def verify_login(self, event):
        #print(drive.proccessing)
        if not self.drive.proccessing:
            self.drive.novo = "Denny"
            print("Terminou")
            self.vrf.cancel()

            print(f"ola o rweu;tado {self.drive.service}")  
            self.parent.parent.drive = self.drive.service
            print(self.parent.parent.drive)

            self.parent.current = "content"


class ContentScreen(Screen):
    def on_pre_enter(self):
        self.drive = DriveManager(self.parent.parent.drive)
        self.drive.func = "get_files"
        self.drive.start()
        self.box = self.parent.ids.files
    
        self.vrf = Clock.schedule_interval(self.verify_files, .2)


    def on_leave(self):
        print(self.children[0].children[0].children[1].children[0].clear_widgets())

    def verify_files(self, event):
        if not self.drive.proccessing:
            print("Terminou de carregar os files")
            self.vrf.cancel()
            print(f"Tamanho {len(self.drive.files)}")
            for file in self.drive.files:
                label = LabelFile(file=file)
                self.box.add_widget(label)

    def show_files(self, button):
        print(self.parent)
        if button == "files":
            self.parent.current = "content"
        else:
            self.parent.current = "uploads"

class FileInfo(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.placeholder = ""


class LoginScreen(Screen):
    def on_enter(self):
        pass


class ButtonOpt(ButtonBehavior, Label):
    press_state = ListProperty([.5, .5, .8, 1])
    release_state = ListProperty([1, 1, 1, 1])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.render()
    def render(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.press_state)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def on_press_state(self, *args):
        self.render()
    
    def on_pos(self, *args):
        self.render()

    def on_size(self, *args):
        self.render()

    def on_press(self):
        self.press_state, self.release_state = self.release_state, self.press_state
    
    def on_release(self):
        self.press_state, self.release_state = self.release_state, self.press_state


class DownloadButton(ButtonOpt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def on_release(self, *args):
        super().on_release()

        #self.service = self.parent.parent.parent.parent.parent.parent.parent.drive
        self.service = App.get_running_app().root.drive
        
        #self.drive = DriveManager(self.service, SELECTED_FILE)
        #self.drive.func = "download"
        #self.drive.start()

        #self.vrf = Clock.schedule_interval(self.check_status, 0.3)
        self.list_box = App.get_running_app().root.children[0].children[0].children[0].children[0].tab_list[0].content.children[0].children[0]
        print(self.list_box.check())

    def check_status(self, event):
        if self.drive.proccessing:
            print(self.drive.downloader)
        else:
            self.vrf.cancel()


class MenuButtons(ButtonOpt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    


class LabelFile(ButtonBehavior, BoxLayout):
    text = StringProperty("sdadsad")
    cor = ListProperty([1,1,1,1])
    cor2 = ListProperty([.2, .2, .2, 1])
    def __init__(self, file, **kwargs):
        super().__init__(**kwargs)
        self.file = file
        self.label = LabelFileText(text=self.file["name"])
        self.add_widget(self.label)
        self.children[1].source = self.file["iconLink"]
        #self.color="black"
        #self.size_hint_y=None
        #self.height=40
        print(self.color)
        #self.on_press = self.selectFile
        self.render()

    def on_press(self, *args):
        global SELECTED_FILE
        SELECTED_FILE = {"file_id": self.file["id"], "filename":self.file["name"], "status": "None"}

        self.cor, self.cor2 = self.cor2, self.cor
        
        for child in self.parent.children:
            if child != self:
                child.cor = 1, 1, 1,1 
                child.cor2 = .2, .2, .2, 1
        #print(App.get_running_app().root.children[0].children[0].children[0].children[0].children[0].children[0].children[0].children)
        print(self.parent.parent.parent.children[0].children[0].ids)
        self.fileinfo_widget = self.parent.parent.parent.children[0].children[0]
        self.fileinfo_widget.ids.filename.text = f"Nome: {self.file['name']}"
        self.fileinfo_widget.ids.file_owner.text = f"Proprietario: {self.file['owners'][0]['displayName']}"
        self.fileinfo_widget.ids.create_date.text = f"Data de criacao: {self.file['createdTime']}"
        self.fileinfo_widget.ids.modified_date.text = f"Data de ultima modificacao: {self.file['modifiedTime']}"
        try:
            self.file_size = int(self.file["size"]) * 0.000001
            if int(self.file_size) <=0:
                self.file_size = f"{self.file_size:.2f} Kb"
            elif 0 <= int(self.file_size) <= 1023:
                self.file_size = f"{self.file_size:.2f} MB"
            else:
                self.file_size = f"{self.file_size:.2f} GB"
            self.fileinfo_widget.ids.size.text = f"Tamanho: {self.file_size}"

        except:
            self.fileinfo_widget.ids.size.text = f"Tamanho: desconhecido"

        print(self.children[1].source)

    def on_release(self, *args):
        pass
        #self.cor2, self.cor = self.cor, self.cor2

    def on_cor(self, *args):
        self.render()

    def render(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.cor)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(pos=self.update_rect, size=self.update_rect)
    
    def selectFile(self):
        self.cor, self.cor2 = self.cor2, self.cor
        for child in self.parent.children:
            if child == self:
                
                print(self.label.text)        
            else:
                child.label.color = [1, 1, 1, 1]
    
    def update_rect(self, event, value):
        self.rect.pos = event.pos
        self.rect.size = event.size


class MainBox(BoxLayout):
    drive = None
    marked_file = None

    def __init__(self):
        super().__init__()

    def show_files(self, button):
        if button == "files":
            self.children[0].current = "content"
        else:
            self.children[0].current = "uploads"


class LabelFileText(Label):

    def __init__(self, text):
        super().__init__()
        self.text = text
        

class ScrollViewFiles(ScrollView):
    pass


"""Upload Layout"""


class UploadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        print("Entrando nos uploads")


class UploadMainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files = []
        self.files_boxs = []
        self.uploading = False
        
    def upload_files(self):
        if len(self.files) > 0:
            for pos, file in enumerate(self.files):
                print(f"Uploading {file}")
                self.files[pos] = {f"name":file, "status": "None"}
            self.service = App.get_running_app().root.drive
            self.drive = DriveManager(self.service, files=self.files)
            self.drive.func = "upload"
            self.drive.start()
            self.vrf = Clock.schedule_interval(self.check_upload, .1)
        else:
            modal = ModalView(size_hint=(None, None), width=300, height=50)
            modal.add_widget(Label(text="Seleciione arqivos para upload"))
            modal.open()
    def check_upload(self, event):

        for pos, file in enumerate(self.drive.files):
            print(file["status"])
            self.files_boxs[pos].ids.status.text = file["status"]
        if not self.drive.proccessing:
            self.files = []
            self.files_boxs = []
            self.vrf.cancel()

    def openfilechooser(self):
        self.modal = ModalView(size_hint=(.8, .8))
        self.modal.padding = 5

        self.file_widget = BoxLayout(size_hint=(.8, .9))
        self.file_widget.orientation = "vertical"
        self.filec = FileChooserView()
        self.file_widget.add_widget(self.filec)

        self.modal.add_widget(self.file_widget)

        #Buttons
        self.boxbtn = BoxLayout(size_hint=(.8, .1))
        self.addbtn = Button(text="Adicionar")
        self.addbtn.on_press = self.selectfiles

        self.cancelbtn = Button(text="Terminar ou cancelar")
        self.cancelbtn.on_press = self.closefilechooser

        self.boxbtn.add_widget(self.addbtn)
        self.boxbtn.add_widget(self.cancelbtn)
        self.file_widget.add_widget(self.boxbtn)
        self.modal.open()


    def closefilechooser(self):
        self.modal.dismiss()


    def selectfiles(self):
        #print(f"Ficheiros selecionados {self.filec.selection}")
        #self.modal.dismiss()
        self.filec.on_submit()

class FilesToUploadScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FilesToUploadList(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FileChooserView(FileChooser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(FileChooserListLayout())


    def on_submit(self, *args):
        
        #print("Submetendo")
        #print(self.selection)
        #print(self.parent.parent.dismiss())
        #print(App.get_running_app().root.children[0].children[0].children[0].children[0].children[0].children[0].children[1].children[0])

        select_files = []
        
        
        list_widget = App.get_running_app().root.children[0].children[0].children[0].children[0].children[0].children[0].children[1].children[0]
        for file in self.selection:
            
            if not file in list_widget.parent.parent.files:
                print(list_widget.parent.parent.files.append(file))
                file_label = FileToUpload(file, self.get_nice_size(file))
                list_widget.parent.parent.files_boxs.append(file_label)
                list_widget.add_widget(file_label)


class FileToUpload(BoxLayout):
    def __init__(self,text, size, **kwargs):
        super().__init__(**kwargs)
        print(self.ids.text)
        self.ids.text.text = os.path.split(text)[-1]
        self.ids.size.text = size


"""DOWNLOADS LAYOUT"""


class DownloadsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ScrollDownloadList(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.box = ListBox()
        
        self.add_widget(self.box)


class ListBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.files_to_download_list = []
    
    def check(self):
        print(SELECTED_FILE)
        self.dw_box = DownloadBox(file=SELECTED_FILE, download=True)
        self.add_widget(self.dw_box)


class DownloadBox(BoxLayout):
    
    def __init__(self,file, download=False, **kwargs):
        super().__init__(**kwargs)
        self.text = file["filename"]
        self.ids.name.text = self.text

        if download:    
            self.service = App.get_running_app().root.drive
            self.drive = DriveManager(self.service, file)
            self.drive.func = "download"
            self.drive.start()

            self.vrf = Clock.schedule_interval(self.check_download, 0.3)

    def check_download(self, event):
        if not self.drive.proccessing:
            self.ids.status.text = "Completo"
            self.vrf.cancel()
        else:
            self.ids.status.text = "Em progresso"


"""AUTO BACKUP"""


class BoxBtn(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AutoBackupMainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initUi()
        if not os.path.exists("files.json"):
            open("files.json", "w").close()
        self.files = []
        self.files_to_backup = []
        try:
            with open("files.json", "r") as files_json:
                for file in json.load(files_json):
                    self.files.append(file)
                    self.scrl.children[0].add_widget(FileLabelAuto(text=file["name"]))
        except Exception as error:
            print(error)
        self.ck_files = Clock.schedule_interval(self.check_files, .2)

    def initUi(self):
        self.add_widget(Label(text="Backups automaticos", size_hint=(1, .05)))
        self.add_widget(BoxBtn())
        self.scrl = ScrollAuto()
        self.add_widget(self.scrl)

    def check_files(self, event):
        for pos, file in enumerate(self.files):
            if file["modification_date"] < os.path.getmtime(file["name"]):
                self.files_to_backup.append({"name": file["name"], "status": "None"})
                self.files[pos]["modification_date"] = os.path.getmtime(file["name"])
                print("Arquivo modificado")
        with open("files.json", "w") as files_json:
            json.dump(self.files, files_json)
        if len(self.files_to_backup) != 0:
            print(self.files_to_backup)
            self.service = App.get_running_app().root.drive
            self.drive = DriveManager(self.service, files=self.files_to_backup)
            self.drive.func = "upload"
            self.drive.start()
            self.files_to_backup = []
            print(self.drive)

    def choose_files(self):
        self.modal = ModalView(size_hint=(.5, .5))
        self.main_box = BoxLayout()
        self.main_box.orientation = "vertical"
        self.file_c = FileChooserAuto()
        self.file_c.on_submit = self.add_file_click
        self.file_c.size_hint = (1, .9)

        self.modal.add_widget(self.main_box)
        self.main_box.add_widget(self.file_c)
        self.box_btn = BoxLayout(size_hint=(1, .1))

        self.add_btn = Button(text="Adicionar")
        self.add_btn.on_release = self.add_files

        self.box_btn.add_widget(self.add_btn)
        self.cancel = Button(text="Concluir ou cancelar")
        self.cancel.on_release = self.close_file
        self.box_btn.add_widget(self.cancel)

        self.main_box.add_widget(self.box_btn)
        self.modal.open()

    def add_file_click(self, file, event2):
        print(self.scrl.children)
        if file[0] not in self.files:
            print(self.files)
            self.scrl.children[0].add_widget(FileLabelAuto(text=file[0]))
            self.files.append({"name": file[0], "modification_date": os.path.getmtime(file[0])})
        with open("files.json", "w") as files_json:
            json.dump(self.files, files_json)

    def add_files(self):
        for file in self.file_c.selection:
            if file not in self.files:
                self.scrl.children[0].add_widget(FileLabelAuto(text=file))
                self.files.append({"name": file, "modification_date": os.path.getmtime(file)})
        with open("files.json", "w") as files_json:
            json.dump(self.files, files_json)


        self.modal.dismiss()

    def close_file(self):
        self.modal.dismiss()


class ListBoxAutoBackup(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FileChooserAuto(FileChooser):
    def __init__(self):
        super().__init__()

        self.add_widget(FileChooserListLayout())


class FileLabelAuto(Label):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class ScrollAuto(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Drive(App):
    def build(self):
        return MainBox()

    def on_stop(self):

        sys.exit()


def main():
    app = Drive()
    app.run()


if __name__ == "__main__":
    main()