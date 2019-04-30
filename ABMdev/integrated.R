#########################################################################################################
# Urbanization model incorporating a spatial prisoner's dilemma and conformist transmission of land ethic
#########################################################################################################

library( dplyr )

rm(list=ls())

##### Create a social network of agents

# generate initial population
x <- 1:50
y <- 1:50

# number of iterations
numstep <- 50
numcell <- 2500

pop <- expand.grid(x, y)
names(pop) <- c("x", "y")

# generate initial adjacency matrix 
adj_mat <- matrix( data=0, nrow=numcell, ncol=numcell )

# do this for the number of iterations (50)
# do this for each cell

for( i in 1:numstep){
  
  for( j in 1:numcell) {
    z <- sample(4, 1)
    if( z == 1){
      pop$x[j] <- pop$x[j] - 1
      if (pop$x[j] == 0) {pop$x[j] <- max(x)}
    }
    else if(z == 2){
      pop$y[j] <- pop$y[j] + 1
      if (pop$y[j] > max(y) ) {pop$y[j] <- 1}
    }
    else if(z == 3){
      pop$x[j] <- pop$x[j] + 1
      if (pop$x[j] > max(x) ) {pop$x[j] <- 1}
    }
    else if(z == 4){
      pop$y[j] <- pop$y[j] - 1
      if (pop$y[j] == 0 ) {pop$y[j] <- max(y)}
    }
  }
  
  # check for overlaps and update adjacency matrix
  
  r <- match( paste0(pop$x, pop$y),  paste0(pop$x, pop$y) )
  
  for (ii in 1:numcell){
    adj_mat[ which( match(r, r[ii]) == 1)[1], which( match(r, r[ii]) == 1)[2] ] <- 1
    adj_mat[ which( match(r, r[ii]) == 1)[2], which( match(r, r[ii]) == 1)[1] ] <- 1
  }
  
}


##### Implements a spatial prisoner's dilemma game

### set parameters
b <- 100                 # benefit    
c <- 1                  # cost
num_gen <- 1000         # number of generations
initfreq_coop <- 0.5    # initial frequency of cooperators
rho <- c / (b-c)

# calculate the number of competitions
num_comps <- num_gen * numcell

### pay-off matrix, i.e. what player 1 gets when playing against 2:
#
#                               player 2
#                       defect       cooperate
# player   defect          P             T   
#   1      cooperate       S             R   
#
# Prisoner's dilemma (PD): 	( R,  T,  S,  P ) = ( b-c,    b,  -c,   0 )

R <- b-c
T <- b
S <- -c
P <- 0

# calculate the maximum payoff difference, alpha
alpha <-  T-S

# construct payoff matrix
rewards <- matrix(c(P, T, S, R), nrow=2, ncol=2, byrow=TRUE)

### Initialize population and result vectors

# generate initial population matrix (1s are cooperators, 0s are defectors)
landscape <- matrix( data=rbinom(n, 1, initfreq_coop), nrow=sqrt(n), ncol=sqrt(n) )

# Because population size is constant, it will be sufficient to record
# the frequency of just one type (e.g. cooperators)
stats <- numeric(num_comps+1)
stats[1] <- sum(landscape)/n

### Simulate

# loop for value of b
for (b in c(1.01, 1.1, 10, 100)){
# loop for value of theta
  for( theta in c(1.1, 1.5, 2, 8)){
# conduct competitions 
for (i in 1:num_comps+1) { 
  # pick a row for the focal individual
  x_i <- sample(sqrt(n), 1) 
  # pick a column for the focal individual
  x_j <- sample(sqrt(n), 1)
  # pick a neighboring competitor location at random
  competitor <- sample(1:8, 2)
  # compete the pair and calculate payoffs to focal individual
  comp <- competitor[1]
  if (comp == 1){
    # transpose matrix down and right
    mat.alt <- landscape[ c(50, 1:49) , c(50, 1:49)]
    P1 <- rewards[ landscape[x_i, x_j] + 1 , mat.alt[x_i,x_j] + 1 ]
  } else if (comp == 2){
    # transpose matrix down
    mat.alt <- landscape[ c(50, 1:49) , ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i ,x_j ] + 1 ]
  } else if (comp == 3){
    # transpose matrix down and left
    mat.alt <- landscape[ c(50, 1:49) , c(2:50, 1) ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  } else if (comp == 4){
    # transpose matrix right
    mat.alt <- landscape[ , c(50, 1:49)]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  } else if (comp == 5){
    # transpose matrix left
    mat.alt <- landscape[ , c( 2:50, 1) ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  } else if (comp == 6){
    # transpose matrix left and up
    mat.alt <- landscape[ c(2:50, 1), c( 50, 1:49) ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  } else if (comp == 7){
    # transpose matrix up
    mat.alt <- landscape[ c(2:50, 1) , ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  } else if (comp == 8){
    # transpose matrix right and up
    mat.alt <- landscape[ c(2:50, 1), c( 2:50, 1) ]
    P1 <- rewards[ landscape[x_i,x_j ] + 1 , mat.alt[x_i,x_j ] + 1 ]
  }
  
  if (competitor[2] == 1){
    # new focal individual is up and left
    mat.alt1 <- landscape[ c(50, 1:49) , c(50, 1:49)]
  } else if (competitor[2] == 2){
    # new focal individual is up
    mat.alt1 <- landscape[ c(50, 1:49) , ]
  } else if (competitor[2] == 3){
    # new focal individual is up and right
    mat.alt1 <- landscape[ c(50, 1:49) , c(2:50, 1) ]
  } else if (competitor[2] == 4){
    # new focal individual is left
    mat.alt1 <- landscape[ , c(50, 1:49)]
  } else if (competitor[2] == 5){
    # new focal individual is right
    mat.alt1 <- landscape[ , c( 2:50, 1) ]
  } else if (competitor[2] == 6){
    # new focal individual is down and left
    mat.alt1 <- landscape[ c(2:50, 1), c( 50, 1:49) ]
  } else if (competitor[2] == 7){
    # new focal individual is down
    mat.alt1 <- landscape[ c(2:50, 1) , ]
  } else if (competitor[2] == 8){
    # new focal individual is down and right
    mat.alt1 <- landscape[ c(2:50, 1), c( 2:50, 1) ]
  }
  
  # compete second pair and calculate payoffs to focal individual
  competitor2 <- sample(1:8, 1)
  
  if (competitor2 == 1){
    # transpose matrix down and right
    mat.alt2 <- mat.alt1[ c(50, 1:49) , c(50, 1:49)]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 2){
    # transpose matrix down
    mat.alt2 <- mat.alt1[ c(50, 1:49) , ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 3){
    # transpose matrix down and left
    mat.alt2 <- mat.alt1[ c(50, 1:49) , c(2:50, 1) ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 4){
    # transpose matrix right
    mat.alt2 <- mat.alt1[ , c(50, 1:49)]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 5){
    # transpose matrix left
    mat.alt2 <- mat.alt1[ , c( 2:50, 1) ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 6){
    # transpose matrix left and up
    mat.alt2 <- mat.alt1[ c(2:50, 1), c( 50, 1:49) ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 7){
    # transpose matrix up
    mat.alt2 <- mat.alt1[ c(2:50, 1) , ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  } else if (competitor2 == 8){
    # transpose matrix right and up
    mat.alt2 <- mat.alt1[ c(2:50, 1), c( 2:50, 1) ]
    P2 <- rewards[ mat.alt1[x_i,x_j ] + 1 , mat.alt2[x_i,x_j ] + 1 ]
  }
  
  # calculate the probability of replacement 
  w <- max(0,(P2-P1)/alpha)
  
  # now replace the first organism, if necessary
  if (w > runif(1)) { landscape[x_i,x_j ] <- mat.alt1[x_i,x_j] }
  
  # record the frequency of cooperators
  stats[i] <- sum(landscape)/n
}

#############################################################
# Implements conformist learning of land ethic
#############################################################

### set parameters
theta <- 8              # strength of conformist bias
initfreq_landethic <- 0.5    # initial frequency of land ethic

### conformist transmission of land ethic

### Initialize population and result vectors

# distribute initial land ethic randomly
pop$ethic <- rbinom( 2500, 1, 0.5) # requires "pop" from network.algorithm

# Because population size is constant, it will be sufficient to record
# the frequency of just one type (e.g. cooperators)
stats.LE <- numeric(num_comps)
stats.LE[1] <- sum(pop$ethic)/n

for (i in 1:num_comps){
  
  
  # pick a  focal individual
  x <- sample(n, 1) 
  
  # update their ethic probabilistically as a function of their neighbors and the majority
  p_0 <- 1 - ( sum(pop$ethic[ which( adj_mat[x,] == 1)]) / length(pop$ethic[ which( adj_mat[x,] == 1)]) )
  p_1 <- sum(pop$ethic[ which( adj_mat[x,] == 1)]) / length(pop$ethic[ which( adj_mat[x,] == 1)])
  
  # calculate the probability of replacement 
  prob_adopt <- p_0^theta / (p_0^theta + p_1^theta)
  
  # now replace the first organism, if necessary
  pop$ethic[x] <- ifelse( runif(1) < prob_adopt, 0, 1 )
  
  # record the frequency of land ethic
  stats.LE[i] <- sum(pop$ethic)/n
  
}

### Plot proportion of cooperators in the population

# use time scale of competition interactions
time <- 1:num_comps
plot(time,stats, type="l",lwd=2, xlab="time (number of competitions)",ylab="Frequency of cooperators")

### Plot proportion of land ethic in the population

# use time scale of competition interactions
time <- 1:num_comps
plot(time,stats.LE, type="l",lwd=2, xlab="time (number of competitions)",ylab="Frequency of land ethic")

  }
  
}