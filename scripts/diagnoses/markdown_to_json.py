"""Converts a markdown file to JSON.

This script is intended to be called from the command line with `python
markdown_to_json.py <input_file> <output_file>`. It will convert the markdown
file to JSON and write it to the output file.

This script was built and with Python 3.11, but as it relies only on the Python
standard library, it should work with any version of Python 3.
"""  # noqa: INP001

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any


class Node:
    """A class representing a node in a tree.

    Attributes:
        children (List[Node]): The child nodes of this node.
        level (int): The level of this node in the tree.
        text (str): The text associated with this node.
        header (bool): Whether this node is a header node.
    """

    def __init__(self, level: int = 0, *, header: bool = True) -> None:
        """Initializes a new instance of the Node class.

        Args:
            level: The level of this node in the tree.
            header: Whether this node is a header node.
        """
        self.children: list[Node] = []
        self.level: int = level
        self.text: str = ""
        self.header: bool = header

    def add_child(self, node: Node) -> None:
        """Adds a child node.

        Args:
            node: The child node to add.
        """
        self.children.append(node)

    def set_text(self, text: str) -> None:
        """Sets the node's text.

        Args:
            text: The text to set.
        """
        self.text = text

    def to_dict(
        self,
    ) -> dict[str, bool | str | list[dict[str, Any]]]:
        """Converts the node and its children to a dictionary.

        This is a recursive method that calls itself for each child.

        Returns:
            dict[str, bool | str | list[dict[str, Any]]]: The dictionary
                representation of the node.
        """
        return {
            "header": self.header,
            "text": self.text,
            "children": [child.to_dict() for child in self.children],
        }


def parse_markdown(file_path: str) -> list[dict[str, Any]]:
    """Parses a markdown file and returns its JSON representation.

    Args:
        file_path: The path to the markdown file.

    Returns:
        list[dict[str, Any]]: The JSON representation of the markdown file.
    """
    with pathlib.Path(file_path).open(encoding="utf-8") as file_buffer:
        lines = file_buffer.readlines()

    root = Node()
    stack = [root]
    current_content_node: Node = Node(header=False)

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("#"):
            level = stripped_line.count("#")
            text = stripped_line[level:].strip()

            if current_content_node.text:
                stack[-1].add_child(current_content_node)
                current_content_node = Node(header=False)

            node = Node(level)
            node.set_text(text)

            while level <= stack[-1].level:
                stack.pop()

            stack[-1].add_child(node)
            stack.append(node)
        elif stripped_line:
            current_content_node.set_text(
                (current_content_node.text + " " + stripped_line).strip(),
            )

    if current_content_node.text:
        stack[-1].add_child(current_content_node)

    children = [child.to_dict() for child in root.children]
    return [{"text": "root", "children": children, "header": True}]


if __name__ == "__main__":
    input_file: str = sys.argv[1]
    output_file = pathlib.Path(sys.argv[2])

    json_content: list[dict[str, Any]] = parse_markdown(input_file)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(json_content, file, indent=2)
