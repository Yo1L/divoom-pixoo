import base64  # noqa: D100
import json

from PIL import Image
import requests


class Pixoo:  # noqa: D101
    ### proxy to communicate with a DIVOOM PIXOO. ###
    __timeout = 10
    __pic_id = 0
    __text_id = 0
    __refresh_pic_id_limit = 32
    debug = False

    def __init__(  # noqa: D107
        ### constructor... ###
        self,
        address,
        size=64,
        debug=False,
        auto_pic_id_reset=True,
        timeout=10,
    ) -> None:
        assert size in [16, 32, 64], (
            "Invalid screen size (pixels). " "Valid options are 16, 32, and 64"
        )

        self.auto_pic_id_reset = auto_pic_id_reset
        self.address = address
        self.debug = debug
        self.size = size

        # Generate URL
        self.__url = "http://{0}/post".format(address)
        self.__timeout = timeout

        # Retrieve the counter
        self.__load_counter()

        # Resetting if needed
        if self.auto_pic_id_reset and self.__pic_id > self.__refresh_pic_id_limit:
            self.reset_pic_id()

    def send_images(self, images: [Image], speed=60) -> None:
        self.__increment_pic_id()

        offset = 0
        json_data = {"Command": "Draw/CommandList", "CommandList": []}

        for frame in images:
            json_data["CommandList"].append(
                {
                    "Command": "Draw/SendHttpGif",
                    "PicNum": len(images),
                    "PicWidth": 64,
                    "PicOffset": offset,
                    "PicID": self.__pic_id,
                    "PicSpeed": speed,
                    "PicData": str(
                        base64.b64encode(
                            bytearray(frame.tobytes("raw", "RGB"))
                        ).decode()
                    ),
                }
            )

            offset += 1

        self.__request(json_data)

    def send_image(self, image: Image):
        self.__increment_pic_id()

        self.__request(
            {
                "Command": "Draw/SendHttpGif",
                "PicNum": 1,
                "PicWidth": 64,
                "PicOffset": 0,
                "PicID": self.__pic_id,
                "PicSpeed": 1000,
                "PicData": str(
                    base64.b64encode(bytearray(image.tobytes("raw", "RGB"))).decode()
                ),
            }
        )

    def __reset_text_id(self):
        self.__text_id = 1

    def clear_text(self):
        self.__reset_text_id()
        self.__request({"Command": "Draw/ClearHttpText"})

    def send_text(
        self,
        text,
        speed=10,
        xy=(0, 0),
        dir=0,
        font=0,
        align=1,
        color="#FFFF00",
    ):
        assert len(xy) == 2, "Invalid xy. " "xy must be a list of len 2"

        self.__text_id += 1
        if self.__text_id >= 20:
            self.__reset_text_id()

        self.__request(
            {
                "Command": "Draw/SendHttpText",
                "TextId": self.__text_id,
                "x": xy[0],
                "y": xy[1],
                "dir": dir,
                "font": font,
                "TextWidth": 64 - xy[0],
                "speed": speed,
                "TextString": text,
                "color": color,
                "align": align,
            }
            #             {
            # "Command":"Draw/SendHttpText",
            # "TextId":4,
            # "x":0,
            # "y":40,
            # "dir":0,
            # "font":4,
            # "TextWidth":56,
            # "speed":10,
            # "TextString":"hello, Divoom",
            # "color":"#FFFF00",
            # "align":1
            # }
        )

    def set_visualizer(self, equalizer_position):
        ### set visualizer. ###
        self.__request(
            {"Command": "Channel/SetEqPosition", "EqPosition": equalizer_position}
        )

    def set_clock(self, clock_id):
        ### set clock face. ###
        self.__request(
            {"Command": "Channel/SetClockSelectId", "ClockId": int(clock_id)},
        )

    def set_custom_channel(self, index):
        self.set_custom_page(index)
        self.set_channel(3)

    def set_custom_page(self, index):
        self.__request(
            {"Command": "Channel/SetCustomPageIndex", "CustomPageIndex": index}
        )

    def set_screen(self, on=True):
        ### set screen on/off. ###
        self.__request({"Command": "Channel/OnOffScreen", "OnOff": 1 if on else 0})

    def get_all_conf(self):
        return self.__request({"Command": "Channel/GetAllConf"})

    def get_state(self):
        data = self.get_all_conf()
        if data["LightSwitch"] == 1:
            return True
        else:
            return False

    def get_brightness(self):
        data = self.get_all_conf()
        return data["Brightness"]

    def reset_pic_id(self):
        if self.debug:
            print("[.] Resetting counter remotely")

        self.__request({"Command": "Draw/ResetHttpGifId"})

    def __load_counter(self):
        data = self.__request({"Command": "Draw/GetHttpGifId"})
        if data:
            self.__pic_id = int(data["PicId"])
            if self.debug:
                print("[.] Counter loaded and stored: " + str(self.__pic_id))

    def __increment_pic_id(self):
        # Add to the internal counter
        self.__pic_id = self.__pic_id + 1

        # Check if we've passed the limit and reset the counter for the animation remotely
        if self.auto_pic_id_reset and self.__pic_id >= self.__refresh_pic_id_limit:
            self.reset_pic_id()
            self.__pic_id = 1

    def __request(self, data: list):
        response = requests.post(self.__url, json.dumps(data), timeout=self.__timeout)
        json_response = response.json()

        if json_response["error_code"] != 0:
            print(data)
            print(json_response)
            return False
        else:
            return json_response
