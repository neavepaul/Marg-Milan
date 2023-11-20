## Mods

-   ### Editable Pdf

    -   less paper use
    -   less paper record
    -   less computation as document quality ensured
    -   easy to maintain and store digitally

-   ### Argument against current handwritten and scanned
    -   the document quality is checked by the api (1st level of computation)
    -   if the document is found to be poor then it has to be rescanned (2nd level) and then the quality is checked again (...nth level)
    -   the rescanning and uploading of documents may not be feasible in many cases as the pdfs are upto 200 pages long in some cases
    -   _with the editable pdf this problem is offsetted as we standardise the document format and remove the unneccessary handwritting hurdle_
    -   although handwritting ocr is a fairly established technology. given our tabular format and extraction needs (to be extracted as a dataframe for the sql database) it makes it computationally intentive as we must make multiple calls to the handwritten-ocr module.
        -   if we send the table to the module as is the table borders will add noise to the output.
        -   one way to offfset the noise is to send each cell to the module individually if handwritten text is found in it. this also is not feasible given the size of the tables
