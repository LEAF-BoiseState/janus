# Download and subset NASS AG Census Data
# Created following https://sheilasaia.rbind.io/post/2019-01-04-nass-api/

library(httr)
library(jsonlite)
library(tidycensus)
library(tidyverse)
library(purrr)
library(mapview)
library(dplyr)

# If you've never used your tidycensus API key in your R session, run this:
census_api_key("6fd2754dd1bdcc811b51c669667df2873b3bd56e")
nass_key <- "B5240598-2A7D-38EE-BF8D-816A27BEF504" #QuickStats

# NASS url
nass_url <- "http://quickstats.nass.usda.gov"

# commodity description of interest
my_commodity_desc<- "OPERATORS"

# query start year
my_year <- "2006"

# state of interest
my_state <- "ID"

###--------------------------------------#
# Download data and turn into dataframe
#####

# final path string
path_id_ops <- paste0("api/api_GET/?key=", nass_key, "&commodity_desc=", my_commodity_desc, "&year__GE=", my_year, "&state_alpha=", my_state)
#unpack JSON object
raw_id_ops <- GET(url = nass_url, path = path_id_ops)
char_raw_id_ops<- rawToChar(raw_id_ops$content)
# check size of object
nchar(char_raw_id_ops)
#turn into list
list_raw_id_ops<- fromJSON(char_raw_id_ops)
# apply rbind to each row of the list and convert to a data frame
id_ops_raw_data <- pmap_dfr(list_raw_id_ops, rbind)

###--------------------------------------#
# Subset Data 
#####
regions <- c("EAST", "SOUTHWEST", "SOUTH CENTRAL")

id_operators <- id_ops_raw_data %>%
  #filter to counties in southern Idaho
  filter(asd_desc %in% regions) %>%
  
  filter(agg_level_desc == "COUNTY") %>%
  filter(asd_desc == "SOUTHWEST") %>%
  
  filter(class_desc == "(ALL)")  %>%

  # trim white space from ends (note: 'Value' is a character here, not a number)
  mutate(value_trim = str_trim(Value)) %>%

  # select only the columns we'll need
  select(state_alpha, state_ansi, county_code, county_name, asd_desc,
         agg_level_desc, year, value_char =value_trim, unit_desc) %>%
  
  # filter out entries with codes '(D)' and '(Z)'
  filter(value_char != "(D)" & value_char != "(Z)") %>% 
  
  # remove commas from number values and convert to R numeric class
  mutate(value = as.numeric(str_remove(value_char, ","))) %>%

  # remove unnecessary columns
  select(-value_char) %>%
  
  # make a column with the county name and year (we'll need this for plotting)
  mutate(county_year = paste0(str_to_lower(county_name), "_", year)) %>%
  
  # make GEOID column to match up with county level spatial data (we'll need this for mapping)
  mutate(GEOID = paste0(state_ansi, county_code))

head(id_operators)



