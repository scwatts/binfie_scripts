#!/usr/bin/env Rscript

# This script demonstrates a number of useful things:
#   1. I scale the x-axis of ggtree plots such that you placement of tip labels is done in a consistent
#   manner, even when the branch lengths vary greatly among tree sets
#   2. I also use scaling of the y-axis with log10(v + 1) in a ggplot2 histogram with stacked bars. This
#   requires that you set geom position to identity and provide a transform function to scale_y_continuous
#   3. Lastly I use hashes to identify duplicated rows in a data frame where I considered a row to be
#   duplicated if it shared the same data as another row, disregarding the exact order of data

### Libraries
require(ape)
require(reshape2)
require(ggplot2)
require(ggtree)
require(digest)
require(phangorn)
require(ggpubr)
require(scales)


### Init and opts
set.seed(0)
.Options$tips <- 100
.Options$subtree_tips <- 6
options(stringsAsFactors=FALSE)


### Data
# Tree
d.tree <- rcoal(.Options$tips)

# Distances
m.dists <- cophenetic.phylo(d.tree)
d.dists <- melt(m.dists, varnames=c('tip1', 'tip2'), value.name='dist')
d.dists[ ,1:2] <- lapply(d.dists[ ,1:2], as.character)


### Processing
## Use only upper triangle of d.dists - find row duplicates using sha1 digest of sorted row data
v.sha1 <- apply(d.dists, 1, function(r) { d <- as.character(sort(r)); digest(d) })
v.diag <- d.dists[ ,1] == d.dists[ ,2]
d.dists <- d.dists[!(duplicated(v.sha1) | v.diag), ]

## Find cluster with smallest distance with at least n elements
# Cluster and iterate merge heights, finding the max cluster size at each height
d.clust <- hclust(as.dist(m.dists))
v.sizes <- lapply(d.clust$height, function(h) { max(table(cutree(d.clust, h=h))) })
# Select appropriate height
i.height_index <- min(which(v.sizes >= .Options$subtree_tips))
f.height <- d.clust$height[i.height_index]

# Collect desired cluster
d.members <- cutree(d.clust, h=f.height)
d.members.size <- table(d.members)
s.cluster <- names(d.members.size[d.members.size >= .Options$subtree_tips])
v.cluster_tips <- names(d.members)[d.members==s.cluster]

### Create data set for two cluster sets - one very closely related and the other with a distance tip
d.small <- d.large <- list()

## Store selected tips
d.small$selected_tips <- v.cluster_tips

# Add the most distance tip to cluster
d.dists.neigh <- d.dists[d.dists$tip1 %in% v.cluster_tips | d.dists$tip2 %in% v.cluster_tips, ]
v.most_dist_tips <- d.dists.neigh[which.max(d.dists.neigh$dist),1:2]
s.new_tip <- v.most_dist_tips[!v.most_dist_tips %in% v.cluster_tips]
d.large$selected_tips <- c(v.cluster_tips, as.character(s.new_tip))

## Set distances of selected tips
d.small$dists <- d.large$dists <- d.dists
v.seldist.small <- apply(d.dists, 1, function(r) { all(r[1:2] %in% d.small$selected_tips) })
v.seldist.large <- apply(d.dists, 1, function(r) { all(r[1:2] %in% d.large$selected_tips) })
d.small$dists$tree <- ifelse(v.seldist.small, 'subtree', 'fulltree')
d.large$dists$tree <- ifelse(v.seldist.large, 'subtree', 'fulltree')

## Generate tree data
d.tree_data <- data.frame(run=d.tree$tip.label, subtree=NA, read_count=round(rnorm(.Options$tips, mean=2e5, sd=1e4)))
d.small$tree_data <- d.large$tree_data <- d.tree_data
d.small$tree_data$subtree <- ifelse(d.tree$tip.label %in% d.small$selected_tips, 'yes', 'no')
d.large$tree_data$subtree <- ifelse(d.tree$tip.label %in% d.large$selected_tips, 'yes', 'no')


### Plot
# Create transform for log10(v + 1)
log10p_trans <- trans_new('log10p', function(v) { log10(v+1) }, function(v) { 10^v - 1 })

# Plot function
generate_plot <- function(data) {
  # Distribution of distances
  g.hist <- ggplot(data$dists, aes(x=dist, fill=tree)) + geom_histogram(position='identity', colour='#3f3f3f', bins=20)
  g.hist <- g.hist + scale_fill_manual(values=c('#9bc1bc', '#ead2ac')) + labs(x='distance', y='count')
  g.hist <- g.hist + scale_y_continuous(trans=log10p_trans)

  # Tree
  g.tree <- ggtree(midpoint(d.tree))
  g.tree <- g.tree %<+% data$tree_data + geom_tippoint(aes(subset=(node %in% which(d.tree$tip.label %in% data$selected_tips)), color=subtree))

  # Subtree
  d.subtree <- drop.tip(d.tree, which(!d.tree$tip.label %in% data$selected_tips))
  g.subtree <- ggtree(d.subtree) + geom_treescale()
  # Scale the x-axis such that the tree always has sufficient space for labels
  g.subtree <- g.subtree + xlim(0, max(g.subtree$data$x) * 1.50)
  g.subtree <- g.subtree %<+% data$tree_data + geom_tiplab(align=TRUE) +
    # Scale position of labels with tree branch length/x-axis
    geom_tiplab(align=TRUE, linetype=NULL, offset=max(g.subtree$data$x)/4, aes(label=read_count))


  # Plot
  ggarrange(plotlist=list(g.tree, g.subtree, g.hist), ncol=3, nrow=1, widths=c(2,3,2))
}

# Create plots
generate_plot(d.small)
generate_plot(d.large)
