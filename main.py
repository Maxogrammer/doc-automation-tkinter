from os import path, set_inheritable, walk
from json import load, dump
import datetime, csv
from pydoc import doc
from tkinter import *
from tkinter import filedialog, messagebox
window = Tk()
window.resizable(True, True)
window.title("Создатель запросов")
window.state("zoomed")
window.configure(background="#E5E5E5")
FONT = ('Arial', 10)
FONT_HEAD = ('Arial', 10, 'bold')
DATA_VALUES = {
 'ООО «Аудируемое лицо»': '""',
 'Рук. проекта': '""',
 'Дательный падеж': '""',
 'Телефон': '""',
 'Почта': '""',
 'Дата': '""',
 'Крайний срок': '""',
 'Год': '""',
 'Период(с)': '""',
 'Период(по)': '""',
 'Количество': '""'}
DATA_EXTRA = {
 'ООО «Аудируемое лицо»': '"Организация"',
 'Рук. проекта': '"Руководитель аудиторской группы"',
 'Дательный падеж': '"ФИО рук. проекта в дательном падеже"',
 'Телефон': '"Телефон руководителя аудиторской группы"',
 'Почта': '"Почта руководителя аудиторской группы"',
 'Дата': '"Дата направления запроса"',
 'Крайний срок': '"Срок, к которому необходимо предоставить документы"',
 'Год': '"Год, за который проводится аудит"',
 'Период(с)': '"Период, за который могли произойти изменения(начало)"',
 'Период(по)': '"Период, за который могли произойти изменения(конец)"',
 'Количество': '"Количество участников аудиторской группы"'}
INFO_PATH = "info.json"
SETTINGS_PATH = "settings.json"
with open(SETTINGS_PATH, "r", encoding="utf-8") as settigns:
    settings_dict = load(settigns)
    PATTERNS_FOLDER = settings_dict["patterns_folder"]
    SAVE_ON_CLOSE = settings_dict["save_on_close"]
    COLOR_TO_REPLACE = settings_dict["color_to_replace"]
    BG = settings_dict["bg_color"]
    AUDITORS_DATA = settings_dict["auditors_data"]

class Grid:

    def __init__(self, frame: Frame, indent_x=5, indent_y=5, anchor=NW, side=LEFT) -> None:
        """
        Create objects.
        """
        self.frame = Frame(frame, bg=BG, width=50,
          height=40)
        self.indent_x = indent_x
        self.indent_y = indent_y
        self.anchor = anchor
        self.side = side
        self.widgets = []

    def add_widget(self, row: int, column: int, widget) -> None:
        """
        Add(append) widget.
        """
        self.widgets.append((widget, row, column))

    def place(self) -> None:
        """
        Place objects.
        """
        for widget_tuple in self.widgets:
            widget = widget_tuple[0]
            row = widget_tuple[1]
            column = widget_tuple[2]
            widget.grid(row=row, column=column, padx=(self.indent_x),
              pady=(self.indent_y))
        else:
            self.frame.pack(anchor=(self.anchor), side=LEFT, padx=10,
              pady=10)


class Buttons(Grid):

    def add_widget(self, row, column, string, command):
        """
        Add(append) button.
        """
        sv = StringVar((self.frame), value=string)
        button = Button((self.frame), font=FONT, relief=GROOVE,
          textvariable=sv,
          command=command)
        self.widgets.append((button, row, column))


class Path:

    def __init__(self) -> None:
        """
        Create objects,
        configure and place them.
        """
        self.frame = LabelFrame(window, font=FONT_HEAD,
          bg=BG,
          width=300,
          height=70,
          text="Путь")
        self.entry = Entry((self.frame), width=155, font=FONT)
        self.entry.bind("<FocusOut>", self.command_save)
        self.entry.bind("<Return>", self.command_save)
        self.button_browse = Button((self.frame), text="Выбрать путь",
          font=FONT,
          height=1,
          relief=GROOVE,
          command=(self.browse_files))
        self.button_clear = Button((self.frame), text="Сбросить",
          font=FONT,
          height=1,
          relief=GROOVE,
          command=(self.command_clear))
        self.load()
        self.place()

    def load(self) -> None:
        """
        Set value for the entry.
        """
        with open(INFO_PATH, "r", encoding="utf-8") as params:
            path = load(params)["changeable"]["path"]
        sv = StringVar(self.frame, path)
        self.entry.configure(textvariable=sv)

    def command_save(self, event=None):
        """
        Save entry's value.
        """
        path = self.entry.get()
        if not path.endswith("/"):
            path += "/"
        with open(INFO_PATH, "r", encoding="utf-8") as info:
            info_dict = load(info)
            info_dict["changeable"]["path"] = path
        with open(INFO_PATH, "w", encoding="utf-8") as info:
            dump(info_dict, info, indent=4, ensure_ascii=False)

    def command_clear(self):
        self.entry.delete(0, END)
        string_var_text = StringVar(self.frame, "/")
        self.entry.configure(textvariable=string_var_text)

    def browse_files(self) -> None:
        """
        Open file explorer window.
        """
        folder_name = filedialog.askdirectory(mustexist=True, title="Выберите папку")
        if not folder_name.endswith("/"):
            folder_name += "/"
        if folder_name != "":
            string_var_text = StringVar(self.frame, folder_name)
            self.entry.configure(textvariable=string_var_text)

    def place(self) -> None:
        """
        Place objects.
        """
        self.frame.pack(anchor=NW, padx=20)
        self.button_clear.pack(anchor=NW, side=LEFT, padx=14, pady=10)
        self.button_browse.pack(anchor=NE, side=RIGHT, padx=5, pady=10)
        self.entry.pack(side=LEFT, padx=10)


class Choose:

    def __init__(self, parent, frame) -> None:
        """
        Create objects.
        """
        self.selected = 0
        self.item_index = 0
        self.items = self.load()
        self.parent = parent
        self.frame = LabelFrame(frame, text="Выберете из списка",
          font=FONT_HEAD,
          bg=BG)
        self.scrollbar = Scrollbar((self.frame), width=20,
          orient=VERTICAL)
        self.listbox = Listbox((self.frame), width=40,
          height=16,
          font=FONT,
          yscrollcommand=(self.scrollbar.set))
        self.listbox.bind("<<ListboxSelect>>", self.select)
        self.listbox.bind("<Double-Button-1>", self.save)
        for item in self.items.values():
            self.listbox.insert(END, item)
        else:
            self.scrollbar.configure(command=(self.listbox.yview))

    def load(self) -> dict:
        """
        Load items
        for the listbox.
        """
        pass

    def get_selected_item(self, evt: Event) -> tuple:
        """
        Return selected document
        and its index from the listbox.
        """
        widget = evt.widget
        try:
            index = int(widget.curselection()[0])
            item = self.items[index]
        except IndexError:
            pass
        else:
            return (
             item, index)

    def select(self, evt: Event) -> None:
        """
        It is called when
        any of the listbox's
        element is selected.

        Remove old element
        (which was chosen before)
        and place new element.
        """
        try:
            item, index = self.get_selected_item(evt)
            self.items[index] = item
        except TypeError:
            pass
        else:
            self.selected = index

    def save(self, evt: Event) -> None:
        """
        Save chosen item.
        """
        try:
            item, index = self.get_selected_item(evt)
            self.items[index] = item
        except TypeError:
            pass
        else:
            self.selected = index
            self.parent.add_item(item)
            self.frame.pack_forget()

    def place(self) -> None:
        """
        Place objects.
        """
        self.listbox.pack(anchor=NW, side=LEFT, padx=10, pady=10, fill=Y)
        self.scrollbar.pack(anchor=NW, side=LEFT, pady=10, fill=Y)
        self.frame.pack(anchor=N, side=TOP, pady=4)


class Saved:

    def __init__(self, parent) -> None:
        """
        Create objects.
        """
        self.window = Tk()
        self.window.resizable(True, True)
        self.window.geometry("340x340")
        self.window.title("Сохранённое")
        self.window.configure(background="#E5E5E5")
        self.window.withdraw()
        self.parent = parent
        self.selected = 0
        self.item_index = 0
        self.items = self.load()
        self.frame = LabelFrame((self.window), text="Выберете из списка",
          font=FONT_HEAD,
          bg=BG)
        self.scrollbar = Scrollbar((self.frame), width=20,
          orient=VERTICAL)
        self.listbox = Listbox((self.frame), width=40,
          height=16,
          font=FONT,
          yscrollcommand=(self.scrollbar.set))
        self.listbox.bind("<<ListboxSelect>>", self.select)
        self.listbox.bind("<Double-Button-1>", self.save)
        for item in self.items.values():
            self.listbox.insert(END, item["ФИО руководителя аудиторской группы"])
        else:
            self.scrollbar.configure(command=(self.listbox.yview))

    def load(self) -> dict:
        """
        Load items
        for the listbox.
        """
        with open(AUDITORS_DATA, "r", encoding="utf-8-sig") as data:
            reader = csv.reader(data)
            items_dict = {}
            i = 0
            for row in reader:
                if i != 0:
                    values_dict = {}
                    for i in range(len(keys)):
                        key = keys[i]
                        value = row[i]
                        values_dict[key] = value
                    else:
                        items_dict[self.item_index] = values_dict
                        self.item_index += 1

                else:
                    keys = row
                    i = 1

        return items_dict

    def get_selected_item(self, evt: Event) -> tuple:
        """
        Return selected document
        and its index from the listbox.
        """
        widget = evt.widget
        try:
            index = int(widget.curselection()[0])
            item = self.items[index]
        except IndexError:
            pass
        else:
            return (
             item, index)

    def select(self, evt: Event) -> None:
        """
        It is called when
        any of the listbox's
        element is selected.

        Remove old element
        (which was chosen before)
        and place new element.
        """
        try:
            item, index = self.get_selected_item(evt)
            self.items[index] = item
        except TypeError:
            pass
        else:
            self.selected = index

    def save_new(self) -> None:
        self.add_frame.pack_forget()
        data = {}
        for field in self.fields.values:
            key = field.value[0]["text"]
            try:
                value = field.value[1].get()
            except TypeError:
                value = field.value[1].get(1.0, END)
            else:
                data[key] = value
        else:
            for value in data.values():
                if value.strip() == "":
                    return None
                self.items[self.item_index] = [value for value in data.values()]
                self.item_index += 1
                self.listbox.insert(END, self.items[self.item_index - 1][0])

    def save(self, evt: Event) -> None:
        """
        Save chosen item.
        """
        try:
            item, index = self.get_selected_item(evt)
            self.items[index] = item
        except TypeError:
            pass
        else:
            self.selected = index
            self.parent.add_item(item)
        self.window.withdraw()

    def place(self) -> None:
        """
        Place objects.
        """
        self.listbox.pack(anchor=NW, side=LEFT, padx=10, pady=10, fill=Y)
        self.scrollbar.pack(anchor=NW, side=LEFT, pady=10, fill=Y)
        self.frame.pack(anchor=NW, side=LEFT, padx=15, pady=5)
        self.window.deiconify()


class Field:

    def __init__(self, frame, name, value='', t_width=46, t_height=1, choose=False, parent=None):
        """
        Create objects,
        configure and place them.
        """
        self.t_width = t_width
        self.t_height = t_height
        self.choose = choose
        self.frame = Frame(frame, background="#E5E5E5")
        label = Label((self.frame), text=name, font=FONT,
          bg=BG,
          width=(self.t_width),
          height=1)
        if self.t_height == 1:
            text = Entry((self.frame), font=FONT,
              width=(self.t_width))
            text.insert(END, value)
        else:
            text = Text((self.frame), font=FONT,
              width=(self.t_width),
              height=(self.t_height))
            text.insert(END, value)
        label.bind("<Enter>", self.enter)
        label.bind("<Leave>", self.leave)
        self.value = [
         label, text]
        if self.choose:
            self.choose_button = Button((self.frame), relief=GROOVE, text="◦◦◦",
              font=FONT,
              command=(self.place_choose))
            self.value.append(self.choose_button)
            self.parent = parent
            self.saved = Saved(self)

    def enter(self, evt):
        extra_info = DATA_EXTRA[self.value[0]["text"]]
        self.value[0].configure(text=extra_info)

    def leave(self, evt):
        for key, value in DATA_EXTRA.items():
            if value == self.value[0]["text"]:
                self.value[0].configure(text=key)

    def place_choose(self) -> None:
        self.saved.place()

    def add_item(self, item):
        replace_dict = {'ФИО руководителя аудиторской группы в дательном падеже':"Дательный падеж",
         'ФИО руководителя аудиторской группы':"Рук. проекта"}
        item_replaced = {}
        for key, value in item.items():
            if key in replace_dict.keys():
                item_replaced[replace_dict[key]] = value
            else:
                item_replaced[key] = value
        else:
            item = item_replaced
            for field in self.parent.values:
                label = field.value[0]["text"]
                if label in item.keys():
                    entry = field.value[1]
                    entry.delete(0, END)
                    entry.insert(0, item[label])

    def delete(self) -> None:
        """
        Delete(remove) objects
        from the window.
        """
        for value in self.value:
            value.pack_forget()
        else:
            self.frame.pack_forget()

    def delete_window(self) -> None:
        """
        Delete windows.
        """
        try:
            self.saved.window.destroy()
        except:
            pass


class Fields:

    def __init__(self, frame, data) -> None:
        """
        Create objects.
        """
        self.data = data
        self.frame = Frame(frame, bg=BG)
        self.values = []

    def add_field(self, key: str, value: str) -> None:
        """
        Add(append) field.
        """
        if key == "Рук. проекта":
            choose = True
            parent = self
        else:
            choose = False
            parent = None
        field = Field((self.frame), key, value, choose=choose, parent=parent)
        self.values.append(field)

    def create_fields(self) -> None:
        try:
            self.data.refresh_time()
        except:
            pass
        else:
            for key, value in self.data.data.items():
                self.add_field(key, value)

    def place(self) -> None:
        """
        Place objects.
        """
        row = 0
        column = 0
        for field in self.values:
            for value in field.value:
                if isinstance(value, Label):
                    if value["text"] == "Дата":
                        row = 0
                        column = 1
                value.pack(anchor=NW, padx=5, pady=3)
            else:
                field.frame.grid(row=row, column=column)
                row += 1

        else:
            self.frame.pack(anchor=NW, side=LEFT, padx=20, pady=5)

    def delete(self) -> None:
        for field in self.values:
            for value in field.value:
                value.pack_forget()
            else:
                field.frame.pack_forget()

        else:
            self.frame.pack_forget()


class Data:

    def __init__(self) -> None:
        """
        Create objects.
        """
        self.frame = LabelFrame(window, text="Данные",
          font=FONT_HEAD,
          bg=BG,
          width=50,
          height=40)
        self.buttons = Buttons((self.frame), side=TOP)
        self.buttons.add_widget(0, 0, "Сбросить", self.reset)
        self.fields = Fields(self.frame, self)
        self.load()

    def get_values(self) -> dict:
        """
        Return all fields.
        """
        data = {}
        period = ""
        for field in self.fields.values:
            key = field.value[0]["text"]
            try:
                value = field.value[1].get()
            except TypeError:
                value = field.value[1].get(1.0, END)
            else:
                if key == "Период(с)":
                    period += "с " + value
                else:
                    if key == "Период(по)":
                        period += " по " + value
                        data["Период"] = period
                data[key] = value
        else:
            return data

    def refresh_time(self) -> None:
        """
        Replace date in data.
        """
        self.current_date = datetime.date.today()
        data = {}
        data["Дата"] = self.current_date.strftime("%d.%m.%Y")
        data["Год"] = self.current_date.strftime("%Y")
        data["Крайний срок"] = (self.current_date + datetime.timedelta(days=3)).strftime("%d.%m.%Y")
        data["Период(с)"] = data["Дата"]
        data["Период(по)"] = data["Крайний срок"]
        for key, value in data.items():
            if key in self.data.keys():
                self.data[key] = value

    def load(self) -> None:
        """
        Set default values
        for the entries.
        """
        with open(INFO_PATH, "r", encoding="utf-8") as info:
            data = load(info)["changeable"]["data"]
        
        self.data = {}
        for key, value in DATA_VALUES.items():
            self.data[key] = value
        else:
            for key in self.data.keys():
                if key in data.keys():
                    self.data[key] = data[key]
                
                self.refresh_time()
                self.fields.create_fields()

    def save(self) -> None:
        with open(INFO_PATH, "r", encoding="utf-8") as info:
            info_dict = load(info)
        row_info_dict = self.get_values()
        odd = []
        for key, value in row_info_dict.items():
            if key not in odd:
                info_dict["changeable"]["data"][key] = value
        with open(INFO_PATH, "w", encoding="utf-8") as info:
            dump(info_dict, info, indent=4, ensure_ascii=False)

    def reset(self) -> None:
        """
        Reset data.
        """
        self.data = {}
        for key, value in DATA_VALUES.items():
            self.data[key] = value
        else:
            self.fields.delete()
            self.fields = Fields(self.frame, self)
            self.fields.create_fields()
            self.place()

    def delete(self) -> None:
        """
        Delete(remove) objects
        from the window.
        """
        for field in self.fields.values:
            field.delete()
        else:
            self.frame.pack_forget()

    def delete_windows(self) -> None:
        """
        Delete(remove) windows.
        """
        for field in self.fields.values:
            field.delete_window()

    def place(self) -> None:
        """
        Place objects.
        """
        self.buttons.place()
        self.fields.place()
        self.frame.pack(anchor=NW, side=LEFT, padx=20, pady=5)


class Patterns(Choose):

    def load(self) -> dict:
        patterns_dict = {}
        for root, dirs, files in walk(PATTERNS_FOLDER):
            for filename in files:
                if filename.endswith(".docx") and not filename.startswith("~"):
                    pattern_name = filename[:-5]
                    patterns_dict[self.item_index] = pattern_name
                    self.item_index += 1
        return patterns_dict

    def save(self, evt: Event) -> None:
        try:
            item, index = self.get_selected_item(evt)
            self.items[index] = item
        except TypeError:
            pass
        else:
            self.selected = index
            self.parent.add_item(item)
            self.frame.pack_forget()


class PatternsList:

    def __init__(self, create_command) -> None:
        """
        Create objects
        and place them.
        """
        self.patterns = {}
        self.selected = 0
        self.pattern_index = 0
        self.frame = LabelFrame(window, text="Шаблоны",
          font=FONT_HEAD,
          bg=BG)
        self.patterns_list_frame = Frame((self.frame), bg=BG)
        self.scrollbar = Scrollbar((self.patterns_list_frame), width=20,
          orient=VERTICAL,
          bg=BG)
        self.listbox = Listbox((self.patterns_list_frame), width=34,
          height=15,
          font=FONT,
          yscrollcommand=(self.scrollbar.set))
        self.listbox.bind("<<ListboxSelect>>", self.select)
        self.listbox.bind("<Button-3>", self.bind_delete)
        self.scrollbar.configure(command=(self.listbox.yview))
        self.buttons = Buttons(self.patterns_list_frame)
        self.buttons.add_widget(0, 0, "Сбросить", self.command_clear)
        self.buttons.add_widget(1, 0, "Добавить", self.choose_pattern)
        self.choose_patterns = Patterns(self, self.frame)
        self.create_button_frame = Frame(self.frame)
        self.create_button = Button((self.create_button_frame), text="СОЗДАТЬ",
          font=FONT_HEAD,
          relief=GROOVE,
          command=create_command)
        self.change_create_button_state()
        self.create_button.pack(anchor=N, side=TOP)

    def get_selected_pattern(self, evt: Event) -> tuple:
        """
        Return selected document
        and its index from the listbox.
        """
        widget = evt.widget
        try:
            index = int(widget.curselection()[0])
            pattern = self.patterns[index]
        except IndexError:
            pass
        else:
            self.change_create_button_state()
            self.create_button.pack_forget()
            self.create_button.pack(anchor=N, side=TOP, pady=5)
            return (pattern, index)

    def select(self, evt: Event) -> None:
        """
        It is called when
        any of the listbox's
        element is selected.

        Remove old element
        (which was chosen before)
        and place new element.
        """
        try:
            pattern, index = self.get_selected_pattern(evt)
            self.patterns[index] = pattern
        except TypeError:
            pass
        else:
            if index != self.selected:
                self.listbox.delete(0, END)
                for pattern in self.patterns.values():
                    self.listbox.insert(END, pattern)
                else:
                    self.selected = index

    def choose_pattern(self) -> None:
        """
        Choose pattern.
        """
        self.create_button_frame.pack_forget()
        self.choose_patterns.place()

    def add_item(self, pattern: str) -> None:
        """
        Add(append) pattern
        to the list.
        """
        patterns = [i for i in self.patterns.values()]
        if pattern in patterns:
            self.create_button_frame.pack(anchor=N, side=TOP, pady=13)
            self.change_create_button_state()
            return
        self.patterns[self.pattern_index] = pattern
        self.pattern_index += 1
        self.selected = self.pattern_index
        self.listbox.delete(0, END)
        for pattern in self.patterns.values():
            self.listbox.insert(END, pattern)
        else:
            self.create_button_frame.pack(anchor=N, side=TOP, pady=13)
            self.change_create_button_state()

    def command_clear(self) -> None:
        """
        Delete all pattern.

        It is called when
        clear button is pushed.
        """
        self.patterns = {}
        self.pattern_index = 0
        self.selected = 0
        self.listbox.delete(0, END)
        self.change_create_button_state()

    def bind_delete(self, evt: Event) -> None:
        """
        Delete selected pattern.

        It is called when
        right button is pushed.
        """
        try:
            pattern, index = self.get_selected_pattern(evt)
        except TypeError:
            pass
        else:
            self.patterns[index] = pattern
        try:
            del self.patterns[index]
        except UnboundLocalError:
            pass
        else:
            self.listbox.delete(index, index)
            tmp_dict = {}
            for key, value in self.patterns.items():
                if key > index:
                    tmp_dict[key - 1] = value
                else:
                    tmp_dict[key] = value
            else:
                self.patterns = tmp_dict
                self.pattern_index -= 1
                self.selected -= 1
                if self.selected < 0:
                    self.selected = 0
                self.change_create_button_state()

    def change_create_button_state(self) -> None:
        """
        Change create button state.
        """
        if len(self.patterns) > 0:
            self.create_button["state"] = "normal"
        else:
            self.create_button["state"] = "disabled"

    def place(self) -> None:
        """
        Place objects.
        """
        self.buttons.place()
        self.listbox.pack(anchor=NW, side=LEFT, padx=10, pady=17, fill=Y)
        self.scrollbar.pack(anchor=NW, side=LEFT, pady=17, fill=Y)
        self.patterns_list_frame.pack(anchor=NW, side=TOP)
        self.create_button_frame.pack(anchor=N, side=TOP, pady=13)
        self.frame.pack(anchor=NW, side=LEFT, pady=5)


class Program:

    def __init__(self) -> None:
        """
        Create objects.
        """
        self.path = Path()
        self.data = Data()
        self.patterns = PatternsList(self.create_documents)
        self.place()

    def create_documents(self) -> None:
        """
        Create documents.
        """
        try:
            from docx import Document
            from docx.shared import RGBColor

            def replace_text(document, data, rgb, black):
                """
                Create documents.
                Have 2 different parts.

                Paragraphs — replace standart text.
                Tables — replace text in tables.
                """

            def paragraphs():
                """
                Replace standart text.
                """
                for par in document.paragraphs:
                    for run in par.runs:
                        try:
                            if run.font and run.font.color and run.font.color.rgb == rgb:
                                replace = False
                                for key, value in data.items():
                                    if key in run.text:
                                        run.text = run.text.replace(key, value)
                                        replace = True
                                if replace:
                                    run.font.color.rgb = black
                        except Exception:
                            pass

            def tables():
                """
                Replace text in tables.
                """
                for table in document.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for par in cell.paragraphs:
                                for run in par.runs:
                                    try:
                                        if run.font and run.font.color and run.font.color.rgb == rgb:
                                            replace = False
                                            for key, value in data.items():
                                                if key in run.text:
                                                    run.text = run.text.replace(key, value)
                                                    replace = True
                                            if replace:
                                                run.font.color.rgb = black
                                    except Exception:
                                        pass

                paragraphs()
                tables()

            path = self.path.entry.get()
            data = self.data.get_values()
            docs = [i for i in self.patterns.patterns.values()]
            for doc in docs:
                try:
                    document = Document(PATTERNS_FOLDER + doc + ".docx")
                except:
                    messagebox.showerror("Ошибка", "Выбранный шаблон не найден")
                else:
                    r, g, b = COLOR_TO_REPLACE
                    rgb = RGBColor(r, g, b)
                    black = RGBColor(0, 0, 0)
                    replace_text(document, data, rgb, black)
                try:
                    import os
                    os.makedirs(path, exist_ok=True)
                    document.save(path + doc + ".docx")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить документ:\n{e}")
                
        except Exception as exception:
            try:
                messagebox.showerror("Ошибка", "Ошибка при создании документов")
            finally:
                exception = None
                del exception

    def save(self):
        self.path.command_save()
        self.data.save()

    def place(self) -> None:
        """
        Place objects.
        """
        self.path.place()
        self.data.place()
        self.patterns.place()

    def delete(self) -> None:
        self.data.delete_windows()


program = Program()
try:

    def end():
        program.save()
        program.delete()
        window.destroy()


    if SAVE_ON_CLOSE:
        window.protocol("WM_DELETE_WINDOW", end)
    window.mainloop()
except Exception as exception:
    try:
        messagebox.showerror("Ошибка", exception)
    finally:
        exception = None
        del exception

except:
    messagebox.showerror("Ошибка", "Системная ошибка")
