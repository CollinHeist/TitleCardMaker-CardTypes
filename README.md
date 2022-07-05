# Card Types for the `TitleCardMaker`
This repository contains user-created card types for use in the [TitleCardMaker](https://github.com/CollinHeist/TitleCardMaker).

# Contributing
In order to contribute your own custom Card Type to this repository, follow these steps:

1. [Create a fork](https://github.com/CollinHeist/TitleCardMaker-CardTypes/fork) of this repo
2. Create a folder with your Github username (i.e. `/CollinHeist/`)
3. Inside that folder, create a `README.md` file with at least one example and a description of your card (as well as any nuances / features)
4. Add your custom Card Type Python class (that follows the specifications outlined [here](https://github.com/CollinHeist/TitleCardMaker/wiki/Custom-Card-Types#creating-a-custom-card-type)) to your username folder
   * Be sure to [read the wiki](https://github.com/CollinHeist/TitleCardMaker-CardTypes/wiki) on the specific syntax required for your CardType to work as a remote asset.
5. Edit the below [table]() with your username and an example of your card
6. Submit a pull request to this repository

> NOTE: By nature of how the Maker pulls in these files, all pull requests and Card Types will be thoroughly vetted for security implications. Please help me out in this process by documenting your code, and avoiding any unnecessary obfuscations.

# Available Card Types
| Creator | `card_type` Specification | Example |
| :---: | :---: | :--- |
| Wdvh | `Wdvh/WhiteTextStandard` | <img src="https://user-images.githubusercontent.com/17693271/169709359-ffc9e109-b327-44e9-b78a-7276f77fe917.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextAbsolute` | <img src="https://user-images.githubusercontent.com/17693271/169709482-6bb023ab-4986-464e-88d6-0e05ad75d0d3.jpg" height="200"/>
| Yozora | `Yozora/SlimTitleCard` | <img src="https://cdn.discordapp.com/attachments/975108033531219979/977614937457303602/S01E04.jpg" height="200"/> |
| Yozora | `Yozora/BarebonesTitleCard` | <img src="https://i.ibb.co/tBPsxpc/Westworld-2016-S04-E01.jpg" height="200"/> |
| Yozora | `Yozora/RetroTitleCard` | <img src="https://i.ibb.co/0tnJJ6P/Stranger-Things-2016-S03-E02.jpg" height="200"/> |


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
