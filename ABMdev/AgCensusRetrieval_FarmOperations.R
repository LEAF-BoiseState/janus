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
my_commodity_desc<- "FARM OPERATIONS" #[AG LAND, INCL BUILDINGS - OPERATIONS WITH ASSET VALUE, MEASURED IN $ / ACRE; $ / OPERATION; $/ACRE; $]; [AG LAND, CROPLAND, PASTURED ONLY - ACRES] [Income, Net or Farm-related?]

# query start year
my_year <- "2000"
# state of interest
my_state <- "ID"

###--------------------------------------#
# Download data and turn into dataframe
#####

# final path string
path_id_farms <- paste0("api/api_GET/?key=", nass_key, "&commodity_desc=", my_commodity_desc, "&year__GE=", my_year, "&state_alpha=", my_state)
#unpack JSON object
raw_id_farms <- GET(url = nass_url, path = path_id_farms)
char_raw_id_farms<- rawToChar(raw_id_farms$content)
# check size of object
nchar(char_raw_id_farms)
#turn into list
list_raw_id_farms<- fromJSON(char_raw_id_farms)
# apply rbind to each row of the list and convert to a data frame
id_farms_raw_data <- pmap_dfr(list_raw_id_farms, rbind)
colnames(id_farms_raw_data)[colnames(id_farms_raw_data)=="CV (%)"] <- "CV"

#####--------------------------------------#
# Subset Data to State Level Aggreegates
#####


id_state_agg <- id_farms_raw_data %>%
  filter(agg_level_desc == "STATE") %>%
  
  # trim white space from ends (note: 'Value' is a character here, not a number)
  mutate(value_trim = str_trim(Value)) %>%
  # select only the columns we'll need
  select(state_alpha, state_ansi,
         agg_level_desc, year, class_desc, domain_desc, domaincat_desc, value_char =value_trim, unit_desc, CV) %>%
  
  # filter out entries with codes '(D)' and '(Z)'
  filter(value_char != "(D)" & value_char != "(Z)") %>% 
  # remove commas from number values and convert to R numeric class
  mutate(value = as.numeric(str_remove(value_char, ","))) %>%
  # remove unnecessary columns
  select(-value_char) 

#####--------------------------------------#
# Subset Data to County Level Aggreegates
#####
regions <- c("EAST", "SOUTHWEST", "SOUTH CENTRAL")
id_county_agg <- id_farms_raw_data %>%
  filter(agg_level_desc == "COUNTY") %>%
  filter(asd_desc %in% regions) %>%
  
  # trim white space from ends (note: 'Value' is a character here, not a number)
  mutate(value_trim = str_trim(Value)) %>%
  mutate(CV_trim = str_trim(CV)) %>%
  # select only the columns we'll need
  select(state_alpha, state_ansi,county_code, county_name, asd_desc,
         agg_level_desc, year, class_desc, domain_desc, domaincat_desc, value_char =value_trim, unit_desc, CV_char = CV_trim) %>%
  
  # filter out entries with codes '(D)' and '(Z)'
  filter(value_char != "(D)" & value_char != "(Z)") %>% 
  # remove commas from number values and convert to R numeric class
  mutate(value = as.numeric(str_remove(value_char, ","))) %>%
  mutate(CV = suppressWarnings(as.numeric(CV_char))) %>%
  # remove unnecessary columns
  select(-value_char) %>%
  select(-CV_char) %>%
  # make a column with the county name and year (we'll need this for plotting)
  mutate(county_year = paste0(str_to_lower(county_name), "_", year)) %>%
  # make GEOID column to match up with county level spatial data (we'll need this for mapping)
  mutate(GEOID = paste0(state_ansi, county_code))

#########################
# Subset Data 
###
variables<-c("TENURE", "AREA OPERATED") 
classes<-c("ORGANIZATION", "TYPOLOGY")


id_farms <- id_county_agg %>%
  #filter out categories of interest
  filter(domain_desc %in% variables | class_desc %in% classes) 
  



ggplot(id_farms) +
  geom_col(aes(x= domaincat_desc, y =value, fill=domaincat_desc))+
  facet_wrap(~county_name) +
  xlab("Type of Tenure") +
  ylab("Acres") +
  theme_bw()+
  theme(axis.text.x = element_blank())

###########
# PERCENTAGE OF IDAHO FARMS

id_state_perc <- id_farms_raw_data %>%
  filter(agg_level_desc == "STATE") %>%
  filter(unit_desc == "PCT OF FARM OPERATIONS") %>%
  # trim white space from ends (note: 'Value' is a character here, not a number)
  mutate(value_trim = str_trim(Value)) %>%
  # select only the columns we'll need
  select(state_alpha, state_ansi,
         agg_level_desc, year, class_desc, domain_desc, domaincat_desc, value_char =value_trim, unit_desc) %>%
  
  # filter out entries with codes '(D)' and '(Z)'
  filter(value_char != "(D)" & value_char != "(Z)") %>% 
  # remove commas from number values and convert to R numeric class
  mutate(value = as.numeric(str_remove(value_char, ","))) %>%
  # remove unnecessary columns
  select(-value_char) 

ggplot(id_state_perc %>% filter(domain_desc == "ORGANIZATION")) +
  geom_col(aes(x= domaincat_desc, y =value, fill=domaincat_desc))+
  xlab("Type of Farm") +
  ylab("Percent of Farm Operations") +
  theme_bw()+
  theme(axis.text.x = element_blank(), legend.position=c(0.25, 0.84))

ggplot(id_state_perc %>% filter(domain_desc == "AREA OPERATED")) +
  geom_col(aes(x= domaincat_desc, y =value, fill=domaincat_desc))+
  xlab("AREA CLASS") +
  ylab("Percent of Farm Operations") +
  theme_bw()+
  theme(axis.text.x = element_blank(), legend.position=c(0.7, 0.7))

ggplot(id_state_perc %>% filter(domain_desc == "ECONOMIC CLASS")) +
  geom_col(aes(x= domaincat_desc, y =value, fill=domaincat_desc))+
  xlab("Economic Class") +
  ylab("Percent of Farm Operations") +
  theme_bw()+
  theme(axis.text.x = element_blank(), legend.position=c(0.4, 0.78))
