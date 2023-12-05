# Card Types for the `TitleCardMaker`
This repository contains user-created card types for use in the [TitleCardMaker](https://github.com/CollinHeist/TitleCardMaker).

# Contributing
In order to contribute your own custom Card Type to this repository, follow these steps:

1. [Create a fork](https://github.com/CollinHeist/TitleCardMaker-CardTypes/fork) of this repo
2. Create a folder with your Github username (i.e. `/CollinHeist/`)
3. Inside that folder, create a `README.md` file with at least one example and a description of your card (as well as any nuances / features)
4. Add your custom Card Type Python class (that follows the specifications outlined [here](https://github.com/CollinHeist/TitleCardMaker/wiki/Custom-Card-Types#creating-a-custom-card-type)) to your username folder
   * Be sure to [read the wiki](https://github.com/CollinHeist/TitleCardMaker-CardTypes/wiki) on the specific syntax required for your CardType to work as a remote asset.
   * It can be helpful to look at my example (`CollinHeist/BetterStandardTitleCard`), or an existing card type, for syntax help
5. Edit the below [table](https://github.com/CollinHeist/TitleCardMaker-CardTypes#available-card-types) with your username and an example of your card
6. Submit a pull request to this repository

> NOTE: By nature of how the Maker pulls in these files, all pull requests and Card Types will be thoroughly vetted for security implications. Please help me out in this process by documenting your code, and avoiding any unnecessary obfuscations.

# Available Card Types
| Creator | `card_type` Specification | Example |
| :---: | :---: | :--- |
| Wdvh | `Wdvh/WhiteTextStandard` | <img src="https://user-images.githubusercontent.com/17693271/169709359-ffc9e109-b327-44e9-b78a-7276f77fe917.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextAbsolute` | <img src="https://user-images.githubusercontent.com/17693271/169709482-6bb023ab-4986-464e-88d6-0e05ad75d0d3.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextTitleOnly` | <img src="https://user-images.githubusercontent.com/17693271/178131552-4ca8cb30-067e-4e04-9d68-472a8f384345.jpg" height="200"/> |
| lyonza | `lyonza/WhiteTextBroadcast` | <img src="https://user-images.githubusercontent.com/1803189/171089736-f60a6ff2-0914-432a-a45d-145323d39c42.jpg" height="200"/> |
| Wdvh | `Wdvh/StarWarsTitleOnly` | <img src="https://user-images.githubusercontent.com/17693271/178131539-c7b55ced-b9ba-4564-8153-a998454e1742.jpg" height="200"/> |
| Beedman | `Beedman/GradientLogoTitleCard` | <img src="https://user-images.githubusercontent.com/17693271/178131602-8d93401b-4b5a-4301-8248-42705547ec6f.jpg" height="200"/> |
| Yozora | `Yozora/SlimTitleCard` | <img src="https://cdn.discordapp.com/attachments/975108033531219979/977614937457303602/S01E04.jpg" height="200"/> |
| Yozora | `Yozora/BarebonesTitleCard` | <img src="https://user-images.githubusercontent.com/17693271/178131581-055fd7ca-0bda-464a-9e4d-67c88adb0a06.jpg" height="200"/> |
| Yozora | `Yozora/RetroTitleCard` | <img src="https://user-images.githubusercontent.com/17693271/178131717-e9c387f7-625c-4654-a49d-93595687e359.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextAbsoluteLogo` | <img src="https://user-images.githubusercontent.com/17693271/178131676-300601a4-bbdb-46ee-8f78-aa859d13d50c.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextStandardLogo` | <img src="https://user-images.githubusercontent.com/17693271/178131565-5351dd98-201e-4f70-a8ff-2311687ed981.jpg" height="200"/> |
| Wdvh | `Wdvh/WhiteTextTitleOnlyLogo` | <img src="https://user-images.githubusercontent.com/17693271/178131633-23a312ac-4e5f-4d1a-87cb-60b865a51fe7.jpg" height="200"/> |
| azuravian | `azuravian/TitleColorMatch` | <img src="https://user-images.githubusercontent.com/7379812/187586521-353ba09f-30a8-424b-bbf3-ee9036c9e638.jpg" height="200"/> |
| CollinHeist | `CollinHeist/BlacklistTitleCard` | <img src="https://user-images.githubusercontent.com/17693271/216839561-ec4a1c27-dcdc-4869-87dd-8d592a26aee2.jpg" height="200"/> |
| KHthe8th | `KHthe8th/TintedFramePlus` | <img src="https://github.com/khthe8th/TitleCardMaker-CardTypes/assets/5308389/d089a1b1-7458-4eaf-ad8d-59c7f332a7c1" height="200"/> |

# Using a Custom Card Type
The [available card types](#available-card-types) can all be specified within the Maker by adding the following:

```yaml
card_type: {USER/CARDTYPE}
```

To a specific series, template, or library. For example, to create The Blacklist in my example card type, it might look like:

```yaml
series:
  The Blacklist (2013):
    card_type: CollinHeist/BlacklistTitleCard
```
