#Get price, value and hectares of top crops in Idaho

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
#my_commodity_desc<- "OPERATORS" #FARM OPERATIONS, [AG LAND, INCL BUILDINGS - OPERATIONS WITH ASSET VALUE, MEASURED IN $ / ACRE; $ / OPERATION; $/ACRE; $]; [AG LAND, CROPLAND, PASTURED ONLY - ACRES] [Income, Net or Farm-related?]
my_group_desc <-"CROPS"
# query start year
my_year <- "2005"

# state of interest
my_state <- "ID"

###--------------------------------------#
# Download data and turn into dataframe
#####

# final path string
path_id_ops <- paste0("api/api_GET/?key=", nass_key, "&sector_desc=", my_group_desc, "&year=", my_year, "&state_alpha=", my_state)
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
# Subset Data based on highest value crops
#####

categories<-c("AREA HARVESTED", "PRICE RECEIVED", "YIELD")
#crops<-c("HOPS ", "PEACHES ", "PLUMS & PRUNES ", "PLUMS & PRUNES, ORGANIC ","PLUMS, ORGANIC ", "PEARS, ORGANIC ","PEACHES, ORGANIC ","GRAPES, ORGANIC ", "CHERRIES, SWEET ","MINT, PEPPERMINT, OIL ", "MINT, SPEARMINT, OIL " )
id_sales <- id_ops_raw_data %>%
  #filter to specific data
  #filter(statisticcat_desc=="SALES") %>%
  #filter(unit_desc=="$") %>%
  filter(statisticcat_desc %in% categories)%>%
  filter(agg_level_desc=="STATE") %>%
  filter(reference_period_desc == 'YEAR') %>%
  # trim white space from ends (note: 'Value' is a character here, not a number)
  mutate(value_trim = str_trim(Value)) %>%
  # select only the columns we'll need
  select(asd_desc,
         agg_level_desc, year, short_desc, class_desc, domain_desc, value_char =value_trim, unit_desc, commodity_desc) %>%
  # filter out entries with codes '(D)' and '(Z)'
  filter(value_char != "(D)" & value_char != "(Z)") %>% 
  # remove commas from number values and convert to R numeric class
  mutate(value = as.numeric(str_remove(value_char, ","))) %>%
  # remove unnecessary columns
  select(-value_char)%>%
  separate(short_desc, c("crop", 'info'), "- ") 
  #filter(crop %in% crops)

write.csv(id_sales, file='IdahoSales_2005.csv')

plot(id_sales$year[id_yeilds$crop == 'HOPS '], id_sales$value[id_sales$crop == 'HOPS '])
plot(id_sales$year[id_sales$crop == 'HOPS ' && id_sales$info == "AREA HARVESTED"], id_sales$value[id_sales$crop == 'HOPS ' && id_sales$info == "AREA HARVESTED"])

