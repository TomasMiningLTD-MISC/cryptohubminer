try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GObject
    print("gtk 3")
except:
    import pygtk
    pygtk.require('2.0')
    print("gtk 2")
    import gtk as Gtk
    import gobject as GObject
    import gtk.gdk as Gdk
import threading, subprocess, psutil
import os
import platform
import datetime
import re
import decimal
import sys



pools_cpu = {
    "Q2C": ["cryptohub.online:3042","qubit"],
}


pools_gpu = {
    "XLR": ["cryptohub.online:3032","nist5"],
    "WYV": ["cryptohub.online:3052","nist5"],
    "Q2C": ["cryptohub.online:3042","qubit"],
    "ONION": ["cryptohub.online:3101","x13"],
}

#radeon
pools_gpu2 = {
    "XLR": ["cryptohub.online:3032","nist5"],
    "WYV": ["cryptohub.online:3052","nist5"],
    "Q2C": ["cryptohub.online:3042","qubitcoin"],
}

def get_data_dir():
    print(sys.platform)
    if sys.platform == 'linux2' or sys.platform == 'linux':
        dat_dir = os.path.expanduser("~") + "/.cryptohubminer"
    elif sys.platform == "win32" or sys.platform == "cygwin":
        dat_dir = os.getenv('APPDATA') + os.path.sep + "cryptohubminer"
    print(dat_dir)

    if not os.path.exists(dat_dir):
        os.makedirs(dat_dir)

    return dat_dir


dita_dir = get_data_dir()
app_dir = os.path.dirname(sys.argv[0])

if sys.platform == 'linux2' or sys.platform == 'linux':
    ccminer_path = app_dir + os.path.sep + "ccminer" + os.path.sep + "ccminer"
    cpuminer_path = app_dir + os.path.sep + "cpuminer" + os.path.sep + "cpuminer"
    sgminer_path = app_dir + os.path.sep + "sgminer" + os.path.sep + "sgminer"
elif sys.platform == "win32" or sys.platform == "cygwin":
    ccminer_path = app_dir + os.path.sep + "ccminer" + os.path.sep + "ccminerAlexis78.exe"
    cpuminer_path = app_dir + os.path.sep + "cpuminer" + os.path.sep + "cpuminer.exe"
    sgminer_path = app_dir + os.path.sep + "sgminer" + os.path.sep + "sgminer.exe"

def rel_path(dir, file):
    return app_dir + os.path.sep + dir + os.path.sep + file


log_f = open(dita_dir + os.path.sep + 'log.txt', 'w')
sys.stdout = log_f



class gui():
    is_linux = False
    nvidia = False
    radeon = False
    old_cpu = False
    started_gpu_nvidia = False
    started_gpu_radeon = False
    started_gpu = False
    started_gpu_title = None
    started_gpu_hs = 0
    started_gpu_hs_upd = None
    started_gpu2 = False
    started_gpu2_title = None
    started_gpu2_hs = 0
    started_gpu2_hs_upd = None
    started_gpu_title3 = None
    started_cpu = False
    started_cpu_title = None
    started_cpu_hs = 0
    started_cpu_hs_upd = None
    cpu_threads = 1
    cpu_coin = None
    gpu_coin = None
    found_devices = []

    def get_resource_path(self, rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def on_destroy(self, widget=None, *data):
        if self.started_gpu or self.started_cpu:
            try:
                messagedialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL, "On close mining process will be stopped")
            except:
                messagedialog = Gtk.MessageDialog(self.window, 0, Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK_CANCEL, "On close mining process will be stopped")
            messagedialog.show_all()
            result = messagedialog.run()
            messagedialog.destroy()
            try:
                if result == Gtk.ResponseType.CANCEL:
                    return True
            except:
                if result == Gtk.RESPONSE_CANCEL:
                    return True
        self.kill_miner("gpu")
        self.kill_miner("cpu")
        log_f.close()
        Gtk.main_quit()
        return False

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_default_size(800, 600)
        self.window.set_title("CryptoHubMiner")
        self.window.connect('delete-event', self.on_destroy)
        self.window.set_icon_from_file(self.get_resource_path("imgs/icon.png"))

        self.box = Gtk.VBox()
        self.window.add(self.box)

        self.hbox_status = Gtk.HBox()
        self.box.pack_start(self.hbox_status, False, True, 30)



        self.img = Gtk.Image()
        self.img.set_from_file(rel_path("imgs", "stop.png"))
        self.hbox_status.pack_start(self.img, False, True, 10)

        self.label_status = Gtk.Label('idle')
        self.label_status.set_markup('<span size="xx-large" foreground="red">Idle</span>')
        self.hbox_status.pack_start(self.label_status, False, True, 10)

        self.fr = Gtk.Frame()
        self.hbox_status.pack_start(self.fr, True, True, 10)

        self.box_c1 = Gtk.VBox()
        self.hbox_status.pack_start(self.box_c1, False, True, 30)

        self.label_title_cpu = Gtk.Label('')
        self.box_c1.pack_start(self.label_title_cpu, True, True, 0)

        self.label_hashrate_cpu = Gtk.Label('')
        self.box_c1.pack_start(self.label_hashrate_cpu, True, True, 0)

        self.label_accepted_cpu = Gtk.Label('')
        self.box_c1.pack_start(self.label_accepted_cpu, True, True, 0)

        self.label_rejected_cpu = Gtk.Label('')
        self.box_c1.pack_start(self.label_rejected_cpu, True, True, 0)

        #self.label_coin_cpu_bal_conf = Gtk.Label('Confirmed balance:')
        #self.box_c1.pack_start(self.label_coin_cpu_bal_conf, True, True, 0)

        self.fr2 = Gtk.Frame()
        self.hbox_status.pack_start(self.fr2, True, True, 10)

        self.box_c2 = Gtk.VBox()
        self.hbox_status.pack_start(self.box_c2, False, True, 30)

        self.label_title_gpu = Gtk.Label('')
        self.box_c2.pack_start(self.label_title_gpu, True, True, 0)

        self.label_hashrate_gpu = Gtk.Label('')
        self.box_c2.pack_start(self.label_hashrate_gpu, True, True, 0)

        self.label_accepted_gpu = Gtk.Label('')
        self.box_c2.pack_start(self.label_accepted_gpu, True, True, 0)

        self.label_rejected_gpu = Gtk.Label('')
        self.box_c2.pack_start(self.label_rejected_gpu, True, True, 0)



        self.fr3 = Gtk.Frame()
        self.hbox_status.pack_start(self.fr3, True, True, 10)

        self.box_c3 = Gtk.VBox()
        self.hbox_status.pack_start(self.box_c3, False, True, 30)

        self.label_title_gpu3 = Gtk.Label('')
        self.box_c3.pack_start(self.label_title_gpu3, True, True, 0)

        self.label_hashrate_gpu3 = Gtk.Label('')
        self.box_c3.pack_start(self.label_hashrate_gpu3, True, True, 0)

        self.label_accepted_gpu3 = Gtk.Label('')
        self.box_c3.pack_start(self.label_accepted_gpu3, True, True, 0)

        self.label_rejected_gpu3 = Gtk.Label('')
        self.box_c3.pack_start(self.label_rejected_gpu3, True, True, 0)




        #gobject.threads_init()
        pl = platform.platform()

        if pl.startswith("Windows"):
            import pywinusb.hid as hid
            all_devices = hid.HidDeviceFilter().get_devices()
            print(all_devices)
            print("1")
            #from wmi import wmi
            #c = wmi.WMI()
            #print(c.Win32_Processor())

            #import platform
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            cpu_threads = info['count']
            info2 = cpuinfo.get_cpu_info_from_cpuid()
            try:
                cpu_features = info2['flags']
            except:
                cpu_features = info['flags']

        else:
            self.is_linux = True
            from hwinfo.pci import PCIDevice
            from hwinfo.pci.lspci import LspciNNMMParser
            from subprocess import check_output

            # Obtain the output of lspci -nnmm from somewhere
            lspci_output = check_output(["lspci", "-nnmm"])

            # Parse the output using the LspciNNMMParser object
            parser = LspciNNMMParser(lspci_output)
            device_recs = parser.parse_items()

            # Instantiate the records as PCI devices
            pci_devs = [PCIDevice(device_rec) for device_rec in device_recs]
            for dev in pci_devs:
                if dev.is_subdevice():
                    dev_info = dev.get_info()
                    if "NVIDIA" in dev_info:
                        self.nvidia = True
                        self.found_devices.append(dev_info)
                    if "Radeon" in dev_info or "RADEON" in dev_info:
                        self.radeon = True
                        self.found_devices.append(dev_info)

            print(self.found_devices)

            proc_output = check_output(["lscpu"])
            cpu_features = str(proc_output.split("Flags:".encode())[1]).split(" ")
            cpu_threads = str(proc_output.split("CPU(s):".encode())[1]).split("\\n")[0].replace("b'","").strip()

        try:
            self.cpu_threads = int(cpu_threads)
        except:
            self.cpu_threads = 2
        print("features", cpu_features, cpu_threads)
        if not "avx2" in cpu_features and not "aes" in cpu_features and not "avx" in cpu_features:
            self.old_cpu = True



        self.label_cpu = Gtk.Label("Enter your CryptoHub user:")
        self.box.pack_start(self.label_cpu, True, True, 20)

        self.user_input_box = Gtk.HBox()
        self.box.pack_start(self.user_input_box, True, True, 10)



        self.user_input_frame = Gtk.Frame()
        try:
            self.user_input_frame.get_style_context().add_class("inp")
        except:
            pass

        self.user_input = Gtk.TextView()
        self.user_input_box.pack_start(self.user_input_frame, True, True, 50)
        self.user_input_frame.add(self.user_input)

        try:
            with open(dita_dir + os.path.sep + "user.conf", "r") as myfile:
                user = myfile.readline().strip()
                self.user_input.get_buffer().set_text(user)
        except Exception as e:
            print(e)
            pass


        self.gtk_style()





        if self.old_cpu:
            self.label_cpu = Gtk.Label("Your CPU is too old and doesn't support AES not AVX.")
            self.box.pack_start(self.label_cpu, True, True, 20)
        else:
            self.label_cpu = Gtk.Label("Select a coin to mine on CPU:")
            self.box.pack_start(self.label_cpu, True, True, 20)
            self.box_nv = Gtk.HBox()
            self.box.pack_start(self.box_nv, True, True, 20)

            self.cpuhbox = Gtk.HBox()
            self.box_nv.pack_start(self.cpuhbox, True, True, 10)

            try:
                self.combobox_cpu = Gtk.ComboBoxText()
            except:
                self.combobox_cpu = Gtk.combo_box_new_text()
            self.combobox_cpu.append_text("Q2C")
            self.cpuhbox.pack_start(self.combobox_cpu, True, True, 10)

            self.label_cpu_threads = Gtk.Label("Threads:")
            self.cpuhbox.pack_start(self.label_cpu_threads, False, True, 20)

            try:
                self.combobox_threads = Gtk.ComboBoxText()
            except:
                self.combobox_threads = Gtk.combo_box_new_text()

            for i in range(self.cpu_threads):
                self.combobox_threads.append_text(str(i+1))
            try:
                self.combobox_threads.set_active(0)
            except:
                pass
            self.cpuhbox.pack_start(self.combobox_threads, True, True, 10)



            self.hbox = Gtk.HBox()
            self.box.pack_start(self.hbox, True, True, 10)

            self.cpu_button = Gtk.Button(label='Start')
            self.cpu_button.connect('clicked', self.on_cpu_button_clicked)
            self.hbox.pack_start(self.cpu_button, True, True, 10)

            self.cpu_button2 = Gtk.Button(label='Stop')
            self.cpu_button2.set_sensitive(False)
            self.cpu_button2.connect('clicked', self.on_cpu_button_clicked2)
            self.hbox.pack_start(self.cpu_button2, True, True, 10)



        if self.nvidia:

            self.label_hashrate = Gtk.Label('Select a coin to mine on Nvidia GPU(s):')
            self.box.pack_start(self.label_hashrate, True, True, 20)

            self.box_nv = Gtk.HBox()
            self.box.pack_start(self.box_nv, True, True, 20)

            try:
                self.combobox_gpu = Gtk.ComboBoxText()
            except:
                self.combobox_gpu = Gtk.combo_box_new_text()

            for k,el in pools_gpu.items():
                self.combobox_gpu.append_text(k)
            self.box_nv.pack_start(self.combobox_gpu, True, True, 10)

            self.hbox = Gtk.HBox()
            self.box.pack_start(self.hbox, True, True, 10)

            self.gpu_button = Gtk.Button(label='Start')
            self.gpu_button.connect('clicked', self.on_gpu_button_clicked)
            self.hbox.pack_start(self.gpu_button, True, True, 10)

            self.gpu_buttonoff = Gtk.Button(label='Stop')
            self.gpu_buttonoff.set_sensitive(False)
            self.gpu_buttonoff.connect('clicked', self.on_gpu_button_off_clicked)
            self.hbox.pack_start(self.gpu_buttonoff, True, True, 10)


        if self.radeon:

            self.label_hashrate2 = Gtk.Label('Select a coin to mine on Radeon GPU(s):')
            self.box.pack_start(self.label_hashrate2, True, True, 20)

            self.box_nv2 = Gtk.HBox()
            self.box.pack_start(self.box_nv2, True, True, 20)

            try:
                self.combobox_gpu2 = Gtk.ComboBoxText()
            except:
                self.combobox_gpu2 = Gtk.combo_box_new_text()

            for k, el in pools_gpu2.items():
                self.combobox_gpu2.append_text(k)
            self.box_nv2.pack_start(self.combobox_gpu2, True, True, 10)

            try:
                self.combobox_gpu2_platform = Gtk.ComboBoxText()
            except:
                self.combobox_gpu2_platform = Gtk.combo_box_new_text()

            self.combobox_gpu2_platform.append_text("Platform 0")
            self.combobox_gpu2_platform.append_text("Platform 1")
            self.combobox_gpu2_platform.append_text("Platform 2")
            self.combobox_gpu2_platform.set_active(0)
            self.box_nv2.pack_start(self.combobox_gpu2_platform, True, True, 10)
            self.label_sel_platform = Gtk.Label('If mining doesnt work try to choose another platform')
            self.box_nv2.pack_start(self.label_sel_platform, True, True, 10)



            self.hbox2 = Gtk.HBox()
            self.box.pack_start(self.hbox2, True, True, 10)

            self.gpu_button2 = Gtk.Button(label='Start')
            self.gpu_button2.connect('clicked', self.on_gpu_button_clicked2)
            self.hbox2.pack_start(self.gpu_button2, True, True, 10)

            self.gpu_button2off = Gtk.Button(label='Stop')
            self.gpu_button2off.set_sensitive(False)
            self.gpu_button2off.connect('clicked', self.on_gpu_button_off2_clicked)
            self.hbox2.pack_start(self.gpu_button2off, True, True, 10)





        GObject.timeout_add(1000, self.upd)

        self.window.show_all()



        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()

    def open_log(self, file):
        a = open(file, 'rb')
        lines = a.readlines()
        if lines:
            last_line = lines[-1]
            return last_line

    def get_log(self, type="gpu"):
        res_data_all = {
            "hashrate": 0,
            "accepted": 0,
            "rejected": 0
        }

        import os.path, time
        filename = dita_dir + os.path.sep + type + "miner.txt"
        print(filename)
        last_change = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        dif = datetime.datetime.now() - last_change
        if dif > datetime.timedelta(seconds=30):
            return res_data_all


        last_line = str(self.open_log(filename))
        print(last_line)
        if "[S/A/T]" in last_line:
            # Alexis ccminer
            print("Alexis ccminer")
            els = last_line.split(",")
            shares = str(els[0].split(":")[-1]).strip().split("/")
            hs = str(els[2].split("/s")[0]).strip()
            res_data_all["hashrate"] = hs + "/s"
            res_data_all["accepted"] = int(shares[1])
            res_data_all["rejected"] = int(shares[2]) - int(shares[1])
        elif "Accepted" in last_line:
            # common ccminer / cpuminer
            print("common ccminer")
            els = last_line.split("Accepted")[1].split(",")
            shares = els[0].strip().split(" ")[1].split("/")
            print(els, shares)
            hs = els[2]
            res_data_all["hashrate"] = hs
            res_data_all["accepted"] = int(shares[0])
            res_data_all["rejected"] = int(shares[1]) - int(shares[0])
        elif "accepted:" in last_line:
            # common ccminer
            print("common ccminer x2")
            els = last_line.split("accepted:")[1].split(",")
            print(els)
            shares = els[0].strip().split(" ")[0].split("/")
            print(els, shares)
            hs = els[1].strip().replace("\\x1b","\x1b").split(" \x1b")[0]
            res_data_all["hashrate"] = hs
            res_data_all["accepted"] = int(shares[0])
            res_data_all["rejected"] = int(shares[1]) - int(shares[0])
        elif "(avg):" in last_line:
            #sgminer
            print("sgminer")
            els = last_line.split("(avg):")[1].split("|")
            print(els)
            shares = els[1].strip().split(" ")
            print(shares)
            res_data_all["hashrate"] = els[0]
            res_data_all["accepted"] = int(shares[0].split(":")[1])
            res_data_all["rejected"] = int(shares[2].split(":")[1])


        return res_data_all

    def upd(self):
        #print("upd")
        if self.started_gpu:
            self.label_status.set_markup('<span size="xx-large" foreground="green">Running</span>')
            try:
                res_data = self.get_log("gpu")
                self.label_title_gpu.set_markup('<span size="large" foreground="green">'+ str(self.started_gpu_title) +'</span>')
                if self.started_gpu_hs != 0 and res_data["hashrate"] == 0:
                    if not self.started_gpu_hs_upd:
                        self.label_hashrate_gpu.set_label("")
                    else:
                        if self.started_gpu_hs_upd < datetime.datetime.now() - datetime.timedelta(seconds=30):
                            self.label_hashrate_gpu.set_label("")
                        else:
                            self.label_hashrate_gpu.set_label(self.started_gpu_hs)
                else:
                    self.label_hashrate_gpu.set_label(str(res_data["hashrate"]))
                    self.started_gpu_hs = str(res_data["hashrate"])
                    self.started_gpu_hs_upd = datetime.datetime.now()
                if res_data["accepted"] > 0 or res_data["rejected"] > 0:
                    self.label_accepted_gpu.set_label("Accepted:" + str(res_data["accepted"]))
                    self.label_rejected_gpu.set_label("Rejected:" + str(res_data["rejected"]))

            except Exception as e:
                print(e)
        else:
            self.label_title_gpu.set_markup('<span size="large" foreground="green"></span>')
            self.label_hashrate_gpu.set_label("")
            self.label_accepted_gpu.set_label("")
            self.label_rejected_gpu.set_label("")


        if self.started_gpu2:
            print("gpu 2")
            self.label_status.set_markup('<span size="xx-large" foreground="green">Running</span>')
            try:
                res_data = self.get_log("gpu2")
                self.label_title_gpu3.set_markup('<span size="large" foreground="green">'+ str(self.started_gpu2_title) +'</span>')
                if self.started_gpu2_hs != 0 and res_data["hashrate"] == 0:
                    if not self.started_gpu2_hs_upd:
                        self.label_hashrate_gpu3.set_label("")
                    else:
                        if self.started_gpu2_hs_upd < datetime.datetime.now() - datetime.timedelta(seconds=30):
                            self.label_hashrate_gpu3.set_label("")
                        else:
                            self.label_hashrate_gpu3.set_label(self.started_gpu2_hs)
                else:
                    self.label_hashrate_gpu3.set_label(str(res_data["hashrate"]))
                    self.started_gpu2_hs_upd = datetime.datetime.now()
                    self.started_gpu2_hs = str(res_data["hashrate"])
                if res_data["accepted"] > 0 or res_data["rejected"] > 0:
                    self.label_accepted_gpu3.set_label("Accepted:" + str(res_data["accepted"]))
                    self.label_rejected_gpu3.set_label("Rejected:" + str(res_data["rejected"]))

            except Exception as e:
                print(e)
        else:
            self.label_title_gpu3.set_markup('<span size="large" foreground="green"></span>')
            self.label_hashrate_gpu3.set_label("")
            self.label_accepted_gpu3.set_label("")
            self.label_rejected_gpu3.set_label("")


        if self.started_cpu:
            self.label_title_cpu.set_markup('<span size="large" foreground="green">Q2C</span>')
            try:
                res_data = self.get_log("cpu")
                self.label_title_cpu.set_markup('<span size="large" foreground="green">' + str(self.started_cpu_title) + '</span>')
                self.label_hashrate_cpu.set_label(str(res_data["hashrate"]))
                #print("hh", self.started_cpu_hs, res_data["hashrate"], self.started_cpu_hs != 0, res_data["hashrate"] == 0)
                if self.started_cpu_hs != 0 and res_data["hashrate"] == 0:
                    if not self.started_cpu_hs_upd:
                        self.label_hashrate_cpu.set_label("")
                    else:
                        if self.started_cpu_hs_upd < datetime.datetime.now() - datetime.timedelta(seconds=30):
                            self.label_hashrate_cpu.set_label("")
                        else:
                            self.label_hashrate_cpu.set_label(self.started_cpu_hs)

                else:
                    self.label_hashrate_cpu.set_label(str(res_data["hashrate"]))
                    self.started_cpu_hs_upd = datetime.datetime.now()
                    self.started_cpu_hs = str(res_data["hashrate"])
                if res_data["accepted"] > 0 or res_data["rejected"] > 0:
                    self.label_accepted_cpu.set_label("Accepted:" + str(res_data["accepted"]))
                    self.label_rejected_cpu.set_label("Rejected:" + str(res_data["rejected"]))

            except Exception as e:
                print(e)
        else:
            self.label_title_cpu.set_markup('<span size="large" foreground="green"></span>')
            self.label_hashrate_cpu.set_label("")
            self.label_accepted_cpu.set_label("")
            self.label_rejected_cpu.set_label("")


        if self.started_gpu or self.started_gpu2 or self.started_cpu:
            self.img.set_from_file(rel_path("imgs", "run.png"))
            self.label_status.set_markup('<span size="xx-large" foreground="green">Running</span>')
        else:
            self.img.set_from_file(rel_path("imgs", "stop.png"))
            self.label_status.set_markup('<span size="xx-large" foreground="red">Idle</span>')
        GObject.timeout_add(1000, self.upd)




    def on_gpu_button_clicked(self, widget):
        key = self.combobox_gpu.get_active_text()
        buf = self.user_input.get_buffer()
        bs = buf.get_bounds()
        user = buf.get_text(bs[0],bs[1],True)
        if not user:
            return

        self.started_gpu_hs = 0

        self.save_user_conf(user)

        pool = pools_gpu[key]
        print(pool)
        if self.nvidia:
            prc = ccminer_path + " -a " + pool[1] + " -o stratum+tcp://" + pool[0] + " -u " + user + " -p x"
            subprocess.call(prc + " > " + dita_dir + os.path.sep + "gpuminer.txt &", shell=True)

            self.started_gpu_title = key
            self.started_gpu = True

            self.gpu_button.set_sensitive(False)
            self.gpu_buttonoff.set_sensitive(True)

    def on_gpu_button_clicked2(self, widget):
        key = self.combobox_gpu2.get_active_text()
        buf = self.user_input.get_buffer()
        bs = buf.get_bounds()
        user = buf.get_text(bs[0], bs[1], True)
        if not user:
            return

        self.started_gpu2_hs = 0

        self.save_user_conf(user)
        pool = pools_gpu2[key]

        if self.radeon:
            platform = self.combobox_gpu2_platform.get_active_text()
            platform = platform.replace("Platform ","")
            prc = sgminer_path + " --algorithm " + pool[1] + " -o stratum+tcp://" + pool[0] + " -u " + user + " -p x --intensity 21 -T -v --gpu-platform " + platform
            subprocess.call(prc + " > " + dita_dir + os.path.sep + "gpu2miner.txt &", shell=True)

            self.started_gpu2_title = key
            self.started_gpu2 = True

            self.gpu_button2.set_sensitive(False)
            self.gpu_button2off.set_sensitive(True)



    def kill_miner(self, type):
        if type == "gpu" or type == "gpu_nvidia":
            if self.nvidia:
                prc_name = "ccminer"
                for proc in psutil.process_iter():
                    if proc.name() == prc_name:
                        proc.kill()

        if type == "gpu" or type == "gpu_radeon":
            if self.radeon:
                prc_name = "sgminer"
                for proc in psutil.process_iter():
                    if proc.name() == prc_name:
                        proc.kill()

        if type == "cpu":
            prc_name = "cpuminer"
            for proc in psutil.process_iter():
                if proc.name() == prc_name:
                    proc.kill()

    def on_gpu_button_off_clicked(self, widget):
        self.kill_miner("gpu_nvidia")
        self.gpu_button.set_sensitive(True)
        self.gpu_buttonoff.set_sensitive(False)
        self.started_gpu_nvidia = False
        self.started_gpu = False

    def on_gpu_button_off2_clicked(self, widget):
        self.kill_miner("gpu_radeon")
        self.gpu_button2.set_sensitive(True)
        self.gpu_button2off.set_sensitive(False)
        self.started_gpu_radeon = False
        self.started_gpu2 = False

    def on_cpu_button_clicked(self, widget):
        key = self.combobox_cpu.get_active_text()
        buf = self.user_input.get_buffer()
        bs = buf.get_bounds()
        user = buf.get_text(bs[0], bs[1], True)
        if not user:
            return

        self.save_user_conf(user)
        pool = pools_cpu[key]
        self.started_cpu_hs = 0

        threads = self.combobox_threads.get_active_text()
        prc = cpuminer_path +  " -a " + pool[1] + " -o stratum+tcp://" + pool[0] + " -u " + user + " -p x  -t " + str(threads)
        print(prc)
        subprocess.call(prc + " > " + dita_dir + os.path.sep + "cpuminer.txt &", shell=True)
        self.started_cpu_title = key
        self.started_cpu = True
        self.cpu_button.set_sensitive(False)
        self.cpu_button2.set_sensitive(True)

    def on_cpu_button_clicked2(self, widget):
        self.kill_miner("cpu")
        self.cpu_button.set_sensitive(True)
        self.cpu_button2.set_sensitive(False)
        self.started_cpu = False

    def save_user_conf(self, user):
        try:
            with open(dita_dir + os.path.sep + "user.conf", "w") as myfile:
                myfile.write(str(user) + "\n")
        except Exception as e:
            print(e)
            pass


    def gtk_style(self):
            css = b"""
    * {
        transition-property: color, background-color, border-color, background-image, padding, border-width;
        transition-duration: 0.6s;
        font-size: 14px;
    }

    frame.inp {
        border-style: solid;
        border-width: 1px;
        padding: 6px;
        border-color: black;
    }
            """
            try:
                style_provider = Gtk.CssProvider()
                style_provider.load_from_data(css)

                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    style_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

            except:
                pass





g = gui()
