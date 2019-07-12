#!/usr/bin/env Rscript
# There are several useful snippets here but overall this is a complicated script and important parts need to be distilled
#   * timelines with ggplot - dodging elements
#   * fine grain control over ggplot rendering
#   * accessing and exploiting ggplot data to programmatically place new elements
#   * pie charts in ggplot placed onto plot with unfixed coordinates (i.e. not 1:1)


# TODO: add snp distances

### Init, opts and libraries
setwd('~/writing/haemophilus_clinical/analysis/11_tranmission_carriage/')

require(ggplot2)
require(reshape2)
require(ggpubr)

.Options$species_colours <- c('Haemophilus influenzae'='#000000', 'Haemophilus parainfluenzae'='#ffffff', 'None'='#a0a0a0')
.Options$amr_colours <- c('Ampicillin_Intermediate'='#efd490',
                          'Augmentin_Intermediate'='#efd491',
                          'Cefotaxime_Intermediate'='#efd492',
                          'Cotrimoxazole_Intermediate'='#efd493',
                          'Rifampicin_Intermediate'='#efd494',

                          'Ampicillin_None'='#bababa',
                          'Augmentin_None'='#bababb',
                          'Cefotaxime_None'='#bababc',
                          'Cotrimoxazole_None'='#bababd',
                          'Rifampicin_None'='#bababe',

                          'Ampicillin_Resistant'='#ed9680',
                          'Augmentin_Resistant'='#ed9681',
                          'Cefotaxime_Resistant'='#ed9682',
                          'Cotrimoxazole_Resistant'='#ed9683',
                          'Rifampicin_Resistant'='#ed9684',

                          'Ampicillin_Sensitive'='#fffffb',
                          'Augmentin_Sensitive'='#fffffc',
                          'Cefotaxime_Sensitive'='#fffffd',
                          'Cotrimoxazole_Sensitive'='#fffffe',
                          'Rifampicin_Sensitive'='#ffffff')
.Options$amr_colours_legend <- c('Resistant'='#ed9682',
                                 'Intermediate'='#efd492',
                                 'None'='#bababc',
                                 'Sensitive'='#ffffff00')
.Options$min_days <- 25
.Options$point_size <- 5
.Options$timeline_offset <- 0.35
.Options$dodge_width <- 0.5
.Options$dodge_position_offset <- 0.1
.Options$pie_radius <- 17.5
.Options$scale_mod <- 1.2
.Options$base_plot_height <- 0.75


### Data
d.info <- read.table('../../sample_data/general/combined_data.tsv', header=TRUE, sep='\t', stringsAsFactors=FALSE)
d.pheno <- read.table('../../sample_data/general/amr_phenotypes.tsv', header=TRUE, sep='\t', stringsAsFactors=FALSE)
# Clusters
read_clusters <- function(fp) {
  con <- file(fp, 'r')
  lines <- readLines(con)
  close(con)
  strsplit(lines, '\t')
}
d.clusters.hi.fp <- '../../analysis/influenzae/transmission_carriage/1_defined_clusters/hi_clusters.txt'
d.clusters.hpi.fp <- '../../analysis/parainfluenzae/transmission_carriage/1_defined_clusters/hpi_clusters.txt'
d.clusters.hi <- read_clusters(d.clusters.hi.fp)
d.clusters.hpi <- read_clusters(d.clusters.hpi.fp)

# Visitation
d.visits <- read_ods('../../sample_data/general/haemophilus_patient_visitation.ods', sheet='long_format')
# Set admission and discharge to dates
d.visits$admission <- as.Date(d.visits$admission, format='%d/%m/%Y')
d.visits$discharge <- as.Date(d.visits$discharge, format='%d/%m/%Y')
# For now remove entries with no admission date
d.visits <- d.visits[!is.na(d.visits$admission), ]
# For visits without discharge (outpatient) set to same day
v.no_discharge <- is.na(d.visits$discharge)
d.visits$discharge[v.no_discharge] <- d.visits$admission[v.no_discharge] + 0.99
# Remove dates that fall outside of study
d.visits <- d.visits[d.visits$admission < "2017-02-23", ]

### Processing
# Set age and date to appropriate types
d.info$pariticpant_age <- as.numeric(d.info$pariticpant_age)
d.info$collection_date <- as.Date(d.info$collection_date, format='%d/%m/%Y')

# Sort clusters by patient number
d.pn.hi <- sapply(d.clusters.hi, function(c) { p <- unique(sub('_[0-9]+$', '', c)); length(p) })
d.pn.hpi <- sapply(d.clusters.hpi, function(c) { p <- unique(sub('_[0-9]+$', '', c)); length(p) })

d.clusters.hi <- d.clusters.hi[sort(d.pn.hi, index.return=TRUE)$ix]
d.clusters.hpi <- d.clusters.hpi[sort(d.pn.hpi, index.return=TRUE)$ix]

# Set all Unknown to None
d.pheno[ ,-1][d.pheno[ ,-1] == 'Unknown'] <- 'None'

# Convert pheno data for pie
d.pheno.pie <- data.frame(sample=d.pheno$sample)
l.cats <- c('Sensitive', 'None', 'Resistant', 'Intermediate')
namr <- length(d.pheno) -1
nsam <- length(d.pheno[ ,1])
ncat <- length(l.cats)
for (amr in colnames(d.pheno[ ,-1])) {
  d <- matrix(0, nsam, ncol=ncat, dimnames=list(NULL, l.cats))
  for (i in 1:nsam) {
    v <- d.pheno[i,amr]
    d[i,v] <- 1/namr
  }
  colnames(d) <- paste0(amr, '_', l.cats)
  d.pheno.pie <- cbind(d.pheno.pie, as.data.frame(d))
}
d.pheno.pie$x <- d.pheno.pie$y <- Inf


### Plot
create_timeline_plot <- function(samples) {
  # Get data
  patients <- unique(sub('_[0-9]$', '', samples))
  d.cluster <- d.info[d.info$participant %in% patients,c('participant', 'sample_number', 'filename', 'pariticpant_age', 'collection_date', 'species_genotyped')]

  # Create base plot for each patient - allow us to offset in-cluster and out-cluster points
  d.dummy <- data.frame(participant=patients, collection_date=as.Date('2016-01-01'))
  l.dummy <- geom_point(data=d.dummy, alpha=0, aes(x=participant, y=collection_date, participant=participant))
  g <- ggplot() + l.dummy
  g.built <- ggplot_build(g)
  d.graph_base <- g.built$data[[1]]

  # Place all in-cluster samples above the line and out-cluster below
  d.cluster$xbase <- d.graph_base$x[match(d.cluster$participant, d.graph_base$participant)]
  d.cluster$x <- ifelse(d.cluster$filename %in% samples, d.cluster$xbase+.Options$timeline_offset, d.cluster$xbase-.Options$timeline_offset)

  # Divide cluster data into overlapping and non-overlapping points
  d.splits.parts <- lapply(patients, function(p) {
    d <- d.cluster[d.cluster$participant==p, ]
    l.ov <- list()
    d.nov <- d[NULL, ]
    # Find overlaps within above and below points
    d.a <- d[d$x > d$xbase, ]
    d.b <- d[d$x < d$xbase, ]
    if (dim(d.a)[2]) {
      r <- split_overlaps(d.a)
      d.nov <- rbind(d.nov, r$nov)
      l.ov <- c(l.ov, r$ov)
    }
    if (dim(d.b)[2]) {
      r <- split_overlaps(d.b)
      d.nov <- rbind(d.nov, r$nov)
      l.ov <- c(l.ov, r$ov)
    }
    list(ov=l.ov, nov=d.nov)
  })

  # Create final list and data.frame for data split
  d.splits <- list()
  d.splits$nov <- do.call('rbind', lapply(d.splits.parts, function(sp) { sp$nov }))
  # Must be done in nested for loop
  d.splits$ov <- list()
  for (part in d.splits.parts) {
    for (ov in part$ov) {
      d.splits$ov[[length(d.splits$ov)+1]] <- ov
    }
  }

  # Create layers for isolate geom_point
  timeline_aes <- aes(x=x, y=collection_date, fill=species_genotyped, participant=filename)
  l.points <- NULL
  l <- geom_point(data=d.splits$nov, timeline_aes, shape=21, size=.Options$point_size, colour='black')
  l.points <- c(l.points, l)
  for (d.ov in d.splits$ov) {
    # Increase vertical position to offset dodge shapes from timeline
    if (all(d.ov$x > d.ov$xbase)) {
      d.ov$x <- d.ov$x + .Options$dodge_position_offset
    } else {
      d.ov$x <- d.ov$x - .Options$dodge_position_offset
    }
    l <- geom_point(data=d.ov, timeline_aes, shape=21, position=position_dodge(width=.Options$dodge_width), size=.Options$point_size, colour='black')
    l.points <- c(l.points, l)
  }

  # Build next plot iteration which now contains isolate points and annotate timelines with segments and pies
  g <- base_plot() + l.dummy + l.points
  g.built <- ggplot_build(g)
  d.graph_noanno <- do.call('rbind', lapply(g.built$data[-1], function(d) { d[ ,c('participant', 'x', 'y')] }))

  # Get layers for pie charts
  g.pies <- get_pie_charts(d.cluster$filename, d.graph_noanno)
  
  # Get horizontal line segments - estimate birthdate
  d.segments.parts <- lapply(patients, function(p) {
    d <- d.cluster[d.cluster$participant==p, ]
    bds <- round(d$collection_date - d$pariticpant_age * 365, 1)
    bd <- mean(bds)
    y1 <- max(as.Date('2016-01-01'), as.Date(bd, origin='1970-01-01'))
    y2 <- as.Date('2017-03-01')
    x1 <- x2 <- d.graph_base$x[d.graph_base$participant==p]
    data.frame(x1=x1, y1=y1, x2=x2, y2=y2)
  })
  d.segments_horizontal <- do.call('rbind', d.segments.parts)
  l.segments_horizontal <- geom_segment(aes(x=x1, y=y1, xend=x2, yend=y2), data=d.segments_horizontal, colour='#444444')
  
  # Get veritcal line segments
  x.src <- d.graph_base$x[match(sub('_[0-9]+', '', d.graph_noanno$participant), d.graph_base$participant)]
  y <- as.Date(d.graph_noanno$y, origin='1970-01-01')
  d.segments_vertical <- data.frame(x1=x.src, y1=y, x2=d.graph_noanno$x, y2=y)
  l.segments_vertical <- geom_segment(aes(x=x1, y=y1, xend=x2, yend=y2), data=d.segments_vertical, colour='#444444')
  
  # Get contact segments, if applicable
  l.contact <- get_contact_segments(patients)
  
  # Generate plot
  g <- base_plot() + l.dummy + l.segments_horizontal + l.contact + l.segments_vertical + g.pies + l.points
}

split_overlaps <- function(d) {
  ov <- lapply(1:(length(d[ ,1]) - 1), function(i) { d$collection_date[i+1] - d$collection_date[i] })
  n <- which(ov < .Options$min_days)
  gs <- list()
  l <- -Inf
  for (i in n) {
    if (i - l == 1) {
      gs[[length(gs)]] <- c(gs[[length(gs)]], i)
    } else {
      gs[[length(gs)+1]] <- i
    }
    l <- i
  }

  gd <- lapply(gs, function(g) { d[c(g, g+1), ] })
  v <- rep(TRUE, length(d[ ,1]))
  v[c(n, n+1)] <- FALSE
  list(ov=gd, nov=d[v, ])
}

get_pie_charts <- function(samples, d.graph) {
  # Create grobs for each pie char
  d.pie <- d.pheno.pie[d.pheno.pie$sample %in% samples, ]
  g.pies <- lapply(1:length(d.pie[ ,1]), function(i) {
    # Get appropriate data
    d <- d.pie[i,!colnames(d.pie) %in% c('sample', 'x', 'y')]
    d <- melt(d, id.vars=NULL, variable.name='status')
    d <- d[d$value > 0, ]
    # Add value to set alpha on - such that only resistance/intermediate is shown
    d$alpha <- ifelse(grepl('Resistant|Intermediate|None', d$status), 1, 0)
    # Create plot
    g <- ggplot(d, aes(x=1, y=value, fill=status, alpha=alpha)) + geom_col(color='#FFFFFF', size=0.25, show.legend=FALSE)
    g <- g + coord_polar(theta='y') + theme_void()
    g <- g + scale_fill_manual(values=.Options$amr_colours)
    g <- g + scale_alpha_identity()
    g  })
  names(g.pies) <- d.pie$sample

  # Convert grob into a custom annotation
  lapply(names(g.pies), function(n) {
    g <- g.pies[[n]]
    dd <- d.graph[d.graph$participant==n, ]
    annotation_custom(grob=ggplotGrob(g),
                      xmin=dd$x-.Options$pie_radius,
                      xmax=dd$x+.Options$pie_radius,
                      ymin=dd$y-.Options$pie_radius,
                      ymax=dd$y+.Options$pie_radius)
  })
}

base_plot <- function() {
  g <- ggplot() + coord_flip()
  g <- g + scale_fill_manual(values=.Options$species_colours, guide=guide_legend(override.aes=list(shape=22)))
  g <- g + scale_y_date(date_breaks='1 month', date_labels='%b %Y', limits=as.Date(c('2016-01-01', '2017-03-01')))
  g <- g + scale_x_discrete(expand=c(0, 1.2))
  g <- g + theme_void()
  g + theme(legend.position='None',
            axis.title=NULL,
            axis.text=NULL,
            axis.title.x=element_blank(),
            panel.grid.major.y=element_line(colour='#CCCCCC'),
            panel.grid.major.x=element_line(colour='#F7F7F7'),
            axis.text.x=element_blank(),
            axis.text.y=element_text(margin=margin(r=0.8*2.2/2), hjust=1),
            axis.text.y.right=element_text(margin=margin(l=0.8*2.2/2), hjust=0),
            # margin param here adjust cluster title
            axis.title.y=element_text(angle=90, margin=margin(r=2.2/2)*10, vjust=1))
}

get_contact_segments <- function(patients) {
  if (length(unique(patients)) > 1) {
    d <- d.visits[d.visits$patient %in% patients, ]
    d1 <- d$admission[d$patient==patients[1]]
    d2 <- d$admission[d$patient==patients[2]]
    
    c <- lapply(d1, function(v) {
      abs(d2 - v)
    })
    
    d.diff <- as.data.frame(c)
    d.enc <- data.frame(xs=NULL, xe=NULL, ys=NULL, ye=NULL)
    for (j in 1:ncol(d.diff)) {
      for (i in 1:nrow(d.diff)) {
        if (d.diff[i,j] <= 0) {
          ww <- d.diff[i,j]
          d.enc_row <- data.frame(xs=d1[j], xe=d2[i], ys=1, ye=2)
          d.enc <- rbind(d.enc, d.enc_row)
        }
      }
    }
    if (length(d.enc) > 0) {
      l.contact <- geom_curve(data=d.enc, aes(x=ys, xend=ye, y=xs, yend=xe), colour='#abdda4', curvature=-0.25, size=2)
      return(l.contact)
    }
  }
  return(NULL)
}

timeline_legend <- function() {
  d.categories <- c('Haemophilus influenzae', 'Haemophilus parainfluenzae', 'None')
  d <- data.frame(participant=1, collection_date=1, species_genotyped=d.categories, sample_number=1)
  timeline_aes <- aes(x=participant, y=collection_date, fill=species_genotyped, group=sample_number)
  g <- ggplot(d) + geom_point(timeline_aes, size=.Options$point_size, shape=21, colour='black')
  g <- g + scale_fill_manual(values=.Options$species_colours, guide=guide_legend(override.aes=list(shape=22)))
  g <- g + labs(fill='Genotyped species')
  get_legend(g)
}

amr_legend <- function() {
  f <- factor(names(.Options$amr_colours_legend), levels=c('Resistant', 'Intermediate', 'Sensitive', 'None'))
  d <- data.frame(x=1:4, y=1:4, v=f)
  g <- ggplot(d) + geom_point(aes(x=x, y=y, fill=v))
  g <- g + scale_fill_manual(values=.Options$amr_colours_legend, guide=guide_legend(override.aes=list(shape=22)))
  g <- g + labs(fill='AMR Phenotype')
  get_legend(g)
}

# Get plots for timelines
d.plots.hi <- lapply(1:length(d.clusters.hi), function(i) {
  cluster <- d.clusters.hi[[i]]
  create_timeline_plot(cluster) + xlab(paste0('Hi g', i))
})
d.plots.hpi <- lapply(1:length(d.clusters.hpi), function(i) {
  cluster <- d.clusters.hpi[[i]]
  create_timeline_plot(cluster) + xlab(paste0('Hpi g', i))
})
d.plots <- c(d.plots.hi, d.plots.hpi)

# Get heights
heights <- sapply(c(d.clusters.hi, d.clusters.hpi), function(s) {
  p <- unique(sub('_[0-9]+$', '', s))
  pn <- length(p)
  h <- .Options$base_plot_height * (pn + .Options$scale_mod)
})

# Set borders
get_border <- function(position, size=1, linetype=1) {
  if (position == 'top') {
    x <- y <- Inf
  } else if (position == 'bottom') {
    x <- y <- -Inf
  } else {
    stop('got bad position')
  }
  annotate(geom='segment', x=x, xend=y, y=as.Date('2016-01-01'), yend=as.Date('2017-03-01'), size=size, linetype=linetype)
}

for (i in 1:length(d.plots)) {
  if (i == 1) {
    d.plots[[i]] <- d.plots[[i]] + get_border('top', size=3)
  }
  if (i == length(d.clusters.hi)) {
    d.plots[[i]] <- d.plots[[i]] + get_border('bottom', size=3)
  } else if (i == length(d.plots)) {
    d.plots[[i]] <- d.plots[[i]] + get_border('bottom', size=3)
  } else {
    d.plots[[i]] <- d.plots[[i]] + get_border('bottom', linetype=2)
  }
}

# Get plot of only x-axis ticks
p.ticks <- theme(axis.ticks=element_line(colour='grey20'),
                 axis.ticks.length=unit(2.2/2, 'pt'),
                 axis.text.x=element_text(angle=45, hjust=1, vjust=1))
g.ticks <- base_plot() + p.ticks + geom_blank()

# Create timeline plots
d.plots[[length(d.plots)+1]] <- g.ticks
g.timelines <- ggarrange(plotlist=d.plots, ncol=1, nrow=length(d.plots), heights=heights, align='v')

# Create legend plot
l.legends <- list(timeline_legend(), amr_legend(), ggplot() + theme_void())
g.legends <- ggarrange(plotlist=l.legends, nrow=3, ncol=1, heights=c(1,1,8))

# Render
svg('timeline_raw.svg', height=30, width=8)
{
  ggarrange(g.timelines, g.legends, nrow=1, ncol=2, widths=c(1, 0.3))
}
dev.off()
