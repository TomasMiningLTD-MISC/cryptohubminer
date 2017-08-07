import gi
try:
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GObject
except:
    import pygtk
    pygtk.require('2.0')
    import gtk
import threading, subprocess, psutil
import os
import platform
import telnetlib
import datetime
import decimal


pools_gpu = {
    "XLR": ["cryptohub.online:3032","nist5"],
    "WYV": ["cryptohub.online:3052","nist5"],
    "OLIT": ["cryptohub.online:3022","x11"],
}


class gui():
    nvidia = False
    radeon = False
    old_cpu = False
    started_gpu = False
    started_cpu = False
    cpu_threads = 1
    cpu_coin = None
    gpu_coin = None

    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.window = Gtk.Window()
        self.window.set_default_size(800, 600)
        self.window.connect('delete-event', Gtk.main_quit)

        self.box = Gtk.VBox()
        self.window.add(self.box)

        self.hbox_status = Gtk.HBox()
        self.box.pack_start(self.hbox_status, False, True, 30)



        self.img = Gtk.Image()
        self.img.set_from_file(self.dir + "/imgs/stop.png")
        self.hbox_status.pack_start(self.img, False, True, 10)

        self.label_status = Gtk.Label('idle')
        self.label_status.set_markup('<span size="xx-large" foreground="red">Idle</span>')
        self.hbox_status.pack_start(self.label_status, False, True, 10)

        self.fr = Gtk.Frame()
        self.hbox_status.pack_start(self.fr, True, True, 10)

        self.box_c1 = Gtk.VBox()
        self.hbox_status.pack_start(self.box_c1, False, True, 30)

        self.label_title_cpu = Gtk.Label('Coin 1')
        self.box_c1.pack_start(self.label_title_cpu, True, True, 0)

        self.label_hashrate_cpu = Gtk.Label('Hashrate 2')
        self.box_c1.pack_start(self.label_hashrate_cpu, True, True, 0)

        self.label_coin_cpu_bal_conf = Gtk.Label('Confirmed balance:')
        self.box_c1.pack_start(self.label_coin_cpu_bal_conf, True, True, 0)

        self.fr2 = Gtk.Frame()
        self.hbox_status.pack_start(self.fr2, True, True, 10)

        self.box_c2 = Gtk.VBox()
        self.hbox_status.pack_start(self.box_c2, False, True, 30)

        self.label_title_gpu = Gtk.Label('Coin 2')
        self.box_c2.pack_start(self.label_title_gpu, True, True, 0)

        self.label_hashrate_gpu = Gtk.Label('Hashrate 2')
        self.box_c2.pack_start(self.label_hashrate_gpu, True, True, 0)




        #gobject.threads_init()
        pl = platform.platform()

        if pl.startswith("Windows"):
            import pywinusb.hid as hid
            all_devices = hid.HidDeviceFilter().get_devices()
            print(all_devices)
            print("1")
            from wmi import wmi
            c = wmi.WMI()
            print(c.Win32_Processor())


        else:
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
                    if "Radeon" in dev_info or "RADEON" in dev_info:
                        self.radeon = True

            proc_output = check_output(["lscpu"])
            cpu_features = str(proc_output.split("Flags:".encode())[1]).split(" ")
            cpu_threads = str(proc_output.split("CPU(s):".encode())[1]).split("\\n")[0].replace("b'","").strip()
            try:
                self.cpu_threads = int(cpu_threads)
            except:
                self.cpu_threads = 4
            if not "avx2" in cpu_features and not "aes" in cpu_features and not "avx" in cpu_features:
                self.old_cpu = True


        if self.old_cpu:
            self.label_cpu = Gtk.Label("Your CPU is too old and doesn't support AES not AVX.")
            self.box.pack_start(self.label_cpu, True, True, 20)
        else:
            self.label_cpu = Gtk.Label("Select a coin to mine on CPU:")
            self.box.pack_start(self.label_cpu, True, True, 20)
            self.box_nv = Gtk.Box()
            self.box.pack_start(self.box_nv, True, True, 20)

            self.cpuhbox = Gtk.HBox()
            self.box_nv.pack_start(self.cpuhbox, True, True, 10)

            self.combobox_cpu = Gtk.ComboBoxText()
            self.combobox_cpu.append_text("Mining Q2C")
            self.cpuhbox.pack_start(self.combobox_cpu, True, True, 10)

            self.label_cpu_threads = Gtk.Label("Threads:")
            self.cpuhbox.pack_start(self.label_cpu_threads, False, True, 20)

            self.combobox_threads = Gtk.ComboBoxText()
            for i in range(self.cpu_threads):
                self.combobox_threads.append_text(str(i+1))
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



        if self.nvidia or self.radeon:

            self.label_hashrate = Gtk.Label('Select a coin to mine on GPU:')
            self.box.pack_start(self.label_hashrate, True, True, 20)

            self.box_nv = Gtk.Box()
            self.box.pack_start(self.box_nv, True, True, 20)

            self.combobox_gpu = Gtk.ComboBoxText()
            for k,el in pools_gpu.items():
                self.combobox_gpu.append_text(k)
            self.box_nv.pack_start(self.combobox_gpu, True, True, 10)

            self.hbox = Gtk.HBox()
            self.box.pack_start(self.hbox, True, True, 10)

            self.gpu_button = Gtk.Button(label='Start')
            self.gpu_button.connect('clicked', self.on_gpu_button_clicked)
            self.hbox.pack_start(self.gpu_button, True, True, 10)

            self.gpu_button2 = Gtk.Button(label='Stop')
            self.gpu_button2.set_sensitive(False)
            self.gpu_button2.connect('clicked', self.on_gpu_button_clicked2)
            self.hbox.pack_start(self.gpu_button2, True, True, 10)




        GObject.timeout_add(1000, self.upd)

        self.window.show_all()



        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()


    def telnet_get(self, command, port):
        if self.nvidia:
            tn = telnetlib.Telnet("127.0.0.1", port)
            tn.write(str(command + "\n").encode('ascii'))

            res_data_all = []
            rs = tn.read_all()
            rs = str(rs)[2:].split("|")
            for el in rs:
                res = str(el).split(";")
                res_data = {}
                for r in res:
                    parts = r.split("=")
                    if len(parts)>1:
                        k = parts[0]
                        res_data[k] = parts[1]
                res_data_all.append(res_data)
            return res_data_all

    def upd(self):
        if self.started_gpu:
            self.label_status.set_markup('<span size="xx-large" foreground="green">Running</span>')
            try:
                res_data = self.telnet_get("summary", 4090)
                self.label_hashrate.set_label(str(res_data["KHS"]))

                try:
                    res_data = self.telnet_get("scanlog", 4090)
                    print(res_data)
                except:
                    pass

            except Exception as e:
                print(e)

        if self.started_cpu:
            self.label_title_cpu.set_markup('<span size="large" foreground="green">Q2C</span>')
            try:
                res_data = self.telnet_get("summary", 4091)
                '''try:
                    khs = decimal.Decimal(res_data[0]["KHS"])
                except:
                    khs = 0'''
                khs = 0
                if khs <= 0:
                    res_data = self.telnet_get("threads", 4091)
                    for el in res_data:
                        if 'KHS' in el:
                            khs += decimal.Decimal(el['KHS'].replace("|'",""))
                self.label_hashrate_cpu.set_label(str(khs))
            except Exception as e:
                print(e)
        else:
            self.label_title_cpu.set_markup('<span size="large" foreground="green"></span>')
            self.label_hashrate_cpu.set_label("")


        if self.started_gpu or self.started_cpu:
            self.img.set_from_file(self.dir + "/imgs/run.png")
            self.label_status.set_markup('<span size="xx-large" foreground="green">Running</span>')
        else:
            self.img.set_from_file(self.dir + "/imgs/stop.png")
            self.label_status.set_markup('<span size="xx-large" foreground="red">Idle</span>')
        GObject.timeout_add(1000, self.upd)

    def on_gpu_button_clicked(self, widget):
        key = self.combobox_gpu.get_active_text()
        pool = pools_gpu[key]
        print(pool)
        if self.nvidia:
            prc = self.dir + "/ccminer/ccminer -a " + pool[1] + " -o stratum+tcp://" + pool[0] + " -u support@cryptohub.online -p x -b 127.0.0.1:4090"
        elif self.radeon:
            print("to do")
        if self.nvidia or self.radeon:
            subprocess.call(prc + " &", shell=True)
            self.started_gpu = True

        self.gpu_button.set_sensitive(False)
        self.gpu_button2.set_sensitive(True)

    def on_gpu_button_clicked2(self, widget):
        if self.nvidia:
            prc_name = "ccminer"
        elif self.radeon:
            prc_name = "sgminer"
        for proc in psutil.process_iter():
            if proc.name() == prc_name:
                proc.kill()

        self.gpu_button.set_sensitive(True)
        self.gpu_button2.set_sensitive(False)
        self.started_gpu = False

    def on_cpu_button_clicked(self, widget):
        threads = self.combobox_threads.get_active_text()
        prc = self.dir + "/cpuminer/cpuminer -a nist5 -o stratum+tcp://cryptohub.online:3032 -u support@cryptohub.online -p x -b 127.0.0.1:4091 -t " + str(threads)
        subprocess.call(prc + " &", shell=True)
        self.started_cpu = True
        self.cpu_button.set_sensitive(False)
        self.cpu_button2.set_sensitive(True)


    def on_cpu_button_clicked2(self, widget):
        prc_name = "cpuminer"
        for proc in psutil.process_iter():
            if proc.name() == prc_name:
                proc.kill()
        self.cpu_button.set_sensitive(True)
        self.cpu_button2.set_sensitive(False)
        self.started_cpu = False


g = gui()
