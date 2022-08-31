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
