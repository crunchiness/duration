# Script that calculates durations

As input takes a text file (file.txt) in this format:

```
2021-05-03
09:00-09:30 Planning the week
11:20-12:35 Pondering Voldemort's plans
14:15-14:25
14:30-16:00 Locating horcruxes

2021-05-04
10:30-13:10 Quidditch
15:10-17:00 Brooding
```

As output produces two files (new_file.txt, file.csv):

new_file.txt
```
2021-05-03
09:00-09:30 (00:30) Planning the week
11:20-12:35 (01:15) Pondering Voldemort's plans
14:15-14:25 (00:10)
14:30-16:00 (01:30) Locating horcruxes
Total: 03:25

2021-05-04
10:30-13:10 (02:40) Quidditch
15:10-17:00 (01:50) Brooding
Total: 04:30
```

file.csv
```
2021-05-03,03:25,Planning the week; Pondering Voldemort's plans; Locating horcruxes
2021-05-04,04:30,Quidditch; Brooding
```
