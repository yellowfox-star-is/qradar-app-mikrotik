# qradar-app-mikrotik

Simple visualization of data gathered via [Mikrotik DSM](https://github.com/yellowfox-star-is/qradar-mikrotik-dsm).

Be warned,<br />
the current UI is very "programmer graphics" (ugly but usable).
I also have a more experience working on backends, rather than frontends, so the visual is a direct impact of that. 

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Inside QRadar

supports only QRadar with Python 3

1. Download packaged zip from [Releases](https://github.com/yellowfox-star-is/qradar-app-mikrotik/releases/latest)
2. Install via Extensions Management

### Outside QRadar

1. Install Docker
2. Install [QRadar App SDK](https://exchange.xforce.ibmcloud.com/hub/extension/517ff786d70b6dfa39dde485af6cbc8b)
3. Download source files
4. Navigate to source directory
5. Edit qenv.ini file with location of your qradar instance
6. run with `qapp run`

## Usage

1. Select date range in popup calendar.
   * Pay attention to the time on bottom of callendar.
2. Click Load Data to start to load data.
3. Wait for all fetches to complete.
4. View data.

Visual cues when loading:
* number of currently running fetches is viewed
* time how all fetches is measured

## Contributing

Check DSM editor to better data collection.

Add more things to visualize.

Better the UI.

## License

This project is licensed under the terms of the [MIT license](LICENSE.md).<br>
Go use the project ^-^

If you  make a work out of this. I would rather you make it open too
and contribute to the open library of code, to benefit us all.
<br>
But I can't and won't stop you, so feel free to do whatever.

Also feel free to mail me, with what you have done with it. I am curious.

## Credits

### Used libraries:

- [qradar-app-sdk](https://www.ibm.com/support/pages/qradar-whats-new-app-framework-sdk-v200)
- [easytimer](https://github.com/albert-gonzalez/easytimer.js)
- [horizontal_timeline](https://codepen.io/Seigiard/pen/MWwoqQ)
- [flatpickr](https://github.com/flatpickr/flatpickr)

### Used LLMs:

- [ChatGPT](https://chat.openai.com/)
- [LLaMA.cpp](https://github.com/ggerganov/llama.cpp)
- [Vicuna](https://vicuna.lmsys.org/)

Hey, hey pst.<br>
If you wanna develop for qradar. Firstly. don't. Their documentation is shit.<br>
But if you still wanna... [this](https://ibmsecuritydocs.github.io/qradar_appfw_v2/) helped me.