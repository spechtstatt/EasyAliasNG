# EasyAlias (Fork)

Forked because the original git repo does not support the handling of apostrophes. 

Original macro documentation:  
https://wiki.freecadweb.org/Macro_EasyAlias

Forked here:  
**https://github.com/spechtstatt/EasyAlias**

---

## What EasyAlias Does

**EasyAlias** automates the creation of spreadsheet cell aliases in FreeCAD.

Instead of manually assigning aliases through the GUI, you can:

1. Enter text into a column (e.g. column **A**).
2. Enter values or formulas into the next column (e.g. column **B**).
3. Select the text cells.
4. Run **EasyAlias**.

The macro will:

- clean the text (spaces → `_`, umlauts → `ae/oe/ue`, etc.)
- remove invalid characters (including `'`)
- assign the cleaned string as the alias to the cell **to the right**

---

## Example

| Cell | Content | Alias |
|------|---------|--------|
| A1 | `radius` | *(none)* |
| B1 | `5` | `radius` |
| A2 | `height` | *(none)* |
| B2 | `15` | `height` |

**With EasyAlias:**

1. Fill in A1/B1 and A2/B2  
2. Select A1:A2  
3. Run the macro  

Aliases are set automatically:
- B1 → `radius`
- B2 → `height`

---



