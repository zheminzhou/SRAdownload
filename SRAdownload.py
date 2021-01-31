#!/usr/bin/env python 
import os, sys, traceback, click, subprocess, shutil, json, time
from glob import glob
try :
    from urllib.request import urlretrieve, urlopen
except :
    from urllib import urlretrieve
    from urllib2 import urlopen

home_dir = os.path.dirname(os.path.realpath(__file__))
fasterq_dump = os.path.join(home_dir, 'sratoolkit.2.9.6-1-ubuntu64/bin/fasterq-dump')
fasterq_cmd = '{fasterq_dump} {acc} -f --split-3 -O {route}'
prefetch = os.path.join(home_dir, 'sratoolkit.2.9.6-1-ubuntu64/bin/prefetch')
prefetch_cmd = '{prefetch} -s {acc}'
ebi_webpage = 'http://www.ebi.ac.uk/ena/data/warehouse/filereport?accession={acc}&result=read_run&fields=base_count,fastq_ftp,submitted_ftp'

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('run', nargs=-1)
@click.option('-f', '--folder', help='Root folder for fetched short reads. Each SRA record will be saved in a sub-folder. DEFAULT: current folder', default='.')
@click.option('-s', '--source', help='Sources for reads, change to EBI,NCBI if your connection to EBI is faster. DEFAULT: NCBI,EBI', default='NCBI,EBI')
@click.option('-m', '--maximum', help='maximum size of the SRA to be download. DEFAULT: no limit', default=None, type=int)
def main(run, folder, source, maximum) :
    '''A simple tool that downloads SRA short reads by their accessions (RUN) from either NCBI or EBI and converts them into fastq.gz files.
Version 1.6

Try it with "SRAdownload SRR2223576 SRR2223582"'''
    sources = source.split(',')
    reads = {}
    for r in run :
        reads[r] = save_read(r, folder, sources, maximum)
    sys.stdout.write(json.dumps(reads, indent=2, sort_keys=True)+'\n')
    return reads

def download_file(url, fname) :
    for i in range(3) :
        try :
            return urlretrieve(url, fname)[0]
        except :
            time.sleep(5)


def get_sratoolkit() :
    try :
        p = subprocess.Popen(fasterq_dump, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
        assert p.returncode == 0, ''
    except Exception as e:
        sys.stderr.write('sratoolkit.2.9.6-1 is required for the module. Downloading from the NCBI website...\n')
        url = 'https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.9.6-1/sratoolkit.2.9.6-1-ubuntu64.tar.gz'
        tar_file = os.path.join(home_dir, 'sratoolkit.2.9.6-1-ubuntu64.tar.gz')
        download_file(url, tar_file)
        subprocess.Popen('tar -vxzf {0}'.format(tar_file).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=home_dir).communicate()
        p = subprocess.Popen(fasterq_dump, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
        assert p.returncode == 0, ''
        sys.stderr.write('sratoolkit.2.9.6-1 has been downloaded. You will not see this the next time.\n')
    return

def save_read(run_accession, folder, sources, maximum_size=None) :
    route = os.path.join(folder, run_accession)
    try:
        os.makedirs(route)
    except Exception as e:
        pass

    for source in sources:
        if source.upper() in ('NCBI', 'SRA', 'GENBANK') :
            get_sratoolkit()
            try :
                cmd = prefetch_cmd.format(prefetch=prefetch, acc = run_accession)
                output = subprocess.Popen(cmd.split(), cwd=route, stdout=subprocess.PIPE).communicate()
                n_base = sum([ int(line.strip().split('\t')[2][:-1].replace(',', '')) for line in output[0].split('\n') if len(line) > 1])
                if maximum_size and n_base > maximum_size :
                    sys.stderr.write('SRA file for {0} is too large. Give up\n'.format(run_accession))
                    continue
                sys.stderr.write('Downloading {0} from NCBI using sratoolkit...\n'.format(run_accession))
                cmd = fasterq_cmd.format(fasterq_dump=fasterq_dump, \
                                                     acc = run_accession, route='.')

                subprocess.Popen(cmd.split(), cwd=route, \
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            except Exception as e:
                traceback.print_exc()
                continue
            finally :
                for fname in glob(os.path.join(os.path.expanduser("~"), \
                                               'ncbi/public/sra/{acc}.sra*'.format(acc=run_accession))) :
                    try:
                        os.unlink(fname)
                    except Exception as e:
                        pass
                for dname in glob(os.path.join(route, 'fasterq.tmp*')) :
                    try :
                        shutil.rmtree(dname)
                    except Exception as e:
                        pass
            
            files = glob(os.path.join(route, '{acc}*.fastq'.format(acc=run_accession)))
            if len(files) :
                try :
                    subprocess.Popen(['pigz', '-f'] + files ).wait()
                except Exception as e:
                    subprocess.Popen(['gzip', '-f'] + files ).wait()

            files = glob( os.path.join( route, '{acc}*.fastq*'.format(acc = run_accession) ) )
            if len(files) == 0 :
                continue
            return sorted(files, key=lambda x:(-len(x), x))
        elif source.upper() in ('EBI', 'ENA') :
            try :
                sys.stderr.write('Downloading {0} from EBI ftp site...\n'.format(run_accession))
                fstring = urlopen(ebi_webpage.format(acc=run_accession), timeout=30).read()
                fstring = fstring.decode().split('\n')[1].strip().split('\t')
                if len(fstring) == 1 : continue
                try :
                    n_base = int(fstring[1])
                except :
                    n_base = 0
                if (maximum_size and n_base > maximum_size) or n_base == 0 :
                    sys.stderr.write('Files for {0} are too large. Give up\n'.format(run_accession))
                    continue
                if len(fstring[1]) and ( fstring[1].lower().find('fastq.gz') >= 0 or  fstring[1].lower().find('fq.gz') >= 0 ) :
                    urls = fstring[1].split(';')
                elif len(fstring) > 2 and len(fstring[2]) and ( fstring[2].lower().find('fastq.gz') >= 0 or  fstring[2].lower().find('fq.gz') >= 0 ) :
                    urls = fstring[2].split(';')
                else :
                    urls = []
                urls = [f.replace('ftp.sra.ebi.ac.uk', 'ftp://ftp.sra.ebi.ac.uk') for f in urls]
                for url in urls :
                    if len(url) > 2 :
                        fname = url.rsplit('/')[-1]
                        download_file(url, os.path.join(route, fname))
            except Exception as e:
                traceback.print_exc()
                continue
            files = glob( os.path.join( route, '{acc}*.fastq.*'.format(acc = run_accession) ) )
            if len(files) == 0 : continue
            return sorted(files, key=lambda x:(-len(x), x))
    return []



if __name__ == '__main__' :
    main()
