_Copyright © 2024 Gabriel Szász; see the end of the file for license
conditions._

# True-ECS

Calculates valid ECS coordinates (RA, DEC) from the image coordinates (X, Y)
using corrected WCS parameters.  This code is handy for the automated ex-post
astrometric corrections of large amounts of photometric measurements.

To determine correct WCS parameters, True-ECS queries Astrometry.net service
via API.  Astrometry.net ignores WCS parameters provided by the FITS header.
Instead, it directly cross-matches a dozen sources in the image using pattern
recognition and then uses these positions to determine the correct WCS
parameters inversely.  Since the method is agnostic to the original WCS
transform parameters, it covers many real-life scenarios that would otherwise
be hard to solve.


## Installation

1. Clone repository and change into the project directory.

```
git clone https://github.com/gszasz/true-ecs.git
cd true-ecs
```

2. Copy the example `config.yaml` into the project directory.

```
cp examples/config.yaml .
```

3. Open the file with your favorite text editor and put there your personal API
key from the Astrometry.net.  Change directory and filenames so they would
reflect your data-file structure.  You can use glob patterns and `{target}`
placeholer that will be replaced by name of the current target.  List all your
targets in the list of targets.

## Usage

Program has no command line options.  All options are defined by by the
`config.yaml` configuration file.

```
./true-ecs.py
```

# Note on copyright years

In copyright notices where the copyright holder is Gabriel Szász, then where a
range of years appears, this is an inclusive range that applies to every year
in the range.  For example: 2005-2008 represents the years 2005, 2006, 2007,
and 2008.

# License conditions

True-ECS is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

True-ECS is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
True-ECS.  If not, see <https://www.gnu.org/licenses/>.  ﻿
