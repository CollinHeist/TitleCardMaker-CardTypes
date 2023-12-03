# `KHthe8th/TintedFramePlusTitleCard`
## Description
A combination of the [TintedFrameTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/TintedFrameTitleCard) and the [StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard) for the best of both worlds. It has the same extras you can pass to tinted frame, and you can still modify the top/middle/bottom frame elements with extras but now it adds the episode title text above the bottom frame element (this is not modifiable).

## Example
![Fringe (2008) - S01E02](https://github.com/khthe8th/TitleCardMaker-CardTypes/assets/5308389/1b20569a-77f1-48eb-8dbb-e5dcba95cbdf)

## Specification
Image shown above has template:

```yaml
templates:
  crime:
    library: <<library>>
    card_type: KHthe8th/TintedFramePlusTitleCard
    extras:
      top_element: logo
      logo: ./source/<<clean_title>> (<<year>>)/logo.png
      episode_text_font_size: 1.3
```
It also has all optional valid extras listed on [TintedFrameTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/TintedFrameTitleCard), as well as stroke_color listed on [StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard#custom-stroke-color)
