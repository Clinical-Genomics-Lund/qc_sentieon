#!/usr/bin/env python3
from collections import defaultdict
import sys
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="A script storing different qc outputs from sentieon driver algorithms into a json-blob for CDM")

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
    json.dump(qc_array, sys.stdout, indent=4)

def read_picard_like_files(filename,category):
    """
    This function reads tabulated header/values outputs from picard
    and creates key=value dicts instead
    """
    with open(filename, 'r') as file:
        for line in file:         
            line = line.strip()        
            if line.startswith('#'):
                # The next line after the one starting with '#' contains the header
                headers_line = next(file).strip().split('\t')
                continue

            if headers_line:
                data_line = line.strip().split("\t")
                break

            if headers_line is None or data_line is None:
                raise ValueError("File does not contain expected headers and data lines.")
            
    picard_dict = dict(zip(headers_line, data_line))
    algo_dict = {
        "software" : category,
        "version" : None,
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
    try:
       q1 = int(cov_dict['granular_Q1'])
       q3 = int(cov_dict['granular_Q3'])
       median = int(cov_dict['granular_median'])
    except (ValueError, KeyError):
        q1, q3, median = None, None, None
        
    if q1 is not None and q3 is not None and median not in (None, 0):
        iqr = q3 - q1
        cov_dict['coverage_uniformity'] = iqr / median
    else:
        cov_dict['coverage_uniformity'] = None
        
       
    algo_dict = {
        "software" : category,
        "version" : None,
        "result": cov_dict
    }
    return algo_dict

def read_vertical_picard(filename, category):
    """
    Read rowbased data from picard and store as dict per column
    Histogram-data for plotting?
    """
    
    data = defaultdict(list)
    
    with open(filename, 'r') as file:
        for line in file:    
            if not line.startswith('#'):
                header_line = line.strip().split()
                break
        for line in file:
            line = line.strip()
            if not line:
                continue
                
            values = line.split()
            
            # Map each value to its corresponding header
            for i, var_name in enumerate(header_line):
            
                # Append the value to the appropriate list in the dictionary
                # Automatically convert to int or float if possible, otherwise keep as string
                
                value = values[i]
            
                for conversion in (int, float):
                    try:
                        value = conversion(value)
                        break
                    except ValueError:
                        continue
                
                data[var_name].append(value)
                
    algo_dict = {
        "software" : category,
        "version" : None,
        "result": data
    }
    return algo_dict                      

if __name__ == "__main__":
    main()