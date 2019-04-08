#!/usr/bin/env Rscript
# Plot a minimum spanning tree from SRST2 MLST output

# TODO: Create new STs for each unique 'not found'/ unclass
# TODO: scale edges by distance


### Init
library(ape)
library(igraph)


### Data
d.mlst <- read.table(url('https://stephen.ac/mlst_data.tsv'), header=TRUE)


### Process
## Create data.frame with only allele information for each sample
# Count number of unique STs (excluding 'not founds')
st_names <- as.character(unique(d.mlst$ST[!grepl('NF', d.mlst$ST)]))
st_freq <- sapply(st_names, function(st) { sum(d.mlst$ST==st) })
names(st_freq) <- st_names

# Create data.frame with allele info
d.st_alleles <- d.mlst[NULL,3:9]
for (st in st_names) {
  d.st_alleles <- rbind(d.st_alleles, d.mlst[match(st, d.mlst$ST),3:9])
}

## Count the number of differences and create dist object
d.mlst.distances <- matrix(0, ncol=nrow(d.st_alleles), nrow=nrow(d.st_alleles))
for (i in 1:(nrow(d.st_alleles)-1)) {
  for (j in (i+1):nrow(d.st_alleles)){
    d.mlst.distances[i,j] <- d.mlst.distances[j,i] <- sum(d.st_alleles[i, ] != d.st_alleles[j, ])
  }
}
d.mlst.distances.euclidean <- dist(d.mlst.distances)


### Plotting
# Create minimum spanning tree and convert to igraph object
d.mst <- ape::mst(d.mlst.distances.euclidean)
g.mst <- graph_from_adjacency_matrix(d.mst, mode=c('undirected'))

# Set vertex size to ST frequency
V(g.mst)$size <- round( 10 * (st_freq / max(st_freq)) ) + 1
V(g.mst)$label <- st_names

# Render graph
plot(g.mst, edge.arrow.size=0.5, vertex.color='gold',
     vertex.frame.color='gray', vertex.label.color='black',
     vertex.label.cex=0.8)
