SRAdownload
===========
Install it via PIP

::

  pip install --upgrade SRAdownload


Usage: SRAdownload [OPTIONS] [RUN]...

  A simple tool that downloads SRA short reads by their accessions (RUN)
  from either NCBI or EBI and converts them into fastq.gz files. Version 1.0

  Try it with "SRAdownload SRR2223576 SRR2223582"

Options:
  -f, --folder TEXT  Root folder for fetched short reads. Each SRA record will
                     be saved in a sub-folder. DEFAULT: current folder

  -s, --source TEXT  Sources for reads, change to EBI,NCBI if your connection
                     to EBI is faster. DEFAULT: NCBI,EBI

  -h, --help         Show this message and exit.
