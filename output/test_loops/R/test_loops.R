# test_loops - Generated from RPX

#' Test Nested Loops
#'
#' Function generated from RPX source code.
#'

#' @return integer value
#' @export
test_nested_loops <- function() {
  total <- 0
  for (i in 1:3) {
    for (j in 1:2) {
      total <- ((total + i) + j)
    }
  }
  return(total)
}

