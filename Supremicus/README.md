# DawnTitleCard

## Description
This is a custom CardType that produces title cards with left, centered or right aligned text on the bottom. CRT TV overlay (nobezel or bezel) with optional watched style based on Yozora's Retro title card for shows like Stranger Things with a retro theme.

## Specification
Below is a table of all valid series [extras](https://github.com/CollinHeist/TitleCardMaker/wiki/Series-YAML-Files#extras) parsed by this card.

| Label | Default Value | Description |
| :---: | :---: | :--- |
| `stroke_color` | `black` | Stroke color of episode and title text |
| `title_text_horizontal_shift` | `0` | How many pixels to horizontally shift the title text |
| `episode_text_vertical_shift` | `0` | How many pixels to vertically shift the episode text |
| `episode_text_font` | `Default` | Font file to use for the episode text |
| `episode_text_font_size` | `1.0` | Scalar of the size of the episode text |
| `episode_text_color` | `None` | Color to use separately for the episode text |
| `episode_text_stroke_color` | `None` | Color to use separately for the episode text stroke |
| `episode_text_kerning` | `18` | Pixel spacing between characters for the episode text |
| `separator` | `•` | Character to separate the season and episode text |
| `h_align` | `left` | Horizontal alignment. `left`, `center` or `right` |
| `crt_overlay` | `None` | Enable CRT TV Overlay `none`, `nobezel` or `bezel` |
| `crt_state_overlay` | `False` | Enable CRT TV Overlay watched/unwatched state `true`/`false` |
| `omit_gradient` | `True` | Omit gradient overlay `true`/`false` |

## Example Cards
<img src="https://raw.githubusercontent.com/Supremicus/tcm-images/main/Preview%20Cards/dawn-preview-card.jpg" width="1000"/>

## Features
- Left side, Centered or Right side alignment
- Adjustable Episode text vertical offset for custom fonts.
- Adjustable Title text horizontal offset for custom fonts.
- CRT TV overlay with a bezel or no bezel, with optional watched style (off by default)
- Optional Gradient

<br>

# HorizonTitleCard
## Description
This is a custom CardType that produces title cards similar to the left or right aligned with vertically centered text with optional symbol similar to the custom cards found on MediUX. CRT TV overlay (nobezel or bezel) with optional watched style based on Yozora's Retro title card for shows like Stranger Things with a retro theme.

## Specification
Below is a table of all valid series [extras](https://github.com/CollinHeist/TitleCardMaker/wiki/Series-YAML-Files#extras) parsed by this card.

| Label | Default Value | Description |
| :---: | :---: | :--- |
| `stroke_color` | `black` | Stroke color of episode and title text |
| `episode_text_vertical_shift` | `0` | How many pixels to vertically shift the episode text |
| `episode_text_font` | `Default` | Font file to use for the episode text |
| `episode_text_font_size` | `1.0` | Scalar of the size of the episode text |
| `episode_text_color` | `None` | Color to use separately for the episode text |
| `episode_text_stroke_color` | `None` | Color to use separately for the episode text stroke |
| `episode_text_kerning` | `18` | Pixel spacing between characters for the episode text |
| `separator` | `•` | Character to separate the season and episode text |
| `h_align` | `left` | Horizontal alignment. `left` or `right` |
| `symbol` | `None` | Custom symbol to use<br>Built-in: `acolyte`, `ahsoka`, `andor`, `bobafett`, `mandalorian`, `obiwan`, `witcher`<br>Custom: `logo` uses *source/show/logo.png* |
| `crt_overlay` | `None` | Enable CRT TV Overlay `none`, `nobezel` or `bezel` |
| `crt_state_overlay` | `False` | Enable CRT TV Overlay watched/unwatched state `true`/`false` |
| `omit_gradient` | `True` | Omit gradient overlay `true`/`false` |
| `alignment_overlay` | `False` | Enable alignment overlay to adjust custom font offsets `true`/`false` |

## Example Cards
<img src="https://raw.githubusercontent.com/Supremicus/tcm-images/main/Preview%20Cards/horizon-preview-card.jpg" width="1000"/>

## Features
- Left side or Right side alignment
- Built-in symbols for some shows, with the option to use your own custom symbols (uses logo.png in show source).
- Adjustable Episode text vertical offset for custom fonts.
- Alignment overlay to adjust custom fonts if not using the default font.
- CRT TV overlay with a bezel or no bezel, with optional watched style (off by default)
- Optional Radial Gradient

## Font Alignment & Custom Symbol
<img src="https://raw.githubusercontent.com/Supremicus/tcm-images/main/Preview%20Cards/horizon-setup.jpg" width="1000"/>

[12 Monkeys (2015) Example Logo](https://raw.githubusercontent.com/Supremicus/tcm-images/main/source/12%20Monkeys%20(2015)/logo.png)