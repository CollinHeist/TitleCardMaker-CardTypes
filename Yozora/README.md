# BarebonesTitleCard
## Description
This is a minimalistic custom CardType which emulates the main features of the [StarWarsTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StarWarsTitleCard). The main difference made to this CardType is the rework of the card to make it more universal in terms of style and design (such as changing the star-themed gradient)

## Example Cards
<img src="https://user-images.githubusercontent.com/17693271/177438468-ba114f2a-a80b-49ad-8c4f-2d0f39f1ad64.jpg" width="1000"/>

## Features
The following outlines the differences from the StandardTitleCard.

- Default font switched to Montserrat
- Episode and Title color change now supported
- Removed Gradient

All other features are as per the StarWarsTitleCard.

# RetroTitleCard
## Description
This is a custom CardType which is inspired by old-school VHS tapes and camcorders. The main difference made to this CardType is the rework of the card to make it more universal in terms of style and design (such as changing the star-themed gradient)

## Specification
By default, watched cards (as determined by your Plex library) will have `REWIND` on them, and be in black and white; while unwatched cards will have `PLAY` and be in full color. These can be overwritten via series [extras](https://github.com/CollinHeist/TitleCardMaker/wiki/Series-YAML-Files#extras) like so:

```yaml
series:
  Breaking Bad (2008):
    card_type: Yozora/RetroTitleCard
    extras:
      override_bw: bw
      override_style: play
```

This would make all cards black and white with `PLAY` on them. `override_bw` can be either `bw` or `color`; while `override_style` can be either `play` or `rewind`.

## Example Cards
<img src="https://user-images.githubusercontent.com/17693271/177438525-b3a36541-0caf-41ff-ae93-77c2d2318a48.jpg" width="1000"/>

## Example Watched Card
The below image showcases the greyscale option which is applied to watched episodes:
<img src="https://user-images.githubusercontent.com/17693271/177438598-09298454-b677-4619-8bc7-a54846031acf.png"/>

## Features
The following outlines the main features of this TitleCard

- Inspired by VHS and Camcorders
- Greyscale and "Play" text changed to "Rewind" for already watched episodes

All other features are as per the StandardTitleCard - including multi-line support, blur, and other options.

# SlimTitleCard
## Description
This is a minimalistic custom CardType which emulates the main features of the [StandardTitleCard](https://github.com/CollinHeist/TitleCardMaker/wiki/StandardTitleCard). The main difference made to this CardType is that the text is moved vertically down to allow the image to be showcased further..

## Example Cards
<img src="https://user-images.githubusercontent.com/17693271/170507855-19eb6f89-4d18-4a0a-89da-40be49497940.jpg" width="1000"/>

## Features
The following outlines the differences from the StandardTitleCard.

- Default font switched to Axiforma
- Episode and Season count moved vertically down
- Title moved vertically down

All other features are as per the StandardTitleCard - including multi-line support, blur, and other options.
