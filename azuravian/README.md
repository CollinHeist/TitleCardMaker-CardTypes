# TitleColorMatchTitleCard
## Description
A modification of [GradientLogoTitleCard](https://github.com/CollinHeist/TitleCardMaker-CardTypes/tree/master/Beedman) to include the option to auto-select font color based on logo color.  It will also automatically crop off extraneous transparent space from the logo.

## Specification
The logo file is passed into this card the same way as the [LogoTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/LogoTitleCard#specification), i.e.:

```yaml
series:
  Peacemaker:
    year: 2022
    extras:
      logo: ./source/Peacemaker (2022)/logo.png
```

To turn on automatic matching of colors, add the following to your template config:
```yaml
mytemplate:
  font:
    color: 'auto'
```

## Example Cards
<img src="https://raw.githubusercontent.com/azuravian/myimages/main/Summary.jpg" width="1000"/>

## Features
- Logo and text
- Gradient
- Left-aligned
- Auto-matching text to logo color

# SciFiTitleCard
## Description
A multi-overlay card designed to look like a heads up display.  Intended for use in Science Fiction series.

## Specification
The following extras can be specified to change the color and alpha (transparency) of each layer
overlay_bottom_color = The color you want to use for the bottom layer (teal in the 1st example card)
overlay_top_color = The color you want to use for the top layer (pink in the 1st example card)
overlay_middle_color = The color you want to use for the middle layer (white in the 1st example card)
overlay_rectangles_color = The color you want to use for the rectangles (green in the 1st example card)
overlay_base_alpha = The transparency (between 0 and 1) you want to use for the black surrounding layer (defaults to 1 or fully opaque)
overlay_bottom_alpha = The transparency (between 0 and 1) you want to use for the bottom layer (defaults to 0.6 or 60% opaque)
overlay_top_alpha = The transparency (between 0 and 1) you want to use for the top layer (defaults to 0.6 or 60% opaque)
overlay_middle_alpha = The transparency (between 0 and 1) you want to use for the middle layer (defaults to 0.6 or 60% opaque)
overlay_rectangles_alpha = The transparency (between 0 and 1) you want to use for the rectangles (defaults to 0.6 or 60% opaque)

## Example Cards
<img src="https://raw.githubusercontent.com/azuravian/myimages/main/SciFiTitleCard/Example1.jpg" width="500"/><img src="https://raw.githubusercontent.com/azuravian/myimages/main/SciFiTitleCard/Example2.jpg" width="500"/>

## Features
- Customizable HUD
- Custom font

