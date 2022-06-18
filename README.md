# Card Types for the `TitleCardMaker`
This repository contains user-created card types for use in the [TitleCardMaker](https://github.com/CollinHeist/TitleCardMaker).

# Contributing
In order to contribute your own custom Card Type to this repository, follow these steps:

1. [Create a fork](https://github.com/CollinHeist/TitleCardMaker-CardTypes/fork) of this repo
2. Create a folder with your Github username (i.e. `/CollinHeist/`)
3. Inside that folder, create a `README.md` file with at least one example and a description of your card (as well as any nuances / features)
4. Add your custom Card Type Python class (that follows the specifications outlined [here](https://github.com/CollinHeist/TitleCardMaker/wiki/Custom-Card-Types#creating-a-custom-card-type)) to your username folder
   * Be sure to [read the wiki](https://github.com/CollinHeist/TitleCardMaker-CardTypes/wiki) on the specific syntax required for your CardType to work as a remote asset.
5. Edit the below [table](https://github.com/CollinHeist/TitleCardMaker-CardTypes#available-card-types) with your username and an example of your card
6. Submit a pull request to this repository

> NOTE: By nature of how the Maker pulls in these files, all pull requests and Card Types will be thoroughly vetted for security implications. Please help me out in this process by documenting your code, and avoiding any unnecessary obfuscations.

# Available Card Types
| Creator | `card_type` Specification | Example |
| :---: | :---: | :--- |
| Wdvh | `Wdvh/StarWarsTitleOnly` | <img src="https://github.com/Wdvh/TitleCardMaker-CardTypes/blob/c14f1b3759983a63e66982ba6517e2bc3f651dca/Wdvh/S01E01.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextStandard` | <img src="https://user-images.githubusercontent.com/17693271/169709359-ffc9e109-b327-44e9-b78a-7276f77fe917.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextAbsolute` | <img src="https://user-images.githubusercontent.com/17693271/169709482-6bb023ab-4986-464e-88d6-0e05ad75d0d3.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextTitleOnly` | <img src="https://github.com/CollinHeist/TitleCardMaker-CardTypes/blob/110c2ec729dbb20d8ed461e7cc5a07c54540f842/Wdvh/S01E07.jpg" height="200"/>
| Yozora | `Yozora/SlimTitleCard` | <img src="https://cdn.discordapp.com/attachments/975108033531219979/977614937457303602/S01E04.jpg" height="200"/> |
| lyonza | `lyonza/WhiteTextBroadcast` | <img src="https://user-images.githubusercontent.com/1803189/171089736-f60a6ff2-0914-432a-a45d-145323d39c42.jpg" height="200"/> |
| CollinHeist | `CollinHeist/BetterStandardTitleCard` | <img src="https://user-images.githubusercontent.com/17693271/169563977-a4711317-afc8-426f-ab85-9f4c76037dc0.jpg" height="200"/> |

# Using a Custom Card Type
The [available card types](#available-card-types) can all be specified within the Maker by adding the following:

```yaml
card_type: {USER/CARDTYPE}
```

To a specific series, template, or library. For example, to create Breaking Bad in the example card type, it might look like:

```yaml
series:
  Breaking Bad:
    year: 2008
    card_type: CollinHeist/BetterStandardTitleCard
```
