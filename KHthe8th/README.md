# `KHthe8th/TintedFramePlusTitleCard`
## Description
A combination of the [TintedFrameTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/TintedFrameTitleCard) and the [StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard) for the best of both worlds. It has the same extras you can pass to tinted frame, and you can still modify the top/middle/bottom frame elements with extras but now it adds the episode title text above the bottom frame element (this is not modifiable). The top element will default to logo now, and title is no longer an option (as it is always shown above the bottom element).

## Example
![House (2004) - S01E02](https://github.com/khthe8th/TitleCardMaker-CardTypes/assets/5308389/d089a1b1-7458-4eaf-ad8d-59c7f332a7c1)

## Specification
Image shown above has template:

```yaml
templates:
  myTemplate:
    library: <<library>>
    card_type: KHthe8th/TintedFramePlusTitleCard
    extras:
      logo: ./source/<<clean_title>> (<<year>>)/logo.png
      episode_text_font_size: 1.3
```
It also has all optional valid extras listed on [TintedFrameTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/TintedFrameTitleCard#valid-extras), as well as stroke_color listed on [StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard#custom-stroke-color)
