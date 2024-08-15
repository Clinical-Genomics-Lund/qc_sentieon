#!/data/bnf/sw/miniconda3/bin/python
from pprint import pprint
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="A script storing different qc outputs from sentieon driver algorithms into a json-blob for CDM")

    parser.add_argument("-s", "--SID",            help="Sample ID, required")
    parser.add_argument("-a", "--assay_metrics",  help="path to WgsMetricsAlgo or HsMetricAlgo algo output file")
    parser.add_argument("-l", "--aln_metrics",    help="path to AlignmentStat algo output file")
    parser.add_argument("-i", "--is_metrics",     help="path to InsertSizeMetricAlgo algo output file")
    parser.add_argument("-d", "--dedup_metrics",  help="path to AlignMetrics")
    parser.add_argument("-g", "--gc_summary",     help="path to GCBias --summary algo output file")
    parser.add_argument("-c", "--cov_summary",    help="path to CoverageMetrics --summary algo output file")
    parser.add_argument("-m", "--mq_metrics",     help="path to MeanQualityByCycle algo output file")
    parser.add_argument("-q", "--qd_metrics",     help="path to QualDistribution algo output file")

    args = parser.parse_args()

    qc_array = []
    if not args.SID:
        exit("You need to supply a sample-id")
    # Load Picard-like output wgs-metrics / hs-metrics aln_metrics is_metrics dedup_metrics.txt gc_summary.txt 
    if args.assay_metrics:
        qc_array.append(read_picard_like_files(args.assay_metrics,"assay"))
    if args.aln_metrics:
        qc_array.append(read_picard_like_files(args.aln_metrics,"alignment"))
    if args.is_metrics:
         qc_array.append(read_picard_like_files(args.is_metrics,"insert"))
    if args.dedup_metrics:
         qc_array.append(read_picard_like_files(args.dedup_metrics,"dedup"))
    if args.gc_summary:
        qc_array.append(read_picard_like_files(args.gc_summary,"gc"))
    # Load other data structures
    #cov_metrics (--histogram_high 2000 or even higher for panel-data to allow for IQR / MEDIAN )
    if args.cov_summary:
        qc_array.append(coverage_calc(args.cov_summary,"coverage"))
    if args.mq_metrics:
        qc_array.append(read_vertical_picard(args.mq_metrics,"qualbycycle"))
    if args.qd_metrics:
        qc_array.append(read_vertical_picard(args.qd_metrics,"qualdist"))
    with open(f"{args.SID}.json", 'w') as json_file:
        json.dump(qc_array, json_file, indent=4)

def read_picard_like_files(filename,category):
    """
    This function reads tabulated header/values outputs from picard
    and creates key=value dicts instead
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        # Iterate through the lines to find the one starting with '#'
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # The next line after the one starting with '#' contains the header
                headers_line = lines[i + 1].strip().split('\t')
                break
        data_line = lines[i + 2].strip().split('\t')
    picard_dict = dict(zip(headers_line, data_line))
    algo_dict = {
        "software" : category,
        "version" : "null",
        "result": picard_dict
    }
    return algo_dict

def coverage_calc(filename,category):
    """
    Accepts CoverageMetrics summary from sentieon.
    Return coverage-thresholds at set values and coverage uniformity (IQR/MEDIAN) calcs
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        headers_line = lines[0].strip().split('\t')
        sample_line = lines[1].strip().split('\t')
    cov_dict = dict(zip(headers_line, sample_line))
    # coverage uniformity
    # interquartile range of coverage, if Q1 and Q3 are valid integers
    if isinstance( cov_dict["granular_Q1"], int) and isinstance(cov_dict['granular_Q3'], int):
        iqr = (int(cov_dict['granular_Q3']) - int(cov_dict['granular_Q1']))
        cov_dict['coverage_uniformity'] = iqr / int(cov_dict['granular_median'])
    else:
        cov_dict['coverage_uniformity'] = "null"
    algo_dict = {
        "software" : category,
        "version" : "null",
        "result": cov_dict
    }
    return algo_dict

def read_vertical_picard(filename,category):
    """
    Read rowbased data from picard and store as dict per column
    Histogram-data for plotting?
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('#'):
                header_line = lines[i+1].strip().split('\t')
                break
        list_dict = {header: [] for header in header_line}
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue
            values = line.split()
            # Map each value to its corresponding header
            for i, header in enumerate(header_line):
                # Append the value to the appropriate list in the dictionary
                # Automatically convert to int or float if possible, otherwise keep as string
                try:
                    list_dict[header].append(int(values[i]))
                except ValueError:
                    try:
                        list_dict[header].append(float(values[i]))
                    except ValueError:
                        list_dict[header].append(values[i])
    algo_dict = {
        "software" : category,
        "version" : "null",
        "result": list_dict
    }
    return algo_dict              

if __name__ == "__main__":
    main()