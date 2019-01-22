library(sp)
library(raster)
library(rgdal)

library(FedData)
library(cdlTools)

setwd("C:\Users\kendrakaiser\Dropbox\BSU\R\IM3\Data")
d01<-shapefile("d01.shp")
srb<-shapefile("SnakeRiverBasin.shp")


# Turn .tifs into rasters and mosaic them
setwd("H:/GIS/CDL")

ptn=c("2010_..\\.tif$", "2011_..\\.tif$", "2012_..\\.tif$", "2013_..\\.tif$","2014_..\\.tif$", "2015_..\\.tif$", "2016_..\\.tif$", "2017_..\\.tif$")
yr=c(2010:2017)
#create list of tiff files for each year 2010 -2017
for (i in 1:8){
  cdlname<- paste("files", yr[i], sep="")
  filist <- list.files(pattern = ptn[i])
  assign(Tnam, filist, envir = .GlobalEnv)
}

listnames<- c("files2010", "files2011", "files2012", "files2013", "files2014", "files2015", "files2016","files2017")

#import tiff as raster for each file (CA, ID, MT, NV, OR, WA, WY)

  for (i in 1:7){
  cdl <- raster(files2017[i])
  nam<-paste("cdl", yr[8], i, sep="_") 
  assign(nam, cdl, envir = .GlobalEnv)
  }


## mosaic
m10<-mosaic(cdl_2010_1, cdl_2010_2, cdl_2010_3, cdl_2010_4, cdl_2010_5, cdl_2010_6, cdl_2010_7, fun=max)
m11<-mosaic(cdl_2011_1, cdl_2011_2, cdl_2011_3, cdl_2011_4, cdl_2011_5, cdl_2011_6, cdl_2011_7, fun=max)
m12<-mosaic(cdl_2012_1, cdl_2012_2, cdl_2012_3, cdl_2012_4, cdl_2012_5, cdl_2012_6, cdl_2012_7, fun=max)
m13<-mosaic(cdl_2013_1, cdl_2013_2, cdl_2013_3, cdl_2013_4, cdl_2013_5, cdl_2013_6, cdl_2013_7, fun=max)
m14<-mosaic(cdl_2014_1, cdl_2014_2, cdl_2014_3, cdl_2014_4, cdl_2014_5, cdl_2014_6, cdl_2014_7, fun=max)
m15<-mosaic(cdl_2015_1, cdl_2015_2, cdl_2015_3, cdl_2015_4, cdl_2015_5, cdl_2015_6, cdl_2015_7, fun=max)
m16<-mosaic(cdl_2016_1, cdl_2016_2, cdl_2016_3, cdl_2016_4, cdl_2016_5, cdl_2016_6, cdl_2016_7, fun=max)
m17<-mosaic(cdl_2017_1, cdl_2017_2, cdl_2017_3, cdl_2017_4, cdl_2017_5, cdl_2017_6, cdl_2017_7, fun=max)

##clip to domain1 and then to the snake river plain
p<-cdl10_d01<-crop(m10, d01)
cdl10_srb<-crop(m10, srb)







               