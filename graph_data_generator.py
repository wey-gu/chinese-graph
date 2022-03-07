#!/usr/bin/env python3

import csv
import json
import pandas as pd
import os
import requests

from pypinyin import STYLE_BOPOMOFO, pinyin, Style
from pypinyin.contrib.tone_convert import to_initials, to_finals


class GraphDataGenerator:
    def __init__(self, output_path=None):
        self.path = output_path if output_path else os.path.join(os.getcwd(), 'output')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    @staticmethod
    def write_list_to_csv(list_to_write, file_path):
        keys = list_to_write[0].keys()
        with open(file_path, "w") as file:
            csvwriter = csv.DictWriter(file, fieldnames=keys, restval="NA")
            csvwriter.writeheader()
            csvwriter.writerows(list_to_write)

    def generate_graph_data(self):
        """
        Generate graph data
        The idioms comes from:
            https://github.com/antfu/handle/raw/main/src/data/idioms.json
        And vertices and edges will be in schema:
            - vertex tag:
                - idiom
                    - id
                    - pinyin
                - character
                    - id
                - pinyin
                    - id
                    - tone
                - pinyin_part
                    - id
                    - type
            - edge type:
                - with_character
                    - position
                - with_pinyin
                - with_pinyin_part
                    - part_type

        :return:
        """
        
        # Get idioms
        raw_idioms_URL = (
            "https://raw.githubusercontent.com/"
            "wey-gu/handle/main/src/data/idioms.json")
        raw_idioms = requests.get(raw_idioms_URL).json()

        # Generate vertices and edges
        idiom, character, character_pinyin, pinyin_part = [], [], [], []
        with_character, with_pinyin, with_pinyin_part = [], [], []

        for idiom_item in raw_idioms:
            idiom_item_id = idiom_item[0]
            idiom_item_pinyin = idiom_item[1].split() if len(
                idiom_item) > 1 else list(
                pinyin_item[0] for pinyin_item in pinyin(
                    idiom_item_id, style=Style.TONE3))

            # vertex: idiom
            idiom.append(
                {":VID(string)": idiom_item_id,
                "idiom.pinyin:string": idiom_item_pinyin})

            # Character
            for position, character_item in enumerate(idiom_item_id):
                pinyin_initial, pinyin_final = None, None
                with_character.append(
                    {":SRC_VID(string)": idiom_item_id,
                    ":DST_VID(string)": character_item,
                    "with_character.position:int": position})
                character.append({":VID(string)": character_item})
                character_pinyin_ = idiom_item_pinyin[position]  # 汉字拼音
                character_pinyin_tone = (
                    character_pinyin_[-1] if character_pinyin_[-1].isdigit()
                    else 0)  # 拼音音调
                character_pinyin_parts = character_pinyin_[:-1]  # 拼音部分，无音调
                pinyin_initial = to_initials(character_pinyin_)  # 拼音声母
                pinyin_final = to_finals(character_pinyin_)  # 拼音韵母

                # edge: with_pinyin
                with_pinyin.append(
                    {
                        ":SRC_VID(string)": idiom_item_id,
                        ":DST_VID(string)": character_pinyin_,
                        "with_pinyin.position:int": position})
                # vertex: character_pinyin
                character_pinyin.append(
                    {
                        ":VID(string)": character_pinyin_,
                        "character_pinyin.tone:int": character_pinyin_tone})

                if pinyin_initial:
                    # edge: with_pinyin_part
                    with_pinyin_part.append(
                        {"with_pinyin_part.part_type:string": "initial",
                        ":SRC_VID(string)": character_pinyin_,
                        ":DST_VID(string)": pinyin_initial})

                    # vertex: pinyin_part
                    pinyin_part.append(
                        {":VID(string)": pinyin_initial,
                        "pinyin_part.part_type:string": "initial"})
                if pinyin_final:
                    # edge: with_pinyin_part
                    with_pinyin_part.append(
                        {"with_pinyin_part.part_type:string": "final",
                        ":SRC_VID(string)": character_pinyin_,
                        ":DST_VID(string)": pinyin_final})
                    # vertex: pinyin_part
                    pinyin_part.append(
                        {":VID(string)": pinyin_final,
                        "pinyin_part.part_type:string": "final"})

        # Write to CSV,
        # the data volume is quite small, we do it in memory w/o batch in one go
        self.write_list_to_csv(idiom, f"{ self.path }/idiom.csv")
        self.write_list_to_csv(character, f"{ self.path }/character.csv")
        self.write_list_to_csv(character_pinyin, f"{ self.path }/character_pinyin.csv")
        self.write_list_to_csv(pinyin_part, f"{ self.path }/pinyin_part.csv")
        self.write_list_to_csv(with_character, f"{ self.path }/with_character.csv")
        self.write_list_to_csv(with_pinyin, f"{ self.path }/with_pinyin.csv")
        self.write_list_to_csv(with_pinyin_part, f"{ self.path }/with_pinyin_part.csv")


if __name__ == "__main__":
    graph_data_generator = GraphDataGenerator()
    graph_data_generator.generate_graph_data()
