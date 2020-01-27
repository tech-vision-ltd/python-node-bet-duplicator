import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import constants as const
from bet_manager import BetManager
import threading
import time
from datetime import datetime
from subprocess import call

bet_manager = BetManager()

# intializing the window
window = tk.Tk()
window.title(const.app_name)

# configuring size of the window
window.geometry(const.app_geometry)

s = ttk.Style()
s.configure('TNotebook.Tab', font=const.font_arial_14)


# Create Tab Control
def update_ui(event):
    update_tab_main()
    reset_tab_settings()


TAB_CONTROL = ttk.Notebook(window)
TAB_CONTROL.bind("<<NotebookTabChanged>>", update_ui)
# Tab1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text=const.tab_home_name)
# Tab2
TAB2 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB2, text=const.tab_settings_name)
TAB_CONTROL.pack(expand=1, fill="both")
# Tab3
TAB3 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB3, text=const.tab_about_name)
TAB_CONTROL.pack(expand=1, fill="both")

# Tab Name Labels
ttk.Label(TAB1, text=" ").grid(column=0, row=0, padx=10, pady=10)
ttk.Label(TAB2, text=" ").grid(column=0, row=0, padx=10, pady=10)
ttk.Label(TAB3, text=const.label_about).grid(column=0, row=0, padx=10, pady=10)

# Tab Main
tab_main_label_mother_key = ttk.Label(TAB1, text=const.key_mother_account)
tab_main_label_mother_key.config(font=const.font_arial_20)
tab_main_label_mother_key.grid(column=0, row=1, padx=20, pady=10, sticky=tk.W)

tab_main_label_mother_value = ttk.Label(TAB1, text="{}".format(bet_manager.app_data.account_mother_name))
tab_main_label_mother_value.config(font=const.font_arial_20)
tab_main_label_mother_value.grid(column=1, row=1, padx=20, pady=10, sticky=tk.W)

tab_main_label_bet_count_key = ttk.Label(TAB1, text=const.key_pending_bets)
tab_main_label_bet_count_key.config(font=const.font_arial_20)
tab_main_label_bet_count_key.grid(column=0, row=2, padx=20, pady=10, sticky=tk.W)

tab_main_label_bet_count_value = ttk.Label(TAB1, text="{}".format(len(bet_manager.current_bets)))
tab_main_label_bet_count_value.config(font=const.font_arial_20)
tab_main_label_bet_count_value.grid(column=1, row=2, padx=20, pady=10, sticky=tk.W)

tab_main_label_sons_key = ttk.Label(TAB1, text=const.key_son_accounts)
tab_main_label_sons_key.config(font=const.font_arial_20)
tab_main_label_sons_key.grid(column=0, row=3, padx=20, pady=10, sticky=tk.W)

list_sons = []
for item in bet_manager.app_data.accounts_son:
    list_sons.append(item['name'])
text_sons = ", ".join(list_sons)

tab_main_label_sons_value = ttk.Label(TAB1, text=text_sons)
tab_main_label_sons_value.config(font=("Arial", 20))
tab_main_label_sons_value.grid(column=1, row=3, padx=20, pady=10, sticky=tk.W)

tab_main_label_percentage_key = ttk.Label(TAB1, text=const.key_percentage)
tab_main_label_percentage_key.config(font=const.font_arial_20)
tab_main_label_percentage_key.grid(column=0, row=4, padx=20, pady=10, sticky=tk.W)

tab_main_label_percentage_value = ttk.Label(TAB1, text="{}".format(bet_manager.app_data.status_percentage))
tab_main_label_percentage_value.config(font=const.font_arial_20)
tab_main_label_percentage_value.grid(column=1, row=4, padx=20, pady=10, sticky=tk.W)


def start_stop():
    if bet_manager.app_data.status_is_running == 1:
        bet_manager.stop()
    else:
        bet_manager.start()
    update_caption()
    thread_ui_update = threading.Thread(target=update_automatically)
    thread_ui_update.start()


tab_main_button_start_stop = ttk.Button(TAB1, text="", width=50, command=start_stop)
tab_main_button_start_stop.grid(row=5, column=1, pady=40)


def update_caption():
    if bet_manager.app_data.status_is_running == 1:
        tab_main_button_start_stop.config(text=const.caption_stop)
    else:
        tab_main_button_start_stop.config(text=const.caption_start)


def update_tab_main():
    tab_main_label_mother_value.config(text="{}".format(bet_manager.app_data.account_mother_name))
    tab_main_label_bet_count_value.config(text="{}".format(len(bet_manager.current_bets)))
    list_sons = []
    for item in bet_manager.app_data.accounts_son:
        list_sons.append(item['name'])
    text_sons = ", ".join(list_sons)
    tab_main_label_sons_value.config(text=text_sons)
    tab_main_label_percentage_value.config(text="{}".format(bet_manager.app_data.status_percentage))
    update_caption()


def update_automatically():
    while bet_manager.app_data.status_is_running == 1:
        update_tab_main()
        print(datetime.now(), " -> ", "app status updated")
        time.sleep(bet_manager.app_data.status_delay_in_seconds)


# Tab Setting
is_modified = False


def set_modified(event):
    is_modified = True
    tab_settings_button_reset.config(state=tk.NORMAL)
    tab_settings_button_save.config(state=tk.NORMAL)
    # print(event)
    print(is_modified)


tab_settings_label_key_name = ttk.Label(TAB2, text="Name")
tab_settings_label_key_name.config(font=const.font_arial_14)
tab_settings_label_key_name.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

tab_settings_label_key_pass = ttk.Label(TAB2, text="Password")
tab_settings_label_key_pass.config(font=const.font_arial_14)
tab_settings_label_key_pass.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)

tab_settings_label_mother_name_key = ttk.Label(TAB2, text=const.key_mother_account)
tab_settings_label_mother_name_key.config(font=const.font_arial_14)
tab_settings_label_mother_name_key.grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)

tab_settings_entry_mother_name = ttk.Entry(TAB2)
tab_settings_entry_mother_name.bind("<Key>", set_modified)
tab_settings_entry_mother_name.config(font=const.font_arial_14)
tab_settings_entry_mother_name.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

tab_settings_entry_mother_pass = ttk.Entry(TAB2)
tab_settings_entry_mother_pass.bind("<Key>", set_modified)
tab_settings_entry_mother_pass.config(font=const.font_arial_14)
tab_settings_entry_mother_pass.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

tab_settings_label_son_key = ttk.Label(TAB2, text=const.key_son_accounts)
tab_settings_label_son_key.config(font=const.font_arial_14)
tab_settings_label_son_key.grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)

tab_settings_entry_son1_name = ttk.Entry(TAB2)
tab_settings_entry_son1_name.bind("<Key>", set_modified)
tab_settings_entry_son1_name.config(font=const.font_arial_14)
tab_settings_entry_son1_name.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

tab_settings_entry_son1_pass = ttk.Entry(TAB2)
tab_settings_entry_son1_pass.bind("<Key>", set_modified)
tab_settings_entry_son1_pass.config(font=const.font_arial_14)
tab_settings_entry_son1_pass.grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)

tab_settings_entry_son2_name = ttk.Entry(TAB2)
tab_settings_entry_son2_name.config(font=const.font_arial_14)
tab_settings_entry_son2_name.bind("<Key>", set_modified)
tab_settings_entry_son2_name.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

tab_settings_entry_son2_pass = ttk.Entry(TAB2)
tab_settings_entry_son2_pass.bind("<Key>", set_modified)
tab_settings_entry_son2_pass.config(font=const.font_arial_14)
tab_settings_entry_son2_pass.grid(row=3, column=2, padx=10, pady=10, sticky=tk.W)

ttk.Label(TAB2, text="").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

tab_settings_percentage_key = ttk.Label(TAB2, text=const.key_percentage)
tab_settings_percentage_key.config(font=const.font_arial_14)
tab_settings_percentage_key.grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)

ttk.Label(TAB2, text="").grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)


def do_select_combo(event):
    set_modified(event)
    print(
        "Combo selected, {} -> {}".format(tab_settings_combo_percentage.current(), tab_settings_combo_percentage.get()))


tab_settings_combo_percentage = ttk.Combobox(TAB2, state="readonly", values=[100, 75, 50])
tab_settings_combo_percentage.config(font=const.font_arial_14)
tab_settings_combo_percentage.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)
tab_settings_combo_percentage.bind("<<ComboboxSelected>>", do_select_combo)


def reset_tab_settings():
    tab_settings_entry_mother_name.delete(0, tk.END)
    tab_settings_entry_mother_name.insert(0, bet_manager.app_data.account_mother_name)
    tab_settings_entry_mother_pass.delete(0, tk.END)
    tab_settings_entry_mother_pass.insert(0, bet_manager.app_data.account_mother_pass)
    tab_settings_entry_son1_name.delete(0, tk.END)
    tab_settings_entry_son1_pass.delete(0, tk.END)
    tab_settings_entry_son2_name.delete(0, tk.END)
    tab_settings_entry_son2_pass.delete(0, tk.END)
    if len(bet_manager.app_data.accounts_son) > 0:
        tab_settings_entry_son1_name.insert(0, bet_manager.app_data.accounts_son[0]['name'])
        tab_settings_entry_son1_pass.insert(0, bet_manager.app_data.accounts_son[0]['pass'])
    if len(bet_manager.app_data.accounts_son) > 1:
        tab_settings_entry_son2_name.insert(0, bet_manager.app_data.accounts_son[1]['name'])
        tab_settings_entry_son2_pass.insert(0, bet_manager.app_data.accounts_son[1]['pass'])
    tab_settings_combo_percentage.set(bet_manager.app_data.status_percentage)
    is_modified = False
    tab_settings_button_reset.config(state=tk.DISABLED)
    tab_settings_button_save.config(state=tk.DISABLED)


def save_changes():
    bet_manager.app_data.account_mother_name = tab_settings_entry_mother_name.get()
    bet_manager.app_data.account_mother_pass = tab_settings_entry_mother_pass.get()
    bet_manager.app_data.accounts_son.clear()
    if tab_settings_entry_son1_name.get() != '':
        bet_manager.app_data.accounts_son.append(
            {'name': tab_settings_entry_son1_name.get(), 'pass': tab_settings_entry_son1_pass.get()}
        )
    if tab_settings_entry_son2_name.get() != '':
        bet_manager.app_data.accounts_son.append(
            {'name': tab_settings_entry_son2_name.get(), 'pass': tab_settings_entry_son2_pass.get()}
        )
    bet_manager.app_data.status_percentage = tab_settings_combo_percentage.get()
    bet_manager.app_data.write_data()
    reset_tab_settings()
    # print(tab_settings_entry_mother_name.get())


tab_settings_button_reset = ttk.Button(TAB2, text=const.caption_rest, width=30, command=reset_tab_settings)
tab_settings_button_reset.grid(row=7, column=1, padx=10, pady=10)

tab_settings_button_save = ttk.Button(TAB2, text=const.caption_save, width=30, command=save_changes)
tab_settings_button_save.grid(row=7, column=2, padx=10, pady=10)

reset_tab_settings()


# Calling Main()
def on_close():
    if messagebox.askokcancel(const.close_message_box_title, const.close_message_box_message):
        bet_manager.stop()

        window.destroy()


window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()

# call(["node", "automation/server.js"])