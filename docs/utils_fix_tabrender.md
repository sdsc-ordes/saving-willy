A js fix for certain UI elements, including maps, getting rendered into a
zero-sized frame by default. Here we resize it so it is visible once the tab is
clicked and no further interaction is required to see it.

::: src.utils.fix_tabrender
