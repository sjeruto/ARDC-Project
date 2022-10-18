library(ggplot2)
library(tidyr)
library(dplyr)

setwd("~/Documents/UTS_3rd_semester/ilab2/github_repo/ARDC-Project")

gov_pos <- read.csv('num_gov_positions.csv') 


ggplot(gov_pos) +
 aes(x = num_gov_positions_bins, y = num_employees) +
 geom_bar(fill = "#014c98", stat = "identity") +
  scale_x_discrete(limits = c("<2", "2-4", "5-7", ">7")) +
  labs(x = "Number of government positions", y = "Number of Employees", 
       title = "Number of government positions previously held by lobbyist employees") +
  theme(panel.background = element_blank(),
        axis.text.x = element_text(color = "#7f7f80", face = "bold"),
        axis.text.y = element_text(color = "#7f7f80", face = "bold"),
        axis.title.x = element_text(color = "#7f7f80", face = "bold"),
        axis.title.y = element_text(color = "#7f7f80", face = "bold"),
        plot.title = element_text(color = "#7f7f80", face = "bold"),
        plot.caption = element_text(hjust = 0, color = "#7f7f80", size = 7)) +
  annotate(geom = "text", x = "<2", y= 27, label = "29 (36.25%)",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = "2-4", y= 41, label = "43 (53.75%)",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = "5-7", y= 3.25, label = "5 (6.25%)",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = ">7", y= 1.5, label = "3 (3.75%)",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2)

 

pos <- read.csv('position_stats.csv')

pos <- pos %>% mutate(per = (Total/sum(Total))*100)

ggplot(pos) +
  aes(x = FormerPosition, y = per) +
  geom_bar(fill = "#014c98", stat = "identity") +
  scale_x_discrete(limits = c('Media adviser/Press secretary', 
                              'Adviser',
                              'Chief of staff/senior adviser', 
                              'Member of Parliament/Senator')) +
  labs(x = "Former government positions", y = "Percentage of positions held", 
       title = "Percentage of government positions held") +
  theme(panel.background = element_blank(),
        axis.text.x = element_text(color = "#7f7f80", face = "bold"),
        axis.text.y = element_text(color = "#7f7f80", face = "bold"),
        axis.title.x = element_text(color = "#7f7f80", face = "bold"),
        axis.title.y = element_blank(),
        plot.title = element_text(color = "#7f7f80", face = "bold"),
        plot.caption = element_text(hjust = 0, color = "#7f7f80", size = 5)) +
  annotate(geom = "text", x = "Media adviser/Press secretary", y= 14.95, label = "17.95%",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = "Adviser", y= 30.33, label = "33.33%",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = "Chief of staff/senior adviser", y= 13.67, label = "16.67%",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  annotate(geom = "text", x = "Member of Parliament/Senator", y= 29.05, label = "32.05%",
           hjust = 0.5, vjust = 0.5, size = 4, check_overlap = TRUE, color = "white",
           fontface = 2) +
  coord_flip()
