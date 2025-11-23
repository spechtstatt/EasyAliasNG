# -*- coding: utf-8 -*-
import FreeCAD
import re
from PySide import QtGui

"""
EasyAliasNG.FCMacro.py
(based on EasyAlias from https://wiki.freecad.org/Macro_EasyAlias - original author: TheMarkster)

This macro can be used to easily create aliases based on the contents of selected spreadsheet
cells in the previous column. As an example, suppose you wish to have the following:

A1: content = 'radius', B1: content = '5', alias = 'radius'
A2: content = 'height', B1: content = '15', alias = 'height'

This "NG" version adds support for processing cells without requiring that the spreadsheet is 
selected and also the correct handling of apostrophes (which is in the original wiki but not 
in the git repo). Additionally it provides a better error message in case of duplicates.

"""

__title__ = "EasyAliasNG"
__author__ = "Spechtstatt"
__url__ = "https://github.com/spechtstatt/EasyAliasNG"
__Wiki__ = "https://github.com/spechtstatt/EasyAliasNG"
__date__ = "2025.11.23" #year.month.date
__version__ = __date__

CELL_ADDR_RE = re.compile(r"([A-Za-z]+)([1-9]\d*)")
CUSTOM_ALIAS_RE = re.compile(r".*\((.*)\)")
MAGIC_NUMBER = 64
REPLACEMENTS = {
    " ": "_",
    ".": "_",
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ß": "ss",
    "'": ""
}

def getSpreadsheets():
    """
    Returns a set of selected spreadsheets in the active document or None if none is selected.
    :returns: a set of selected spreadsheets in the active document or None if none is selected
    :rtype: set
    """

    spreadsheets = set()
    for selectedObject in Gui.Selection.getSelection():
        if selectedObject.TypeId == 'Spreadsheet::Sheet':
            spreadsheets.add(selectedObject)
        elif selectedObject.TypeId == "App::Link":
            linkedObject = selectedObject.LinkedObject
            if linkedObject.TypeId == 'Spreadsheet::Sheet':
                spreadsheets.add(linkedObject)
    return spreadsheets

# The original implementatin of a1_to_rowcol and rowcol_to_a1 can be found here:
# https://github.com/burnash/gspread/blob/master/gspread/utils.py


def set_alias_with_diagnostics(spreadsheet, nextCell, alias):
    """
    Try to set an alias and show a more specific error message if it fails.
    Distinguishes (as far as possible) between:
      - invalid alias characters
      - duplicate aliases
      - other errors
    """
    try:
        spreadsheet.setAlias(nextCell, alias)
        return True
    except Exception as e:
        msg = str(e) if e is not None else ""        
        msg_lower = msg.lower()

        # Heuristic checks based on FreeCAD error messages
        if "invalid" in msg_lower and "character" in msg_lower:
            text = (
                "Unable to set alias <i>{alias}</i> at cell {cell} "
                "in spreadsheet <i>{sheet}</i>."
                "<br><br><b>Reason:</b> The alias contains invalid characters."
                "<br>Aliases must start with a letter and may only contain "
                "letters, digits and underscores."
                "<br><br><small>FreeCAD message: {msg}</small>"
            ).format(alias=alias, cell=nextCell,
                     sheet=spreadsheet.FullName, msg=msg)

            QtGui.QMessageBox.critical(None, "Invalid alias", text)

        elif ("already in use" in msg_lower or
              "already defined" in msg_lower or
              "duplicate" in msg_lower):
            text = (
                "Unable to set alias <i>{alias}</i> at cell {cell} "
                "in spreadsheet <i>{sheet}</i>."
                "<br><br><b>Reason:</b> This alias is already used elsewhere "
                "in this spreadsheet and must be unique."
                "<br><br><small>FreeCAD message: {msg}</small>"
            ).format(alias=alias, cell=nextCell,
                     sheet=spreadsheet.FullName, msg=msg)
            
            QtGui.QMessageBox.warning(None, "Duplicate alias", text)

        else:
            # Fallback: old generic message but with underlying error
            text = (
                "Unable to set alias <i>{alias}</i> at cell {cell} "
                "in spreadsheet <i>{sheet}</i>."
                "<br><br><b>Reason:</b> An unexpected error occurred."
                "<br><br><small>FreeCAD message: {msg}</small>"
            ).format(alias=alias, cell=nextCell,
                     sheet=spreadsheet.FullName, msg=msg)

            QtGui.QMessageBox.critical(None, "Alias error", text)

        return False


def iter_selected_spreadsheet_cells():
    """
    Returns a list of (spreadsheet, cell_name) tuples based on the current GUI selection.
    Works even if only cells in the spreadsheet are selected and the sheet itself
    is not selected in the tree.
    """
    result = []
    for sel in Gui.Selection.getSelectionEx():
        obj = sel.Object
        # follow links
        if obj.TypeId == "App::Link":
            obj = obj.LinkedObject

        if obj.TypeId != 'Spreadsheet::Sheet':
            continue

        # SubElementNames should contain things like 'A1', 'B3', etc.
        for sub_name in sel.SubElementNames:
            if CELL_ADDR_RE.match(sub_name):
                result.append((obj, sub_name))

    return result


def process_cell(spreadsheet, selectedCell):
    contents = spreadsheet.getContents(selectedCell)
    if not contents:
        return

    alias = textToAlias(contents)
    row, column = a1_to_rowcol(selectedCell)
    nextCell = rowcol_to_a1(row, column + 1)

    set_alias_with_diagnostics(spreadsheet, nextCell, alias)


def a1_to_rowcol(label:str):
    """Translates a cell's address in A1 notation to a tuple of integers.
    :param str label: A cell label in A1 notation, e.g. 'B1'. Letter case is ignored.
    :returns: a tuple containing `row` and `column` numbers. Both indexed from 1 (one).
    :rtype: tuple
    Example:
    >>> a1_to_rowcol('A1')
    (1, 1)
    """

    match = CELL_ADDR_RE.match(label)

    row = int(match.group(2))

    column_label = match.group(1).upper()
    column = 0
    for i, c in enumerate(reversed(column_label)):
        column += (ord(c) - MAGIC_NUMBER) * (26**i)

    return (row, column)

def rowcol_to_a1(row:int, column:int):
    """Translates a row and column cell address to A1 notation.
    :param row: The row of the cell to be converted. Rows start at index 1.
    :type row: int, str
    :param col: The column of the cell to be converted. Columns start at index 1.
    :type row: int, str
    :returns: a string containing the cell's coordinates in A1 notation.
    Example:
    >>> rowcol_to_a1(1, 1)
    A1
    """

    row = int(row)

    column = int(column)
    dividend = column
    column_label = ""
    while dividend:
        (dividend, mod) = divmod(dividend, 26)
        if mod == 0:
            mod = 26
            dividend -= 1
        column_label = chr(mod + MAGIC_NUMBER) + column_label

    label = "{}{}".format(column_label, row)

    return label

def textToAlias(text:str):
    # support for custom aliases between parentheses
    match = CUSTOM_ALIAS_RE.match(text)
    if match:
        return match.group(1)

    for character in REPLACEMENTS:
        text = text.replace(character,REPLACEMENTS.get(character))
    return text


def main():   
    # 1) Trying to use direct cell selection (no sheet selection needed)
    cell_pairs = iter_selected_spreadsheet_cells()

    if cell_pairs:
        for spreadsheet, selectedCell in cell_pairs:
            process_cell(spreadsheet, selectedCell)
        App.ActiveDocument.recompute()
        return

    # 2) Fallback (sheet selected in tree, then cells via ViewObject)
    spreadsheets = getSpreadsheets()
    if not spreadsheets:
        QtGui.QMessageBox.critical(
            None,
            "Error",
            "No spreadsheet or spreadsheet cells selected.\n"
            "Please select spreadsheet cells in the spreadsheet view."
        )
        return

    for spreadsheet in spreadsheets:
        for selectedCell in spreadsheet.ViewObject.getView().selectedCells():
            process_cell(spreadsheet, selectedCell)

    App.ActiveDocument.recompute()


main()
