# True ECS

Calculates true ECS coordinates from image x, y coordinates using corrected WCS
parameters.

## Usage

1. Set up permissions.

```
chmod +x astrometry_api.py true_ecs.py
```

2. Copy example configuration file to the project directory.

```
cp examples/config.yaml .
```

3. Open the file with your favorite text editor and put there your personal API
key from the Astrometry.net.  Change directory and filenames so they would
reflect your data-file structure.  You can use glob patterns and `{target}`
placeholer that will be replaced by name of the current target.  List all your
targets in the list of targets.

3. Run the program.

```
./true-ecs.py
```

## License

Copyright (C) 2024  Gabriel Szász

True-ECS is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

True-ECS is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
True-ECS.  If not, see <https://www.gnu.org/licenses/>.
﻿
