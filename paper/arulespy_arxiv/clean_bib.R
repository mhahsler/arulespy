library(stringr)

clean_bib <- function(input_file, input_bib, output_bib){
  lines <- paste(readLines(input_file), collapse = "")
  
  entries <- unique(str_match_all(lines, "@([a-zA-Z0-9\\:\\+]+)[, \\?\\!\\]\\;]")[[1]][, 2])
  
  cat("Found:", entries)
  
  bib <- paste(readLines(input_bib), collapse = "\n")
  bib <- unlist(strsplit(bib, "\n@"))
  
  output <- sapply(entries, grep, bib, fixed = TRUE, value = T)
  output <- paste("@", output, sep = "")
  
  writeLines(unlist(output), output_bib)
}

clean_bib("paper.Rmd", "paper.bib", "used.bib")