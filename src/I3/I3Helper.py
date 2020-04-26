import i3ipc
import mss
import mss.tools
import subprocess
from PIL import Image, ImageDraw, ImageFont
from Icon.IconHelper import IconHelper


# Wrapper around i3
class I3Helper(object):
    def __init__(self, deck, config):
        self.deck = deck
        self.config = config
        self.i3 = i3ipc.Connection()
        self.workspaces = self.i3.get_workspaces()
        self.image_format = deck.key_image_format()
        self.default_icon = Image.open('Assets/i3_logo.png').convert("RGBA")
        self.vscode_icon = Image.open('Assets/vscode.png').convert("RGBA")
        self.terminal_icon = Image.open('Assets/terminal.png').convert("RGBA")
        self.browser_icon = Image.open('Assets/firefox.png').convert("RGBA")
        self.files_icon = Image.open('Assets/nautilus.png').convert("RGBA")
        self.media_icon = Image.open('Assets/spotify.png').convert("RGBA")
        self.pictures_icon = Image.open('Assets/images.png').convert("RGBA")
        self.android_icon = Image.open('Assets/android.png').convert("RGBA")
        self.libreoffice_icon = Image.open('Assets/libreoffice.png').convert("RGBA")
        self.api_icon = Image.open('Assets/api.png').convert("RGBA")
        self.communication_icon = Image.open('Assets/slack.png').convert("RGBA")

    def get_wm(self):
        cmd = "inxi -Sxx | grep Desktop | awk -F: '{ print $2 }'"
        inxi = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = inxi.communicate()[0].rstrip()

        return str(output).replace("b' ", "").replace("'", "")

    def get_key_config(self, key):
        # Make sure we have a Key config
        for k in self.config:
            if k['key'] == key:
                return k

        return None

    def get_key_image(self, key, state):
        key_config = self.get_key_config(key)

        if key_config["type"] == "workspace":
            return self.get_key_workspace_image(key_config)
        elif key_config["type"] in ["exit", "reload", "layout", "dummy"]:
            return IconHelper.prepare_fontawesome_image(self.image_format, key_config['icon'], key_config['text'])

    def get_workspace(self, key):
        for w in self.workspaces:
            if w.num == key:
                return w

        return None

    def get_key_workspace_image(self, key_config):
        # Check if workspace is visible
        workspace = None

        for ws in self.workspaces:
            if ws.num == key_config['workspace'] and ws.visible:
                workspace = ws
        if self.get_wm() != "sway 1.4 dm":
            if workspace:
                rect = workspace.rect

                with mss.mss() as sct:
                    monitor = {"top": rect.y, "left": rect.x, "width": rect.width, "height": rect.height}
                    raw_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", raw_img.size, raw_img.rgb).convert('RGBA')
            else:
                # Default i3 Icon
                img = self.default_icon
        else:
            current_workspace = {
                1: self.vscode_icon,
                2: self.terminal_icon,
                3: self.browser_icon,
                4: self.files_icon,
                5: self.media_icon,
                6: self.pictures_icon,
                7: self.android_icon,
                8: self.libreoffice_icon,
                9: self.api_icon,
                0: self.communication_icon
            }
            img = current_workspace.get(key_config['workspace'], key_config['workspace'])
        current_workspace_name = {
            "1": "C0D3",
            "2": "T3rM",
            "3": "Br0W53R",
            "4": "F1L3",
            "5": "M3D14",
            "6": "Gr4Ph1K",
            "7": "J4V4",
            "8": "CuRS3S",
            "9": "V3RS10N",
            "0": "C0MMuN1C"
        }
        title = current_workspace_name.get(key_config['text'], key_config['text'])
        return IconHelper.prepare_image(self.image_format, img, title)

    def go_to_workspace(self, workspace):
        self.i3.command("workspace number " + str(workspace))

        # Update workspaces (could be changed)
        self.workspaces = self.i3.get_workspaces()

    def switch_layout(self, key_config):
        self.i3.command("layout " + key_config["layout"])

        # Update workspaces (could be changed)
        self.workspaces = self.i3.get_workspaces()

    def reload(self):
        self.i3.command("reload")

    def exit(self):
        self.i3.command("exit")
