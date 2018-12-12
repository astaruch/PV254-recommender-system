# Potrebne knihovny - pokud je dosud nemate, je treba je nejdrive nainstalovat, napr. funkci "install.packages"
library (agricolae)	#	pro Scheffeho test
library (car)	#	pro Levenuv test


tabulka <- read.csv2 (file = "pv254-barbsdelrey.csv", sep = ',')
tabulka$score_sum <- as.numeric(levels(tabulka$score_sum))[tabulka$score_sum]


# Podivame se na cetnosti, prumery a mediany
table (tabulka$algorithm_type)
table (tabulka)
tapply (tabulka$score_sum, tabulka$algorithm_type, mean)
tapply (tabulka$score_sum, tabulka$algorithm_type, median)

#	Grafy 
par (mfrow = c (1, 2))
plot.design (score_sum ~ algorithm_type, data = tabulka, fun = mean)
plot.design (score_sum ~ algorithm_type, data = tabulka, fun = median)
par (mfrow = c (1, 1))
barvy <- c ("red", "green", "cyan", "orange")

# Boxplot a overeni homogenity rozptylu
boxplot (score_sum ~ algorithm_type, data = tabulka, col = barvy, xlab = "barbsdelrey", ylab = "score_sum")
points (tabulka$algorithm_type, tabulka$score_sum, pch = 4)
# Bartlettuv test
bartlett.test (score_sum ~ algorithm_type, data = tabulka)
# Bartlettuv test
leveneTest (score_sum ~ algorithm_type, data = tabulka)

# Neparametricka varianta ANOVy - Kruskalluv-Wallisuv test
KWTest <- kruskal (tabulka$score_sum, tabulka$algorithm_type)
KWTest$groups
plot(KWTest, las = 1)
#	=> lisi se dvojice A-B, A-C, A-D, C-D
