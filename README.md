# ajSurvey

This script calculats the cartesian koordinates from polar coordinates.
The cartesian coordinate of the center is required, as well as one cartesian coordinate for reference.

The inputfile contains of horizontal angles, vertial angles, tilted distance in meters and vertical offset in meters.
This information is added from a .csv-file to the standard input, like this:

```bash
$ cat observasjoner.csv | python3 polarberegning.py
```

The known coordinates and the vertical offset of the center point are applied by using flags.
Use the -h flag to print the help message:

```bash
$ python3 polarberegning.py -h
```


