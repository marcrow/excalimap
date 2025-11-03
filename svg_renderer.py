"""
SVG Renderer for Excalimap
Converts Excalidraw JSON elements to clean SVG without font embedding issues
"""

import json
import base64
from xml.sax.saxutils import escape


class SVGRenderer:
    """Renders Excalidraw JSON to SVG format"""

    def __init__(self, excalidraw_json, theme='dark'):
        """
        Initialize SVG renderer

        Args:
            excalidraw_json: Excalidraw JSON string or dict
            theme: 'dark' or 'light'
        """
        if isinstance(excalidraw_json, str):
            self.data = json.loads(excalidraw_json)
        else:
            self.data = excalidraw_json

        self.elements = self.data.get('elements', [])
        self.files = self.data.get('files', {})
        self.app_state = self.data.get('appState', {})
        self.theme = theme

        # Calculate bounding box
        self.min_x, self.min_y, self.max_x, self.max_y = self._calculate_bounds()

    def _calculate_bounds(self):
        """Calculate the bounding box of all elements"""
        if not self.elements:
            return 0, 0, 800, 600

        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for element in self.elements:
            if element.get('isDeleted'):
                continue

            x = element.get('x', 0)
            y = element.get('y', 0)
            width = element.get('width', 0)
            height = element.get('height', 0)

            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)

        # Add padding
        padding = 20
        return (
            min_x - padding,
            min_y - padding,
            max_x + padding,
            max_y + padding
        )

    def _get_stroke_dasharray(self, stroke_style):
        """Convert Excalidraw stroke style to SVG dasharray"""
        if stroke_style == 'dashed':
            return '8 12'
        elif stroke_style == 'dotted':
            return '2 6'
        return None

    def _render_rectangle(self, element):
        """Render a rectangle element"""
        x = element.get('x', 0)
        y = element.get('y', 0)
        width = element.get('width', 0)
        height = element.get('height', 0)

        stroke_color = element.get('strokeColor', '#000')
        background_color = element.get('backgroundColor', 'transparent')
        stroke_width = element.get('strokeWidth', 1)
        stroke_style = element.get('strokeStyle', 'solid')
        opacity = element.get('opacity', 100) / 100

        dasharray = self._get_stroke_dasharray(stroke_style)
        dasharray_attr = f' stroke-dasharray="{dasharray}"' if dasharray else ''

        return f'''<rect x="{x}" y="{y}" width="{width}" height="{height}"
            fill="{background_color}"
            stroke="{stroke_color}"
            stroke-width="{stroke_width}"{dasharray_attr}
            opacity="{opacity}" />'''

    def _render_text(self, element):
        """Render a text element"""
        x = element.get('x', 0)
        y = element.get('y', 0)
        width = element.get('width', 0)
        height = element.get('height', 0)
        text = element.get('text', '')

        stroke_color = element.get('strokeColor', '#000')
        font_size = element.get('fontSize', 20)
        text_align = element.get('textAlign', 'left')
        vertical_align = element.get('verticalAlign', 'top')

        # Escape text for XML
        text = escape(text)

        # Calculate text position based on alignment
        text_x = x
        if text_align == 'center':
            text_x = x + width / 2
        elif text_align == 'right':
            text_x = x + width

        # Calculate vertical position
        text_y = y
        lines = text.split('\n')
        line_height = font_size * 1.2
        total_text_height = len(lines) * line_height

        if vertical_align == 'middle':
            text_y = y + (height - total_text_height) / 2 + font_size
        elif vertical_align == 'bottom':
            text_y = y + height - total_text_height + font_size
        else:  # top
            text_y = y + font_size

        # Render multi-line text
        svg_lines = []
        for i, line in enumerate(lines):
            line_y = text_y + (i * line_height)
            svg_lines.append(f'''<tspan x="{text_x}" dy="{line_height if i > 0 else 0}">{line}</tspan>''')

        anchor = 'middle' if text_align == 'center' else ('end' if text_align == 'right' else 'start')

        return f'''<text x="{text_x}" y="{text_y}"
            fill="{stroke_color}"
            font-size="{font_size}"
            font-family="Arial, sans-serif"
            text-anchor="{anchor}">
            {''.join(svg_lines)}
        </text>'''

    def _render_line(self, element):
        """Render a line element (used for output connections)"""
        x = element.get('x', 0)
        y = element.get('y', 0)
        points = element.get('points', [[0, 0]])

        stroke_color = element.get('strokeColor', '#000')
        stroke_width = element.get('strokeWidth', 2)

        # Convert points to path
        if not points:
            return ''

        path_parts = [f'M {x + points[0][0]} {y + points[0][1]}']
        for point in points[1:]:
            path_parts.append(f'L {x + point[0]} {y + point[1]}')

        path_d = ' '.join(path_parts)

        return f'<path d="{path_d}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="none" />'

    def _render_arrow(self, element):
        """Render an arrow element"""
        x = element.get('x', 0)
        y = element.get('y', 0)
        points = element.get('points', [[0, 0]])

        stroke_color = element.get('strokeColor', '#000')
        stroke_width = element.get('strokeWidth', 2)

        # Convert points to path
        if not points:
            return ''

        path_parts = [f'M {x + points[0][0]} {y + points[0][1]}']
        for point in points[1:]:
            path_parts.append(f'L {x + point[0]} {y + point[1]}')

        path_d = ' '.join(path_parts)

        # Add arrowhead if needed
        end_arrowhead = element.get('endArrowhead')
        marker_end = ''
        if end_arrowhead == 'triangle' or end_arrowhead:
            marker_end = ' marker-end="url(#arrowhead)"'

        return f'<path d="{path_d}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="none"{marker_end} />'

    def _render_image(self, element):
        """Render an image element"""
        x = element.get('x', 0)
        y = element.get('y', 0)
        width = element.get('width', 0)
        height = element.get('height', 0)
        file_id = element.get('fileId')

        if not file_id or file_id not in self.files:
            return ''

        file_data = self.files[file_id]
        mime_type = file_data.get('mimeType', 'image/png')
        data_url = file_data.get('dataURL', '')

        # Extract base64 data if it's a data URL
        if data_url.startswith('data:'):
            # Use the data URL directly
            href = data_url
        else:
            # Assume it's already base64
            href = f'data:{mime_type};base64,{data_url}'

        return f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="{href}" />'

    def _create_arrowhead_marker(self):
        """Create SVG marker definition for arrowheads"""
        arrow_color = self.app_state.get('viewBackgroundColor', '#fff')
        if self.theme == 'dark':
            arrow_color = '#fff'
        else:
            arrow_color = '#000'

        return f'''
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10"
                    refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                <path d="M0,0 L0,6 L9,3 z" fill="{arrow_color}" />
            </marker>
        </defs>'''

    def render(self):
        """Render the complete SVG"""
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y

        background_color = self.app_state.get('viewBackgroundColor', '#000')

        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" ',
            f'     viewBox="{self.min_x} {self.min_y} {width} {height}" ',
            f'     width="{width}" height="{height}">',
            f'<rect x="{self.min_x}" y="{self.min_y}" width="{width}" height="{height}" fill="{background_color}" />',
            self._create_arrowhead_marker()
        ]

        # Render elements in order
        for element in self.elements:
            if element.get('isDeleted'):
                continue

            element_type = element.get('type')

            try:
                if element_type == 'rectangle':
                    svg_parts.append(self._render_rectangle(element))
                elif element_type == 'text':
                    svg_parts.append(self._render_text(element))
                elif element_type == 'line':
                    svg_parts.append(self._render_line(element))
                elif element_type == 'arrow':
                    svg_parts.append(self._render_arrow(element))
                elif element_type == 'image':
                    svg_parts.append(self._render_image(element))
            except Exception as e:
                # Skip problematic elements but continue rendering
                print(f"Warning: Could not render element {element.get('id')}: {e}")
                continue

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def save(self, output_path):
        """Save SVG to file"""
        svg_content = self.render()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
