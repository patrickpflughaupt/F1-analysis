# load dependencies
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(dtplyr))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(ggridges))

# define path
path <- "~/Documents/01-Computing/Kaggle/02-F1/scripts/"
setwd(path)

# load data sets 
df.results <- fread(file = paste0(path, "../data/raw_data/results.csv"))
df.qualifying <- fread(file = paste0(path, "../data/raw_data/qualifying.csv"))
df.lap_times <- fread(file = paste0(path, "../data/raw_data/lap_times.csv"))

# convert time string to time unit
times <- as.POSIXct(df.lap_times$lap_time, format = "%M:%OS")

# delta lap times (difference between each every laps) per driver per race per year
Year = 2018
df.delta.lap.times <- lazy_dt(df.lap_times, immutable = FALSE) %>% 
    mutate(lap_time = times,  
           time.delta = difftime(lap_time, lead(lap_time), units = "secs")) %>% 
    filter(time.delta < 10 & time.delta > -10, season >= Year) %>% 
    select(c(circuit_id, driver, time.delta, season)) %>% 
    filter(driver == "hamilton" | driver == "max_verstappen") %>% 
    na.omit() %>% 
    as_tibble()

p <- df.delta.lap.times %>% 
    ggplot(aes(x = time.delta, y = driver, fill = circuit_id)) + 
    geom_density_ridges() + 
    facet_grid(circuit_id ~ season, switch = "y") + 
    theme_ridges() + 
    theme(legend.position = "none", 
          axis.text.y = element_blank(), 
          strip.text.y.left = element_text(angle = 0)) + 
    labs(x = "Difference (secs)",
         y = "", 
         title = "Delta lap times of Hamilton (Top) vs. Verstappen (Bottom)", 
         subtitle = paste0(Year, " - 2021"))

ggsave(filename = paste0("../figures/2018-2021_delta_laptimes_ham-vs-ver.pdf"), 
       plot = p, width = 9, height = 13)

# select only hamilton and verstappen's race and qualifying times 
df.filtered.results <- lazy_dt(df.results, immutable = FALSE) %>% 
    filter(season >= Year, driver == "hamilton" | driver == "max_verstappen") %>% 
    select(c("season", "round", "circuit_id", "driver", "status")) %>% 
    filter(status == "Finished") %>% 
    as_tibble() 

df.filtered.qualifying <- lazy_dt(df.qualifying, immutable = FALSE) %>% 
    filter(season >= Year, driver_name == "Lewis  Hamilton  HAM" | driver_name == "Max  Verstappen  VER") %>% 
    mutate(driver = ifelse(driver_name == "Lewis  Hamilton  HAM", "hamilton", "max_verstappen")) %>% 
    select(-c("driver_name", "car")) %>% 
    filter(nchar(qualifying_time) > 0) %>% 
    as_tibble() 

df.results.qualifying <- inner_join(
    df.filtered.results, df.filtered.qualifying, by = c("season", "round", "driver")) %>% 
    mutate(qualifying.time = as.POSIXct(qualifying_time, format = "%M:%OS")) %>% 
    select(-qualifying_time) %>%
    na.omit()

df.avg.race.pace <- lazy_dt(df.lap_times, immutable = FALSE) %>% 
    mutate(lap_time = times) %>% 
    select(c(circuit_id, driver, lap_time, season)) %>% 
    filter(driver == "hamilton" | driver == "max_verstappen") %>% 
    group_by(season, circuit_id, driver) %>% 
    na.omit() %>% 
    as_tibble()

# obtain the 95% CI for each driver for each race for each season
df.CI <- df.avg.race.pace %>% 
    group_by(season, circuit_id, driver) %>% 
    summarise(MEAN = mean(lap_time),
              SD = sd(lap_time),
              ERROR = qnorm(0.975)*SD/sqrt(n())) %>% 
    mutate(LEFT.CI = MEAN-ERROR, RIGHT.CI = MEAN+ERROR) %>% 
    select(-c(MEAN, SD, ERROR))

# filter results only for those that fall within the 95% CI
df.avg.race.pace <- left_join(
    df.avg.race.pace, df.CI, by = c("season", "circuit_id", "driver")) %>% 
    group_by(season, circuit_id, driver) %>% 
    filter(lap_time <= RIGHT.CI & lap_time >= LEFT.CI)

# ham vs. ver race pace over qualifying pace split into 3 intervals
df.racequali.pace <- lazy_dt(df.results.qualifying, immutable = TRUE) %>% 
    select(-c("round", "grid_position")) %>% 
    inner_join(., df.avg.race.pace, by = c("season", "circuit_id", "driver")) %>% 
    group_by(season, circuit_id, driver) %>% 
    mutate(laps = 1:n(),
           race.interval = cut(laps, breaks = 3)) %>% 
    group_by(season, circuit_id, driver, race.interval) %>% 
    summarise(mean.rq.pace = mean(lap_time),
              qualifying.time = mean(qualifying.time)) %>% 
    select(-race.interval) %>% 
    mutate(interval = 1:n(), 
           interval = ifelse(interval == 1, "0-start", ifelse(interval == 2, "1-mid", "2-end"))) %>% 
    mutate(mean.diff = mean.rq.pace-qualifying.time) %>% 
    select(-c(mean.rq.pace, qualifying.time)) %>% 
    group_by(season, circuit_id, interval) %>% 
    mutate(time.delta = lead(mean.diff)-mean.diff) %>% 
    as_tibble() %>% 
    na.omit()

p <- df.racequali.pace %>% 
    ggplot(aes(x = time.delta, y = ..density..)) + 
    geom_density(, fill = "skyblue") + 
    geom_vline(xintercept = 0, linetype = "dashed", alpha = 0.4) +
    facet_grid(season ~ interval, space = "free_y") + 
    coord_cartesian(xlim = c(-5, 5)) + 
    labs(x = "Time delta (secs)", 
         y = "Density", 
         title = "Race vs. quali pace split into 3 intervals: Ham (better < 0) vs. Ver (better > 0)", 
         subtitle = paste0(Year, " - 2021"))
ggsave(filename = paste0("../figures/", Year,"-2021_racepace-vs-quali-3intervals_ham-vs-ver.pdf"), plot = p, width = 7)