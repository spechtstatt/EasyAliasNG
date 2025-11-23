# EasyAliasNG (Fork)
**https://github.com/spechtstatt/EasyAliasNG**

Forked version of EasyAlias. Adds 
- the possibility to execute the macro without selectin the spreadsheet explicitely
- better error message in case of duplicates
- correct handling of apostrophes (original git repo does not include this)

Original macro documentation:  
https://wiki.freecadweb.org/Macro_EasyAlias

---

## What EasyAliasNG Does

**EasyAliasNG** automates the creation of spreadsheet cell aliases in FreeCAD.

Instead of manually assigning aliases through the GUI, you can:

1. Enter text into a column (e.g. column **A**).
2. Enter values or formulas into the next column (e.g. column **B**).
3. Select the text cells (in e.g. column **A**)
4. Run **EasyAlias**.

The macro will:

- clean the text (spaces → `_`, umlauts → `ae/oe/ue`, etc.)
- remove invalid characters (including `'`)
- assign the cleaned string as the alias to the cell **to the right**

---

## Example

|  | A         | B        | 
|--|-----------|----------|
|1 | radius   | 10       |
|2 | length   | 42       |

**With EasyAlias:**

1. Fill A1/A2
2. Select A1:A2  
3. Run the macro  

Aliases in column B are set automatically:
- B1 → `radius`
- B2 → `length`

---



