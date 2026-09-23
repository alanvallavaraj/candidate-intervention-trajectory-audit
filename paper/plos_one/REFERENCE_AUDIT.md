# Reference check for the PLOS ONE draft

The manuscript cites 43 distinct entries in order of first appearance. The attached `plos2025.bst` prints Vancouver-style numbered references with up to six authors before *et al.* Four arXiv records are presented as preprints, with their intact dotted identifiers in the rendered PDF and working arXiv URLs.

The audit compared titles and available metadata with publisher records, authors' institutional pages, the COCO project citation, and the arXiv abstract pages. Particularly important corrections made in this revision:

| Entry | Correction | Source |
|---|---|---|
| `jones1998ego` | Added volume 13(4), pp. 455–492 and DOI. | [Springer](https://link.springer.com/article/10.1023/A%3A1008306431147) |
| `hansen2020coco` | Corrected the **printed** publication year to 2021; added volume 36(1), pp. 114–144 and DOI. The BibTeX key is retained to avoid breaking citations. | [COCO official citation](https://coco-platform.org/) |
| `hansen2009bbob` | Replaced a general BBOB overview link with the cited INRIA research report record. | [HAL/INRIA](https://hal.science/inria-00362633) |
| `luo2019`, `wang2020forest`, `jin2011survey`, `lu2011`, `cai2020`, `pan2019`, `beaucaire2019`, `blank2020pymoo`, `storn1997`, `li2021`, `lv2019`, `zhou2007`, `tian2017` | Added checked DOI identifiers to the existing titles, authors and journal/conference metadata. | Publisher records linked by DOI in `references.bib` |
| `gpsaf2022`, `hansen2011inject`, `siper2026`, `yu2026janus` | Moved the dotted arXiv identifier into a separate bibliography note because the supplied PLOS style removes periods from numerals embedded in a journal name. | The four `arxiv.org/abs/` links in `references.bib` |

The bibliography contains source metadata for the cited works, but this is not a retraction or correction-status service. Check for new corrections, retractions, or later journal versions immediately before submission. The original LaTeX paper bibliography has also received the publisher-backed metadata corrections.
