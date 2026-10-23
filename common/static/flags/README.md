# Country Flags

The SVG flags in this directory come from [flag-icons](https://github.com/lipis/flag-icons).
This project includes both image sets:

- `4x3/` — flags with a 4:3 aspect ratio;
- `1x1/` — square flags.

The styles are in `common/static/css/flag-icons.css` and reference the SVG files
using paths relative to the stylesheet. Django Admin loads this stylesheet. For
example, the Ukrainian flag can be displayed as:

```html
<span class="fi fi-ua"></span>
```

The class after `fi-` is the country's lowercase, two-letter ISO 3166-1 alpha-2
code. Add the `fis` class to use the square version:

```html
<span class="fi fi-ua fis"></span>
```

When updating the assets, keep the CSS and SVG files in sync and preserve the
`../flags/4x3/` and `../flags/1x1/` paths. The `flag-icons` project is distributed
under the [MIT License](https://github.com/lipis/flag-icons/blob/main/LICENSE).

Many thanks to the `flag-icons` maintainers and contributors for creating and
maintaining this useful open-source project.
