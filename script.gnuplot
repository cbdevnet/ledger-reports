#!/usr/bin/gnuplot
TITLE = system("echo $TITLE")
LEGEND = system("echo $LEGEND")
SVGTITLE = system("echo $SVGTITLE")
set term svg size 1920,1080 enhanced font "Biolinum,10" name "".SVGTITLE
set grid
set xdata time
set title "".TITLE
set timefmt "%Y-%m-%d"
set format x "%Y-%m-%d"
set autoscale
set xzeroaxis linewidth 2
set boxwidth 0.95 relative
set style fill solid 0.25 border
set style line 1 lw 1 lc rgb "blue"
set style line 2 lw 1 lc rgb "red"
set style line 3 lw 1 lc rgb "black"
set style line 4 lw 1 lc rgb "sea-green"
set style increment user
