import re
import yaml

from config import Config
from models.command import Command
from models.info import Info
from models.out import Out
from models.title import Title
from models.container import Container
from utils import Utils


class ParserMD:

    @staticmethod
    def parse_sub_items(parent_item, sub_item):
        new_obj = None
        if sub_item["type"] == "command":
            new_obj = Command(
                text=sub_item["text"],
                comment=sub_item.get("comment"),
                icon=sub_item.get("icon"),
                tool_link=sub_item.get("tool_link"),
                link=sub_item.get("link"),
                out=sub_item.get("out"),
                is_cve=sub_item.get("is_cve")
            )
        if sub_item["type"] == "info":
            new_obj = Info(
                text=sub_item["text"],
                comment=sub_item.get("comment"),
                link=sub_item.get("link"),
                is_cve=sub_item.get("is_cve")
            )

        if sub_item["type"] == "command" or sub_item["type"] == "info":
            for out_item in sub_item.get("out", []):
                ParserMD.parse_out_items(new_obj, out_item)

        if sub_item.get("content") is not None:
            for sub_sub_item in sub_item.get("content"):
                if new_obj is not None:
                    ParserMD.parse_sub_items(new_obj, sub_sub_item)
        parent_item.content.append(new_obj)

    @staticmethod
    def parse_out_items(parent_item, sub_item):
        new_obj = None
        if sub_item["type"] == "out":
            new_obj = Out(
                text=sub_item.get("text"),
                object_id=sub_item.get("id"),
                color=sub_item.get("color")
            )
        parent_item.out.append(new_obj)

    @staticmethod
    def parse_md_to_objects(md_data, conf, md_file='unknown'):
        # # load yml
        # with open("mindmap/conf.yml", "r", encoding="utf-8") as file:
        #     conf = yaml.safe_load(file)

        colors = conf['color_id']

        parent = {}
        level = 0
        id = 0
        in_code_block = False
        code_block_lines = []
        code_block_id = 0
        code_block_level = 0  # Track the level where code block started
        container_just_created = False

        for line_num, line in enumerate(md_data, start=1):
            #print(f'[+] parse line : {repr(line)} | in_code_block={in_code_block} | level={level}')

            # Safety check: if we hit structural markdown while in code block, close the code block
            if in_code_block and (line.startswith('#') or (line.strip().startswith('- ') and not line.strip().startswith('- ``` '))):
                # Force close the code block
                #print(f'    >>> Force closing code block due to structural markdown')
                id += 1
                full_text = '\n'.join(code_block_lines)
                text = full_text
                new_obj = Command(text=text, comment="", link=None, is_cve=False, out=[],
                                object_id=hash(f'{id}'), icon=None, tool_link=None)
                level = code_block_level
                parent[level] = new_obj

                # Check if parent level exists
                if (level-1) not in parent:
                    raise ValueError(
                        f"Markdown hierarchy error in '{md_file}':\n"
                        f"  Found code block at indentation level {level}\n"
                        f"  but no parent exists at level {level-1}.\n"
                        f"  Ensure you have a proper hierarchy:\n"
                        f"    # Container → ## Title → - ``` code block\n"
                        f"  Current line: {line_num}"
                    )

                parent[level-1].content.append(new_obj)
                code_block_lines = []
                in_code_block = False
                # Now continue processing this line normally (don't skip it)

            # Handle multi-line code blocks with ```
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block - create a command object with the full text
                    id += 1
                    full_text = '\n'.join(code_block_lines)
                    #print(f'    Code block finished. Full text: {repr(full_text)}')
                    # Don't use split_text for code blocks - preserve original line breaks
                    text = full_text
                    new_obj = Command(text=text, comment="", link=None, is_cve=False, out=[],
                                    object_id=hash(f'{id}'), icon=None, tool_link=None)
                    # Use the level we saved when starting the code block
                    level = code_block_level
                    # Code blocks CAN have children, so set them as parent
                    parent[level] = new_obj

                    # Check if parent level exists
                    if (level-1) not in parent:
                        raise ValueError(
                            f"Markdown hierarchy error in '{md_file}':\n"
                            f"  Found code block at indentation level {level}\n"
                            f"  but no parent exists at level {level-1}.\n"
                            f"  Ensure you have a proper hierarchy:\n"
                            f"    # Container → ## Title → - ``` code block\n"
                            f"  Current line: {line_num}"
                        )

                    parent[level-1].content.append(new_obj)
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start of code block - use current level (set by empty list item or previous item)
                    in_code_block = True
                    code_block_lines = []
                    # Use current level, ensuring it's at least 3
                    if level < 3:
                        code_block_level = 3
                    else:
                        code_block_level = level
                continue

            if in_code_block:
                # Accumulate lines in code block
                # Replace leading spaces with non-breaking space (U+00A0) to preserve them in Excalidraw
                stripped_line = line.rstrip('\n')
                # Count and replace leading spaces
                leading_spaces = len(stripped_line) - len(stripped_line.lstrip(' '))
                if leading_spaces > 0:
                    stripped_line = '\u00A0' * leading_spaces + stripped_line.lstrip(' ')
                code_block_lines.append(stripped_line)
                #print(f'    Added to code block: {repr(stripped_line)}')
                continue

            cve = False
            id = id + 1
            out = []
            url = None
            if ">>>" in line:
                id_out = 0
                outputs = line.split('>>>')[1:]
                column = 0
                for output in outputs:
                    for o in output.split('||'):
                        color = Config.default_out_color
                        if o.strip() in conf['out'].keys():
                            color_id = conf['out'][o.strip()]
                            color = colors[color_id]
                        text = o.strip().rstrip('\n')
                        text = Utils.split_text(text, Config.out_new_line_nb_chars)
                        new_out = Out(text=text, object_id=hash(f'{id}-{id_out}'), color=color)
                        # TODO dirty refactor
                        if column == 0:
                            out.append(new_out)
                        if column == 1:
                            if out[-1].out is not None:
                                out[-1].out.append(new_out)
                            else:
                                out[-1].out = [new_out]
                        if column == 2:
                            if out[0].out[-1].out is not None:
                                out[0].out[-1].out.append(new_out)
                            else:
                                out[0].out[-1].out = [new_out]
                        id_out += 1
                    column += 1
                line = line.split('>>>')[0]

            if "@CVE@" in line:
                cve = True
                line = line.replace('@CVE@','')

            if line.startswith('# '):
                match = re.search(r"# (.+)", line)
                color = Config.info_background_color
                text = match.group(1)
                if text.strip() in conf['container_color'].keys():
                    color_id = conf['container_color'][text.strip()]
                    color = colors[color_id]
                text = Utils.split_text(match.group(1), Config.container_new_line_nb_chars)
                container = Container(text=text, color=color, position=None, content=[], object_id=hash(f'{id}'))
                level = 1
                if level not in parent.keys():
                    parent[level] = container
                container_just_created = True
                continue

            # Auto-description: Plain text after container title becomes a title
            if container_just_created and level == 1 and not line.startswith('##') and not line.startswith('-') and line.strip() and not line.startswith('<!--'):
                # This is a description line after container - make it a title
                id += 1
                text = Utils.split_text(line.strip(), Config.title_new_line_nb_chars)
                title_obj = Title(text=text, is_cve=False, content=[], out=[], object_id=hash(f'{id}'))
                level = 2
                parent[level] = title_obj
                parent[level-1].content.append(title_obj)
                container_just_created = False
                continue

            if line.startswith('##'):
                container_just_created = False

            if line.startswith('## '):
                match = re.search(r"## (.+)", line)
                text = Utils.split_text(match.group(1), Config.title_new_line_nb_chars)
                title_obj = Title(text=text, is_cve=cve, content=[], out=out, object_id=hash(f'{id}'))
                level = 2
                parent[level] = title_obj
                parent[level-1].content.append(title_obj)
                continue

            if line.startswith('<!--'):
                match = re.search(r'<!--\s+cve\s+-->', line)
                if match:
                    parent[level].cve = True

            if line.strip().startswith('['):
                match = re.search(r"\((https?://[^\)]+)\)", line)
                if match:
                    url = match.group(1)
                    parent[level].link = url

            if line.strip().startswith('- `') and '```' not in line:
                match = re.search(r"(\s*)- `(.+)`", line)
                spaces = len(match.group(1))
                level = int(3 + spaces/2)
                text = Utils.split_text(match.group(2), Config.command_new_line_nb_chars)

                # tool parsing
                cmd_to_parse = text.replace('proxychains ', '')
                tool = cmd_to_parse.split(' ')[0]
                icon = None
                tool_link = None
                if tool in conf['tools'].keys():
                    icon = conf['tools'][tool].get('icon')
                    tool_link = conf['tools'][tool].get('link')

                new_obj = Command(text=text,comment="",link=None,is_cve=cve, out=out, object_id=hash(f'{id}'), icon=icon, tool_link=tool_link)
                parent[level] = new_obj

                # Check if parent level exists
                if (level-1) not in parent:
                    raise ValueError(
                        f"Markdown hierarchy error in '{md_file}':\n"
                        f"  Found command at indentation level {level} (line: '{line.strip()}')\n"
                        f"  but no parent exists at level {level-1}.\n"
                        f"  Ensure you have a proper hierarchy:\n"
                        f"    # Container → ## Title → - `command` → (2-space indent) - child\n"
                        f"  Current line: {line_num}"
                    )

                parent[level-1].content.append(new_obj)

            elif line.strip().startswith('-'):
                # Check if this line contains a code block marker
                if '```' in line:
                    # This is "- ```" format - extract level and start code block
                    spaces_match = re.search(r"(\s*)-\s*", line)
                    if spaces_match:
                        spaces = len(spaces_match.group(1))
                        level = int(3 + spaces / 2)
                        # Start code block at this level
                        in_code_block = True
                        code_block_lines = []
                        code_block_level = level
                        #print(f'    >>> Started code block at level {level}')
                    continue

                match = re.search(r"(\s*)- (.+)", line)
                if match:
                    spaces = len(match.group(1))
                    level = int(3 + spaces / 2)
                    content = match.group(2).strip()

                    # Skip if content is empty or only whitespace
                    if not content:
                        # Empty list item - just set level for next item
                        continue

                    text = Utils.split_text(content, Config.info_new_line_nb_chars)
                    new_obj = Info(text=text,comment="",link=None,is_cve=cve, out=out, object_id=hash(f'{id}'))
                    parent[level] = new_obj

                    # Check if parent level exists
                    if (level-1) not in parent:
                        raise ValueError(
                            f"Markdown hierarchy error in '{md_file}':\n"
                            f"  Found item at indentation level {level} (line: '{line.strip()}')\n"
                            f"  but no parent exists at level {level-1}.\n"
                            f"  Ensure you have a proper hierarchy:\n"
                            f"    # Container → ## Title → - item → (2-space indent) - child → (4-space indent) - grandchild\n"
                            f"  Current line: {line_num}"
                        )

                    parent[level-1].content.append(new_obj)
                else:
                    # Empty list item (just "-" with no text and maybe no space) - might be followed by code block
                    # Calculate level but don't create an object yet
                    spaces_match = re.search(r"(\s*)-\s*$", line)
                    if spaces_match:
                        spaces = len(spaces_match.group(1))
                        level = int(3 + spaces / 2)

        return container
