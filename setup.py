from distutils.core import setup
import py2exe
import os, sys

# Find GTK+ installation path
__import__('gtk')
m = sys.modules['gtk']
gtk_base_path = m.__path__[0]
print(gtk_base_path)

def generate_data_files(prefix, tree, file_filter=None):
    data_files = []
    for root, dirs, files in os.walk(os.path.join(prefix, tree)):
        to_dir = os.path.relpath(root, prefix)

        if file_filter is not None:
            file_iter = (fl for fl in files if file_filter(root, fl))
        else:
            file_iter = files

        data_files.append((to_dir, [os.path.join(root, fl) for fl in file_iter]))

    non_empties = [(to, fro) for (to, fro) in data_files if fro]

    return non_empties


GTK_RUNTIME_DIR = os.path.join(
    os.path.split(os.path.dirname(m.__file__))[0], "runtime")

GTK_THEME_DEFAULT = os.path.join("share", "themes", "Default")
GTK_THEME_WINDOWS = os.path.join("share", "themes", "MS-Windows")
GTK_GTKRC_DIR = os.path.join("etc", "gtk-2.0")
GTK_GTKRC = "gtkrc"
GTK_WIMP_DIR = os.path.join("lib", "gtk-2.0", "2.10.0", "engines")
GTK_WIMP_DLL = "libwimp.dll"
GTK_ICONS = os.path.join("share", "icons")

data_files_gtk = (
                # Use the function above...
                generate_data_files(GTK_RUNTIME_DIR, GTK_THEME_DEFAULT) +
                generate_data_files(GTK_RUNTIME_DIR, GTK_THEME_WINDOWS) +
                #generate_data_files(GTK_RUNTIME_DIR, GTK_ICONS) +

                # ...or include single files manually
                [
                    (GTK_GTKRC_DIR, [
                        os.path.join(GTK_RUNTIME_DIR,
                            GTK_GTKRC_DIR,
                            GTK_GTKRC)
                    ]),

                    (GTK_WIMP_DIR, [
                        os.path.join(
                            GTK_RUNTIME_DIR,
                            GTK_WIMP_DIR,
                            GTK_WIMP_DLL)
                    ])
                ]

                + ['readme.txt']
            )

#print(data_files_gtk)

setup(
    windows=[{"script": "miner.py", 'icon_resources': [(1, "icon.ico")]}],
    options={"py2exe": { 'dll_excludes': [ "MSVCP90.dll", 'msvcr71.dll', "IPHLPAPI.DLL", "NSI.dll",  "WINNSI.DLL",  "WTSAPI32.dll", "mswsock.dll", "powrprof.dll", "user32.dll", "shell32.dll", "wsock32.dll", "advapi32.dll", "kernel32.dll", "ntwdblib.dll", "ws2_32.dll", "oleaut32.dll", "ole32.dll"], 'includes': ['cairo', 'pango', 'pangocairo', 'atk', 'gobject', 'gio', 'gtk.keysyms','psutil','_psutil_mswindows','psutil._psutil_windows','psutil._pswindows']}},
    zipfile=None,
    data_files=data_files_gtk
)
